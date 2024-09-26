from typing import List
from haystack import component
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hierarchy_helpers import (
    get_sub_hierarchy_from_path,
    extract_chunks_from_hierarchy,
    create_context_text_from_hierarchy,
)

from models.hierarchy_path import HierarchyPathData


@component
class WikiContextCreator:
    def __init__(self, document_store):
        self.document_store = document_store
        
    def extract_path_list(self, hierarchy_paths: List[str]) -> List[List[str]]:
        path_list = []
        if len(hierarchy_paths) > 0:
            # Parse the JSON string into a dictionary
            data = json.loads(hierarchy_paths[0])
            
            # Validate and parse the data using Pydantic models
            hierarchy_path_data = HierarchyPathData(**data)
            
            # Extract the path values
            for path_obj in hierarchy_path_data.paths:
                path_list.append(path_obj.path)
        
        return path_list

    @component.output_types(context_list=List[str])
    def run(self, hierarchy_paths: List[str], chunks_hierarchy: dict):
        context_list = []
        
        path_list = self.extract_path_list(hierarchy_paths)
        for path in path_list:
            page_title = path[0]
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
