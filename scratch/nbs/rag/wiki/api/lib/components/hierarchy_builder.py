from typing import List
from haystack import Document
from haystack import component
from wiki_hierarchy import WikiHierarchy


@component
class HierarchyBuilder:
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

        wiki_hierarchy = WikiHierarchy("bolt://localhost:7687", "neo4j", "neo4jpass")
        for doc in unique_title_docs:
            title, sh, ch = wiki_hierarchy.get_hierarchy(doc.id)
            sec_hier[title] = sh
            chunk_hier[title] = ch
        wiki_hierarchy.close()

        return sec_hier, chunk_hier
