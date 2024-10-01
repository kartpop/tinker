sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack_integrations.document_stores.weaviate.document_store import (
    WeaviateDocumentStore,
)
from haystack_integrations.components.retrievers.weaviate.embedding_retriever import (
    WeaviateEmbeddingRetriever,
)
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchBM25Retriever,
)
from haystack.components.joiners.document_joiner import DocumentJoiner
import sys
import os
from haystack import Pipeline
from lib.templates import p1_qa_template


document_embedder = OpenAIDocumentEmbedder(model="text-embedding-3-small")
text_embedder = OpenAITextEmbedder(model="text-embedding-3-small")
weaviate_store = WeaviateDocumentStore(url="http://localhost:8088")
elasticsearch_store = ElasticsearchDocumentStore(hosts="http://localhost:9200")
weaviate_retriever = WeaviateEmbeddingRetriever(document_store=weaviate_store, top_k=3)
elasticsearch_retriever = ElasticsearchBM25Retriever(
    document_store=elasticsearch_store, top_k=3
)
reciprocal_rank_fusion_joiner = DocumentJoiner(join_mode="reciprocal_rank_fusion")
p1_qa_prompt_builder = PromptBuilder(template=p1_qa_template)
p1_qa_generator = OpenAIGenerator(model="gpt-4o-mini")


hybrid_pipeline = Pipeline()

hybrid_pipeline.add_component("text_embedder", text_embedder)
hybrid_pipeline.add_component("weaviate_retriever", weaviate_retriever)
hybrid_pipeline.add_component("elasticsearch_retriever", elasticsearch_retriever)
hybrid_pipeline.add_component(
    "reciprocal_rank_fusion_joiner", reciprocal_rank_fusion_joiner
)
hybrid_pipeline.add_component("p1_qa_prompt_builder", p1_qa_prompt_builder)
hybrid_pipeline.add_component("p1_qa_generator", p1_qa_generator)

hybrid_pipeline.connect("text_embedder.embedding", "weaviate_retriever.query_embedding")
hybrid_pipeline.connect("weaviate_retriever", "reciprocal_rank_fusion_joiner")
hybrid_pipeline.connect("elasticsearch_retriever", "reciprocal_rank_fusion_joiner")
hybrid_pipeline.connect(
    "reciprocal_rank_fusion_joiner.documents", "p1_qa_prompt_builder.documents"
)
hybrid_pipeline.connect("p1_qa_prompt_builder", "p1_qa_generator")
