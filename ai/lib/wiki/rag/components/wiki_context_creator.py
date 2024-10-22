import logging
from typing import List
from haystack import component
import json
from lib.wiki.rag.helpers.hierarchy_helpers import (
    extract_chunks_from_hierarchy,
    create_context_text_from_hierarchy,
    get_subhierarchy_and_metadata_from_path,
)

from lib.wiki.rag.helpers.log_helpers import (
    custom_serializer,
    strip_embeddings_from_dict,
)
from lib.wiki.rag.models.hierarchy_path import HierarchyPathData
from haystack import Document


@component
class WikiContextCreator:
    def __init__(self, document_store, logger: logging.Logger):
        self.document_store = document_store
        self.logger = logger

    def extract_path_list(self, hierarchy_paths: List[str]) -> List[List[str]]:
        """
        Extracts the path list from the hierarchy_paths list (strip off LLM reasoning)
        """
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

    @component.output_types(documents=List[Document])
    def run(self, hierarchy_paths: List[str], chunks_hierarchy: dict):
        try:
            context_list = []

            path_list = self.extract_path_list(hierarchy_paths)
            for path in path_list:
                page_title = path[0]
                if page_title not in chunks_hierarchy:
                    self.logger.warning(
                        f"WikiContextCreator: Page title '{page_title}' not found in chunks_hierarchy. Page may not exist; likely LLM hallucination while predicting probable wiki hierarchy_paths which may contain the anwer."
                    )
                    continue
                page_chunk_hierarchy = chunks_hierarchy.get(page_title, {})
                try:
                    page_sub_hierarchy, page_sub_hierarchy_metadata = (
                        get_subhierarchy_and_metadata_from_path(
                            page_chunk_hierarchy, path
                        )
                    )
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
                    page_sub_hierarchy_chunk_docs = (
                        self.document_store.filter_documents(
                            filters=document_store_filters
                        )
                    )

                    page_sub_hierarchy_text = create_context_text_from_hierarchy(
                        page_sub_hierarchy, page_sub_hierarchy_chunk_docs
                    )

                    context_list.append(
                        Document(
                            content=page_sub_hierarchy_text,
                            meta=page_sub_hierarchy_metadata,
                        )
                    )
                except Exception as e:
                    self.logger.warning(
                        f"WikiContextCreator: Failed to create context for path {path}: {e}. If path is not found in hierarchy, it may be due to hallucination by LLM."
                    )
                    continue

            return {"documents": context_list}
        except Exception as e:
            self.logger.error(
                f"\nError while creating the wiki context in WikiContextCreator, find error details below."
            )
            strip_embeddings_from_dict(chunks_hierarchy)
            self.logger.info(
                f"\nHierarchy paths received by the WikiContextCreator: {json.dumps(hierarchy_paths, default=custom_serializer, indent=4)}"
            )
            self.logger.info(
                f"\nChunks hierarchy received by the WikiContextCreator: {json.dumps(chunks_hierarchy, default=custom_serializer, indent=4)}"
            )
            raise
