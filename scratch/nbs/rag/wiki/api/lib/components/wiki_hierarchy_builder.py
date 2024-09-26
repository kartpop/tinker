from typing import List
from haystack import Document
from haystack import component
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from wiki_hierarchy import WikiHierarchy


@component
class WikiHierarchyBuilder:
    def __init__(self, neo4j_uri: str, neo4j_username: str, neo4j_password: str):
        self.neo4j_uri = neo4j_uri
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password

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
        unique_title_docs = self.filter_unique_titles(documents)

        sec_hier, chunk_hier = dict(), dict()

        wiki_hierarchy_driver = WikiHierarchy(
            self.neo4j_uri, self.neo4j_username, self.neo4j_password
        )
        for doc in unique_title_docs:
            title, sh, ch = wiki_hierarchy_driver.get_hierarchy(doc.id)
            sec_hier[title] = sh
            chunk_hier[title] = ch
        wiki_hierarchy_driver.close()

        return {"sections_hierarchy": sec_hier, "chunks_hierarchy": chunk_hier}
