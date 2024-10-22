import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import json
from config import config
import logging
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack_integrations.document_stores.weaviate.document_store import (
    WeaviateDocumentStore,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from haystack_integrations.components.retrievers.weaviate.embedding_retriever import (
    WeaviateEmbeddingRetriever,
)
from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchBM25Retriever,
)
from haystack.components.joiners.document_joiner import DocumentJoiner
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from pydantic import BaseModel
from lib.wiki.rag.components.wiki_context_creator import WikiContextCreator
from lib.wiki.rag.components.wiki_hierarchy_builder import WikiHierarchyBuilder
from lib.wiki.rag.helpers.log_helpers import (
    log_dict_as_json,
    strip_embeddings_from_dict,
)
from lib.wiki.rag.pipelines.graph_pipeline import GraphPipeline
from lib.wiki.rag.pipelines.hybrid_pipeline import HybridPipeline
from lib.wiki.rag.templates.phase_1_qa import phase_1_qa_template
from lib.wiki.rag.templates.phase_2_hierarchy import phase_2_hierarchy_template
from lib.wiki.rag.templates.phase_2_qa import phase_2_qa_template
from wikirag.rag.question_answer_async import QuestionAnswerAsync
from fastapi import FastAPI, HTTPException
import aiofiles


class Question(BaseModel):
    question: str


class HybridPipelineDatabaseResources:
    def __init__(
        self,
        weaviate_store: WeaviateDocumentStore,
        elasticsearch_store: ElasticsearchDocumentStore,
    ):
        self.weaviate_store = weaviate_store
        self.elasticsearch_store = elasticsearch_store
        
    def test_connectivity(self):
        # Test Weaviate connectivity
        try:
            self.weaviate_store.client.collections.list_all(simple=True)
            logger.info("HybridPipelineDatabaseResources: Successfully connected to Weaviate.")
        except Exception as e:
            logger.error(f"HybridPipelineDatabaseResources: Failed to connect to Weaviate: {e}")
            raise
        
        # Test Elasticsearch connectivity
        try:
            self.elasticsearch_store.client.info()
            logger.info("HybridPipelineDatabaseResources: Successfully connected to Elasticsearch.")
        except Exception as e:
            logger.error(f"HybridPipelineDatabaseResources: Failed to connect to Elasticsearch: {e}")
            raise

    def close(self):
        self.weaviate_store.client.close()
        self.elasticsearch_store.client.close()


class GraphPipelineDatabaseResources:
    def __init__(
        self,
        elasticsearch_store: ElasticsearchDocumentStore,
        graph_driver: GraphDatabase.driver,
    ):
        self.elasticsearch_store = elasticsearch_store
        self.graph_driver = graph_driver
        
    def test_connectivity(self):
        # Test Elasticsearch connectivity
        try:
            self.elasticsearch_store.client.info()
            logger.info("GraphPipelineDatabaseResources: Successfully connected to Elasticsearch.")
        except Exception as e:
            logger.error(f"GraphPipelineDatabaseResources: Failed to connect to Elasticsearch: {e}")
            raise
        
        # Test Neo4j connectivity
        try:
            with self.graph_driver.session() as session:
                session.run("MATCH (n) RETURN COUNT(n) AS count").single()["count"]
            logger.info("GraphPipelineDatabaseResources: Successfully connected to Neo4j.")
        except Exception as e:
            logger.error(f"GraphPipelineDatabaseResources: Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        self.elasticsearch_store.client.close()
        self.graph_driver.close()


def initialize_hybrid_pipeline():
    # Load configurations from .env and config.yml
    # Haystack components cannot be reused across pipelines. Each pipeline should have its own set of components.
    WEAVIATE_HOST = os.getenv("WEAVIATE_HOST")
    WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT"))
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
    ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT"))
    EMBEDDING_MODEL = config.get("openai.embedding_model", "text-embedding-3-small")
    LLM_MODEL = config.get("openai.llm_model", "gpt-4o-mini")
    TOP_K_EMBEDDING_RETRIEVER = config.get("rag.top_k.embedding_retriever", 3)
    TOP_K_BM25_RETRIEVER = config.get("rag.top_k.bm25_retriever", 3)
    HYBRID_JOIN_MODE = config.get("rag.hybrid_join_mode", "reciprocal_rank_fusion")

    # Log all config and environment variables
    logger.debug("\nHybrid Pipeline - Configuration and Environment Variables:")
    logger.debug(f"WEAVIATE_HOST: {WEAVIATE_HOST}")
    logger.debug(f"WEAVIATE_PORT: {WEAVIATE_PORT}")
    logger.debug(f"ELASTICSEARCH_HOST: {ELASTICSEARCH_HOST}")
    logger.debug(f"ELASTICSEARCH_PORT: {ELASTICSEARCH_PORT}")
    logger.debug(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
    logger.debug(f"LLM_MODEL: {LLM_MODEL}")
    logger.debug(f"TOP_K_EMBEDDING_RETRIEVER: {TOP_K_EMBEDDING_RETRIEVER}")
    logger.debug(f"TOP_K_BM25_RETRIEVER: {TOP_K_BM25_RETRIEVER}")
    logger.debug(f"HYBRID_JOIN_MODE: {HYBRID_JOIN_MODE}")

    document_embedder = OpenAIDocumentEmbedder(model=EMBEDDING_MODEL)
    text_embedder = OpenAITextEmbedder(model=EMBEDDING_MODEL)
    weaviate_store = WeaviateDocumentStore(
        url=f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}"
    )
    elasticsearch_store = ElasticsearchDocumentStore(
        hosts=[f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"]
    )
    weaviate_retriever = WeaviateEmbeddingRetriever(
        document_store=weaviate_store, top_k=TOP_K_EMBEDDING_RETRIEVER
    )
    elasticsearch_retriever = ElasticsearchBM25Retriever(
        document_store=elasticsearch_store, top_k=TOP_K_BM25_RETRIEVER
    )
    reciprocal_rank_fusion_joiner = DocumentJoiner(join_mode=HYBRID_JOIN_MODE)
    phase_1_qa_prompt_builder = PromptBuilder(template=phase_1_qa_template)
    phase_1_qa_generator = OpenAIGenerator(model=LLM_MODEL)

    resources = HybridPipelineDatabaseResources(weaviate_store, elasticsearch_store)

    return (
        HybridPipeline(
            document_embedder,
            text_embedder,
            weaviate_retriever,
            elasticsearch_retriever,
            reciprocal_rank_fusion_joiner,
            phase_1_qa_prompt_builder,
            phase_1_qa_generator,
        ),
        resources,
    )


def initialize_graph_pipeline():
    # Load configurations from .env and config.yml
    # Haystack components cannot be reused across pipelines. Each pipeline should have its own set of components.
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
    ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT"))
    LLM_MODEL = config.get("openai.llm_model", "gpt-4o-mini")
    NEO4J_HOST = os.getenv("NEO4J_HOST")
    NEO4J_PORT = int(os.getenv("NEO4J_PORT"))
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    logger.debug("\nGraph Pipeline - Configuration and Environment Variables:")
    logger.debug(f"ELASTICSEARCH_HOST: {ELASTICSEARCH_HOST}")
    logger.debug(f"ELASTICSEARCH_PORT: {ELASTICSEARCH_PORT}")
    logger.debug(f"LLM_MODEL: {LLM_MODEL}")
    logger.debug(f"NEO4J_HOST: {NEO4J_HOST}")
    logger.debug(f"NEO4J_PORT: {NEO4J_PORT}")
    logger.debug(f"NEO4J_USER: {NEO4J_USER}")

    graph_driver = GraphDatabase.driver(
        f"bolt://{NEO4J_HOST}:{NEO4J_PORT}", auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    elasticsearch_store = ElasticsearchDocumentStore(
        hosts=[f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"]
    )
    wiki_hierarchy_builder = WikiHierarchyBuilder(
        graphDatabaseDriver=graph_driver, logger=logger
    )
    hierarchy_prompt_builder = PromptBuilder(template=phase_2_hierarchy_template)
    hierarchy_generator = OpenAIGenerator(model=LLM_MODEL)
    wiki_context_creator = WikiContextCreator(
        document_store=elasticsearch_store, logger=logger
    )
    phase_2_qa_prompt_builder = PromptBuilder(template=phase_2_qa_template)
    phase_2_qa_generator = OpenAIGenerator(model=LLM_MODEL)

    resources = GraphPipelineDatabaseResources(elasticsearch_store, graph_driver)

    return (
        GraphPipeline(
            wiki_hierarchy_builder,
            hierarchy_prompt_builder,
            hierarchy_generator,
            elasticsearch_store,
            wiki_context_creator,
            phase_2_qa_prompt_builder,
            phase_2_qa_generator,
        ),
        resources,
    )


def setup_logging():
    global logger

    # Ensure log directories exist
    log_filepath = config.get("rag.log_filepath", "/aux/data/wiki/v3000/logs/rag/")
    if not os.path.exists(log_filepath):
        os.makedirs(log_filepath, exist_ok=True)
    qa_logs_filepath = config.get(
        "rag.qa_logs_filepath", "/aux/data/wiki/v3000/logs/rag/qa/"
    )
    if not os.path.exists(qa_logs_filepath):
        os.makedirs(qa_logs_filepath, exist_ok=True)

    log_level = config.get("logging.level", "INFO")
    log_format = config.get(
        "logging.format", "%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger(__name__)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_filename = f"{log_filepath}{timestamp}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)


load_dotenv()
setup_logging()

# Test content tracing
from haystack import tracing

tracing.tracer.is_content_tracing_enabled = True
# --------------------------------------------

hybrid_pipeline, hybrid_pipeline_resources = initialize_hybrid_pipeline()
hybrid_pipeline_resources.test_connectivity()

graph_pipeline, graph_pipeline_resources = initialize_graph_pipeline()
graph_pipeline_resources.test_connectivity()

qna = QuestionAnswerAsync(
    hybrid_pipeline=hybrid_pipeline,
    graph_pipeline=graph_pipeline,
    logger=logger,
)

logger.info("QuestionAnswer RAG pipeline initialized and ready for use.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Nothing to do on startup

    yield

    logger.info("Shutting down and closing resources.")
    hybrid_pipeline_resources.close()
    graph_pipeline_resources.close()


app = FastAPI(lifespan=lifespan)


async def log_qna(question, ask_response):
    qa_logs_filepath = config.get(
        "rag.qa_logs_filepath", "/aux/data/wiki/v3000/logs/rag/qa/"
    )
    log_filename = f"{qa_logs_filepath}{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    qa_json = {
        "question": question,
        "answer": ask_response["answer"],
        "metadata": ask_response["metadata"],
    }
    await log_dict_as_json(log_filename, qa_json)


@app.post("/ask")
async def ask(q: Question):
    try:
        question = q.question

        ask_response = await qna.ask(question)

        response = {"question": question, "answer": ask_response["answer"]}

        # Log the question-answer asynchonously
        asyncio.create_task(log_qna(question, ask_response))

        return response
    except Exception as e:
        logger.exception(
            f"An error occurred during the processing of the question '{q.question}': {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="An internal server error occurred."
        )
