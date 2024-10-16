import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple
from haystack import Document
import redis
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack_integrations.document_stores.weaviate.document_store import (
    WeaviateDocumentStore,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from lib.wiki.index.chunk.helpers import get_documents_and_page_hierarchy
from lib.wiki.index.download.helpers import get_title_pathname_map
from lib.wiki.index.graph.page_graph_creator import Neo4jPageGraphCreator
from lib.wiki.index.graph.category_graph_creator import Neo4jCategoryGraphCreator


class Indexer:
    def __init__(
        self,
        logger: logging.Logger,
        redis_client: redis.Redis,
        openai_doc_embedder: OpenAIDocumentEmbedder,
        w_store: WeaviateDocumentStore,
        e_store: ElasticsearchDocumentStore,
        page_graph_creator: Neo4jPageGraphCreator,
        category_graph_creator: Neo4jCategoryGraphCreator,
    ):
        self.logger = logger
        self.redis = redis_client
        self.embedder = openai_doc_embedder
        self.w_store = w_store
        self.e_store = e_store
        self.w_writer = DocumentWriter(
            document_store=self.w_store, policy=DuplicatePolicy.SKIP
        )
        self.e_writer = DocumentWriter(
            document_store=self.e_store, policy=DuplicatePolicy.SKIP
        )
        self.page_graph_creator = page_graph_creator
        self.category_graph_creator = category_graph_creator

    def store_documents_elasticsearch(self, documents: List[Document]) -> None:
        """
        Store documents in ElasticsearchDocumentStore.
        """
        self.e_writer.run(documents=documents)

    def get_embedded_documents(
        self, documents: List[Document], filepath: str, page_filename: str
    ) -> List[Document]:
        """
        Get embedded documents from ./metadta/index/embeddings. Create embeddings using the OpenAIDocumentEmbedder and store
        the embedded documents in the same directory if they do not already exist.
        """
        page_filename_wo_ext = os.path.splitext(page_filename)[0]
        embeddings_filepath = os.path.join(
            filepath, ".metadata/index/embeddings", f"{page_filename_wo_ext}.json"
        )

        if os.path.exists(embeddings_filepath):
            with open(embeddings_filepath, "r") as file:
                data = json.load(file)
            return [Document.from_dict(doc) for doc in data["documents"]]

        metadata_emdeddings_path = os.path.join(filepath, ".metadata/index/embeddings")
        if not os.path.exists(metadata_emdeddings_path):
            os.makedirs(metadata_emdeddings_path)

        # Create embeddings and store embedded documents
        embedded_documents = self.embedder.run(documents=documents)
        if "documents" not in embedded_documents:
            raise KeyError(
                "The 'documents' key is missing in the embedded_documents returned from embedder."
            )
        embedded_docs_file_to_save = {
            "documents": [
                doc.to_dict() for doc in embedded_documents["documents"]
            ],  # convert Haystack Document object to dict
            "meta": embedded_documents["meta"] if "meta" in embedded_documents else {},
        }
        with open(embeddings_filepath, "w") as file:
            json.dump(embedded_docs_file_to_save, file)

        return embedded_documents["documents"]

    def store_documents_weaviate(self, documents: List[Document]) -> None:
        """
        store documents in WeaviateDocumentStore.
        """
        self.w_writer.run(documents=documents)

    def index_wiki_pages(
        self, category: str, filepath: str, category_pages_indexed: Dict[str, int]
    ) -> int:
        """
        Indexes already chunked wiki data for all pages in a category and its subcategories. Chunked data is available in
        the .metadata/chunk directory. The intermediate embeddings are stored in the .metadata/index/embeddings directory.

        List of Haystack Document objects is created from stored chunks and stored into three databases:
        - ElasticsearchDocumentStore: for full-text search (list of Document objects without embeddings is stored)
        - WeaviateDocumentStore: for vector search (list of Document objects enriched with embeddings is stored)
        - Neo4j: for graph search (list of Document objects are stored as Chunk type nodes and Section, Page, Category type nodes
        are created to represent the structure of the data)
        """
        title_pathname = get_title_pathname_map(category, filepath)

        pages_filename_set = {file.name for file in Path(filepath).glob("*.html")}
        categories_dirname_set = {
            dir.name
            for dir in Path(filepath).iterdir()
            if dir.is_dir() and dir.name != ".metadata"
        }

        num_total_pages_indexed = 0

        pages = title_pathname["pages"]
        for page_title, page_filename in pages.items():
            if self.redis.sismember("indexed_pages", page_title):
                continue
            if page_filename not in pages_filename_set:
                continue
            documents, hierarchy = get_documents_and_page_hierarchy(
                filepath, page_title, page_filename
            )
            self.store_documents_elasticsearch(documents)
            embedded_documents = self.get_embedded_documents(
                documents, filepath, page_filename
            )
            self.store_documents_weaviate(embedded_documents)
            self.page_graph_creator.create_graph(hierarchy)
            self.redis.sadd("indexed_pages", page_title)
            num_total_pages_indexed += 1

        if num_total_pages_indexed > 0:
            category_pages_indexed[category] = num_total_pages_indexed

        subcategories = title_pathname["categories"]
        for subcategory_title, subcategory_path in subcategories.items():
            if self.redis.sismember("indexed_categories", subcategory_title):
                continue
            if subcategory_path not in categories_dirname_set:
                continue
            subcategory_path = os.path.join(filepath, subcategory_path)
            num_total_pages_indexed += self.index_wiki_pages(
                subcategory_title, subcategory_path, category_pages_indexed
            )
            self.redis.sadd("indexed_categories", subcategory_title)

        return num_total_pages_indexed

    def build_category_graph(self, category: str, filepath: str) -> int:
        """
        Creates a graph representation of the category and connections to its subcategories and pages. The graph is created
        on top of the individual page hierarchy graphs already existing in Neo4j.
        """
        title_pathname = get_title_pathname_map(category, filepath)

        pages = title_pathname["pages"]
        for page_title in pages:
            if not self.redis.sismember("indexed_pages", page_title):
                continue
            self.category_graph_creator.create_category_to_page_relationship(
                category, page_title
            )

        subcategories = title_pathname["categories"]
        for subcategory_title, subcategory_path in subcategories.items():
            if not self.redis.sismember("indexed_categories", subcategory_title):
                continue
            self.category_graph_creator.create_category_to_subcategory_relationship(
                category, subcategory_title
            )
            subcategory_path = os.path.join(filepath, subcategory_path)
            self.build_category_graph(
                subcategory_title, subcategory_path
            )

    def index_wiki_data(
        self, category: str, filepath: str, category_pages_indexed: Dict[str, int]
    ) -> int:
        """
        Indexes the wiki data for a category and its subcategories. The data is indexed in ElasticsearchDocumentStore,
        WeaviateDocumentStore, and Neo4j. The graph representation of the category and its subcategories is created in Neo4j.
        """
        try:
            num_total_pages_indexed = self.index_wiki_pages(
                category, filepath, category_pages_indexed
            )
            self.build_category_graph(category, filepath)

            return num_total_pages_indexed

        except Exception as e:
            self.logger.error(
                f"Error indexing data for category {category}: {e}",
                exc_info=True,
            )
            return -1
