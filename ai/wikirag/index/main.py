import os
import logging
from config import config
import redis
from dotenv import load_dotenv
from downloader import Downloader, DownloaderException
from chunker import Chunker, ChunkerException
from indexer import Indexer, IndexerException
from datetime import datetime
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack_integrations.document_stores.weaviate.document_store import (
    WeaviateDocumentStore,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from neo4j import GraphDatabase
from lib.wiki.index.graph.page_graph_creator import Neo4jPageGraphCreator
from lib.wiki.index.graph.category_graph_creator import Neo4jCategoryGraphCreator


class Resources:
    def __init__(
        self,
        redis_client: redis.Redis,
        w_store: WeaviateDocumentStore,
        e_store: ElasticsearchDocumentStore,
        graph_creator_driver: GraphDatabase.driver,
    ):
        self.redis_client = redis_client
        self.w_store = w_store
        self.e_store = e_store
        self.graph_creator_driver = graph_creator_driver

    def close(self):
        self.redis_client.close()
        self.w_store.client.close()
        self.e_store.client.close()
        self.graph_creator_driver.close()


def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_level = config.get("level", "INFO")
    log_format = config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger(__name__)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filepath = config.get("index.log_filepath", "/aux/data/wiki/v100/logs/index/")
    log_filename = f"{log_filepath}{timestamp}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    return logger


def initialize_resources():
    load_dotenv()

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))
    REDIS_DB = int(os.getenv("REDIS_DB"))
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    NEO4J_HOST = os.getenv("NEO4J_HOST")
    NEO4J_PORT = int(os.getenv("NEO4J_PORT"))
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    graph_creator_driver = GraphDatabase.driver(
        f"bolt://{NEO4J_HOST}:{NEO4J_PORT}", auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    WEAVIATE_HOST = os.getenv("WEAVIATE_HOST")
    WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT"))
    w_store = WeaviateDocumentStore(url=f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}")

    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
    ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT"))
    e_store = ElasticsearchDocumentStore(
        hosts=[f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"]
    )

    return Resources(
        redis_client,
        w_store,
        e_store,
        graph_creator_driver,
    )


def run_indexing(logger, resources):
    category = config.get("index.category", "Dinosaurs")
    filepath = config.get("index.filepath", f"/aux/data/wiki/v100/Dinosaurs")

    # Download wiki data
    downloader = Downloader(logger, resources.redis_client)
    logger.info(f"Downloading category members for {category} ...")
    category_pages_downloaded = {}
    exclude_keywords = config.get(
        "index.exclude_keywords", ["bird", "list of", "lists of"]
    )
    max_depth = config.get("index.max_depth", 2)
    num_pages_downloaded = downloader.fetch_wiki_data(
        category, filepath, exclude_keywords, category_pages_downloaded, max_depth
    )
    logger.info(
        f"Successfully downloaded {num_pages_downloaded} total pages.\nDownloaded category pages: {category_pages_downloaded}"
    )

    # Chunk wiki data
    chunker = Chunker(logger, resources.redis_client)
    logger.info(f"Chunking category members for {category} ...")
    category_pages_chunked = {}
    num_pages_chunked = chunker.chunk_wiki_data(
        category, filepath, category_pages_chunked
    )
    logger.info(
        f"Successfully chunked {num_pages_chunked} total pages.\nChunked category pages: {category_pages_chunked}"
    )

    # Index wiki data
    logger.info(f"Indexing category members for {category} ...")
    embedding_model = config.get("embedding_model", "text-embedding-3-small")
    embedder = OpenAIDocumentEmbedder(model=embedding_model)
    page_graph_creator = Neo4jPageGraphCreator(resources.graph_creator_driver)
    category_graph_creator = Neo4jCategoryGraphCreator(resources.graph_creator_driver)
    indexer = Indexer(
        logger,
        resources.redis_client,
        embedder,
        resources.w_store,
        resources.e_store,
        page_graph_creator,
        category_graph_creator,
    )
    category_pages_indexed = {}
    num_pages_indexed = indexer.index_wiki_data(
        category, filepath, category_pages_indexed
    )
    logger.info(
        f"Successfully indexed {num_pages_indexed} total pages.\nIndexed category pages: {category_pages_indexed}"
    )


def main():
    logger = setup_logging()
    resources = initialize_resources()
    try:
        run_indexing(logger, resources)
    except DownloaderException as e:
        logger.exception(f"Downloader failed: {e}", exc_info=True)
    except ChunkerException as e:
        logger.exception(f"Chunker failed: {e}", exc_info=True)
    except IndexerException as e:
        logger.exception(f"Indexer failed: {e}", exc_info=True)
    except Exception as e:
        logger.exception(f"Unknown error occurred: {e}", exc_info=True)
    finally:
        logger.info("Closing resources.")
        resources.close()


if __name__ == "__main__":
    main()
