from typing import List
from haystack import component
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hierarchy_helpers import (
    get_sub_hierarchy_from_path,
    extract_chunks_from_hierarchy,
    create_context_text_from_hierarchy,
)


@component
class WikiContextCreator:
    def __init__(self, document_store):
        self.document_store = document_store

    @component.output_types(context_list=List[str])
    def run(self, hierarchy_paths: List[str], chunks_hierarchy: dict):

        context_list = []

        for path in hierarchy_paths:
            page_title = path.split(" -> ")[0]
            page_chunk_hierarchy = chunks_hierarchy.get(page_title, {})
            page_sub_hierarchy = get_sub_hierarchy_from_path(page_chunk_hierarchy, path)
            page_sub_hierarchy_chunk_ids = extract_chunks_from_hierarchy(
                page_sub_hierarchy
            )

            document_store_filters = {
                "operator": "OR",
                "conditions": [
                    {"field": "id", "operator": "==", "value": chunk_id}
                    for chunk_id in page_sub_hierarchy_chunk_ids
                ],
            }
            page_sub_hierarchy_chunk_docs = self.document_store.filter_documents(
                filters=document_store_filters
            )

            page_sub_hierarchy_text = create_context_text_from_hierarchy(
                page_sub_hierarchy, page_sub_hierarchy_chunk_docs
            )

            context_list.append(page_sub_hierarchy_text)

        return {"context_list": context_list}
