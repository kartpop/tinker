import json
import logging
from typing import List
from haystack import Document
from haystack import component
from lib.wiki.rag.helpers.log_helpers import (
    custom_serializer,
    strip_embeddings_from_dict,
)
from lib.wiki.rag.helpers.wiki_hierarchy import WikiHierarchy
from neo4j import GraphDatabase


@component
class WikiHierarchyBuilder:
    def __init__(
        self, graphDatabaseDriver: GraphDatabase.driver, logger: logging.Logger
    ):
        self.graphDatabaseDriver = graphDatabaseDriver
        self.logger = logger

    def filter_unique_titles(self, documents: List[Document]) -> List[Document]:
        seen_titles = set()
        unique_documents = []
        for doc in documents:
            title = doc.meta.get("title")
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_documents.append(doc)
        return unique_documents

    @component.output_types(sections_hierarchy=dict, chunks_hierarchy=dict)
    def run(self, documents: List[Document]):
        """
        Get the hierarchy of the sections and chunks for the given documents.

        Args:
            documents: List of documents for which the hierarchy is to be retrieved.

        Returns:
            Two dictionaries containing the hierarchy of the sections and chunks for the given documents.

        Refer to the WikiHierarchy class for more details on the hierarchy structure.
        """
        try:
            unique_title_docs = self.filter_unique_titles(documents)

            sec_hier, chunk_hier = dict(), dict()

            wiki_hierarchy_driver = WikiHierarchy(self.graphDatabaseDriver)
            for doc in unique_title_docs:
                title, sh, ch = wiki_hierarchy_driver.get_hierarchy(doc.id)
                sec_hier[title] = sh
                chunk_hier[title] = ch

            return {"sections_hierarchy": sec_hier, "chunks_hierarchy": chunk_hier}
        except Exception as e:
            self.logger.error(
                f"\nError while building the wiki hierarchy in WikiHierarchyBuilder, find error details below."
            )
            docs = {"documents": [doc.to_dict() for doc in documents]}
            strip_embeddings_from_dict(docs)
            self.logger.info(
                f"\nDocuments received by the WikiHierarchyBuilder: {json.dumps(docs, default=custom_serializer, indent=4)}"
            )
            raise
