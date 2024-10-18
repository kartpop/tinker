from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack_integrations.components.retrievers.weaviate.embedding_retriever import (
    WeaviateEmbeddingRetriever,
)
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchBM25Retriever,
)
from haystack.components.joiners.document_joiner import DocumentJoiner
from haystack import Pipeline


class PipelineSingleton:
    """
    In Haystack, each component instance can only be used in a single pipeline. This singleton class ensures that the
    component instances are only used in a single pipeline.
    """

    _instance = None

    @classmethod
    def get_instance(cls, build_func):
        if cls._instance is None:
            cls._instance = build_func()
        return cls._instance


class HybridPipeline:
    """
    A RAG pipeline for question answering.

    Phase-1: The pipeline retrieves documents via both semantic search and full-text search, ranks the retrieved
    documents and feeds those as contex to an LLM to generate a response.
    """

    def __init__(
        self,
        document_embedder: OpenAIDocumentEmbedder,
        text_embedder: OpenAITextEmbedder,
        weaviate_retriever: WeaviateEmbeddingRetriever,
        elasticsearch_retriever: ElasticsearchBM25Retriever,
        reciprocal_rank_fusion: DocumentJoiner,
        phase_1_qa_prompt_builder: PromptBuilder,
        phase_1_qa_generator: OpenAIGenerator,
    ):
        self.document_embedder = document_embedder
        self.text_embedder = text_embedder
        self.weaviate_retriever = weaviate_retriever
        self.elasticsearch_retriever = elasticsearch_retriever
        self.reciprocal_rank_fusion = reciprocal_rank_fusion
        self.phase_1_qa_prompt_builder = phase_1_qa_prompt_builder
        self.phase_1_qa_generator = phase_1_qa_generator

    def build(self) -> Pipeline:
        """
        Builds a haystack pipeline which does the following:
        1. Retrieves documents from Weaviate vector store and Elasticsearch full-text search.
        2. Ranks and joins the results using reciprocal rank fusion.
        3. Builds the prompt using the context documents and invokes an LLM to generate response.
        """
        def create_pipeline() -> Pipeline:
            pipeline = Pipeline()
            pipeline.add_component("text_embedder", self.text_embedder)
            pipeline.add_component("weaviate_retriever", self.weaviate_retriever)
            pipeline.add_component(
                "elasticsearch_retriever", self.elasticsearch_retriever
            )
            pipeline.add_component(
                "reciprocal_rank_fusion_joiner", self.reciprocal_rank_fusion
            )
            pipeline.add_component(
                "phase_1_qa_prompt_builder", self.phase_1_qa_prompt_builder
            )
            pipeline.add_component("phase_1_qa_generator", self.phase_1_qa_generator)

            pipeline.connect(
                "text_embedder.embedding", "weaviate_retriever.query_embedding"
            )
            pipeline.connect("weaviate_retriever", "reciprocal_rank_fusion_joiner")
            pipeline.connect("elasticsearch_retriever", "reciprocal_rank_fusion_joiner")
            pipeline.connect(
                "reciprocal_rank_fusion_joiner.documents",
                "phase_1_qa_prompt_builder.documents",
            )
            pipeline.connect("phase_1_qa_prompt_builder", "phase_1_qa_generator")

            return pipeline

        return PipelineSingleton.get_instance(create_pipeline)
