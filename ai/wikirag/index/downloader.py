import os
import logging
from typing import List
import redis

from lib.wiki.index.download.helpers import (
    get_title_pathname_map,
    download_page,
)


class Downloader:
    def __init__(self, logger: logging.Logger, redis_client: redis.Redis):
        self.logger = logger
        self.redis = redis_client

    def fetch_wiki_data(
        self,
        category: str,
        filepath: str,
        inverse_filter: list,
        category_pages_downloaded: dict,
        depth: int,
    ) -> int:
        """
        Fetches Wikipedia data recursively for a given category and saves it to the specified filepath.

        Args:
            category (str): The Wikipedia category to fetch data for.
            filepath (str): The directory path to save the data.
            inverse_filter (list): A list of words/phrases; category or pages containing any of these as substring will be excluded.
            category_pages_downloaded (dict): A dictionary to track the number of pages downloaded per category.
            depth (int): The current remaining depth for the recursive fetch.

        Returns:
            int: The total number of pages downloaded.
        """
        try:
            if depth < 1:
                return 0

            if not os.path.exists(filepath):
                os.makedirs(filepath)

            num_total_pages_downloaded = 0
            title_pathname = get_title_pathname_map(
                category, filepath, inverse_filter, create=True
            )

            pages = title_pathname["pages"]
            for page_title, page_filename in pages.items():
                if self.redis.sismember("downloaded_pages", page_title):
                    continue
                download_page(page_title, page_filename, filepath)
                num_total_pages_downloaded += 1
                self.redis.sadd("downloaded_pages", page_title)

            if num_total_pages_downloaded > 0:
                category_pages_downloaded[category] = num_total_pages_downloaded

            subcategories = title_pathname["categories"]
            for subcategory_title, subcategory_path in subcategories.items():
                if self.redis.sismember("downloaded_categories", subcategory_title):
                    continue
                subcategory_path = os.path.join(filepath, subcategory_path)
                subcategory_total_pages_downloaded = self.fetch_wiki_data(
                    subcategory_title,
                    subcategory_path,
                    inverse_filter,
                    category_pages_downloaded,
                    depth - 1,
                )
                num_total_pages_downloaded += subcategory_total_pages_downloaded
                self.redis.sadd("downloaded_categories", subcategory_title)

            return num_total_pages_downloaded

        except Exception as e:
            self.logger.error(
                f"Error downloading data for category {category}: {e}",
                exc_info=True,
            )
            return -1
