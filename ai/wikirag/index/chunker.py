import os
import json
import logging
from pathlib import Path
from typing import Dict
import redis
from haystack.components.converters import TextFileToDocument
from haystack import Pipeline
from lib.wiki.index.chunk.wiki_page_chunker import WikiPageChunker
from lib.wiki.index.download.helpers import get_title_pathname_map


class ChunkerException(Exception):
    pass


class Chunker:
    def __init__(self, logger: logging.Logger, redis_client: redis.Redis):
        self.logger = logger
        self.redis = redis_client

    def make_result_serializable(self, result: dict) -> None:
        """
        The result dictionary has objects of type 'Document' dataclass which is specific to Haystack. Those objects should be
        flattened to a dictionary so that result dict can be serialized to JSON.
        """
        documents = result["splitter"]["documents"]
        result["splitter"]["documents"] = [doc.to_dict() for doc in documents]

    def chunk_page(self, filepath: str, page_title: str, page_filename: str) -> None:
        """
        Chunk the page and store chunks in .metadata/chunks folder
        """
        page_filepath = os.path.join(filepath, page_filename)
        if not os.path.exists(page_filepath):
            raise FileNotFoundError(f"File {page_filepath} does not exist.")

        # Run chunk pipeline
        converter = TextFileToDocument()
        splitter = WikiPageChunker()

        chunk_pipeline = Pipeline()

        chunk_pipeline.add_component("converter", converter)
        chunk_pipeline.add_component("splitter", splitter)

        chunk_pipeline.connect("converter", "splitter")

        result = chunk_pipeline.run(
            data={
                "converter": {
                    "sources": [Path(page_filepath)],
                    "meta": {"page_title": page_title},
                }
            }
        )

        self.make_result_serializable(result)

        # Write chunk results to file
        metadata_chunk_path = os.path.join(filepath, ".metadata/chunk")
        if not os.path.exists(metadata_chunk_path):
            os.makedirs(metadata_chunk_path)
        page_chunk_filepath = os.path.join(
            metadata_chunk_path, f"{page_filename.replace('.html', '')}.json"
        )
        with open(page_chunk_filepath, "w") as file:
            json.dump(result, file)

    def chunk_wiki_data(
        self, category: str, filepath: str, category_pages_chunked: Dict[str, int]
    ) -> int:
        """
        Chunks wiki data for all pages in a category and its subcategories.

        Downloaded wiki data is accessed from the .metadata/download directory in the category filepath.
        Chunks and hierarchy information is stored in the .metadata/chunk directory.
        """
        try:
            num_total_pages_chunked = 0
            title_pathname = get_title_pathname_map(category, filepath, create=False)

            pages_filename_set = {file.name for file in Path(filepath).glob("*.html")}
            categories_dirname_set = {
                dir.name
                for dir in Path(filepath).iterdir()
                if dir.is_dir() and dir.name != ".metadata"
            }

            pages = title_pathname["pages"]
            for page_title, page_filename in pages.items():
                if self.redis.sismember("chunked_pages", page_title):
                    continue
                if page_filename not in pages_filename_set:
                    continue
                self.chunk_page(filepath, page_title, page_filename)
                num_total_pages_chunked += 1
                self.redis.sadd("chunked_pages", page_title)

            if num_total_pages_chunked > 0:
                category_pages_chunked[category] = num_total_pages_chunked

            subcategories = title_pathname["categories"]
            for subcategory_title, subcategory_path in subcategories.items():
                if self.redis.sismember("chunked_categories", subcategory_title):
                    continue
                if subcategory_path not in categories_dirname_set:
                    continue
                subcategory_path = os.path.join(filepath, subcategory_path)
                subcategory_total_pages_chunked = self.chunk_wiki_data(
                    subcategory_title, subcategory_path, category_pages_chunked
                )
                num_total_pages_chunked += subcategory_total_pages_chunked
                self.redis.sadd("chunked_categories", subcategory_title)

            return num_total_pages_chunked

        except Exception as e:
            raise ChunkerException(f"Error chunking data for category {category}: {e}")
