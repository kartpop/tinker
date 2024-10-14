import os
import logging
from lib.wiki.index.helpers import (
    get_title_pathname_map,
    download_page,
    WikiDownloadError,
)
from typing import List
from config import config
import redis
from dotenv import load_dotenv


class ProcContext:
    redis = None
    logger = None


proc_context = ProcContext()


def fetch_wiki_data(
    category: str,
    filepath: str,
    inverse_filter: list,
    category_pages_downloaded: dict,
    depth: int,
) -> int:
    """
    Fetches Wikipedia data for a given category and saves it to the specified filepath.

    Args:
        category (str): The Wikipedia category to fetch data for.
        filepath (str): The directory path to save the data.
        inverse_filter (list): A list of page/category titles to exclude.
        category_pages_downloaded (dict): A dictionary to track the number of pages downloaded per category.
        depth (int): The current depth of the recursive fetch.

    Returns:
        int: The total number of pages downloaded.
    """
    try:
        if (
            depth > 100
        ):  # Limit the depth to 100; max depth of Wikipedia category tree ~ 15-20
            return 0

        if not os.path.exists(filepath):
            os.makedirs(filepath)

        num_total_pages_downloaded = 0
        title_pathname = get_title_pathname_map(
            category, filepath, inverse_filter, create=True
        )

        pages = title_pathname["pages"]
        for page_title, page_filename in pages.items():
            if proc_context.redis.sismember("downloaded_pages", page_title):
                continue
            download_page(page_title, page_filename, filepath)
            num_total_pages_downloaded += 1
            proc_context.redis.sadd("downloaded_pages", page_title)

        if num_total_pages_downloaded > 0:
            category_pages_downloaded[category] = num_total_pages_downloaded

        subcategories = title_pathname["categories"]
        for subcategory_title, subcategory_path in subcategories.items():
            if proc_context.redis.sismember("downloaded_categories", subcategory_title):
                continue
            subcategory_path = os.path.join(filepath, subcategory_path)
            subcategory_total_pages_downloaded = fetch_wiki_data(
                subcategory_title,
                subcategory_path,
                inverse_filter,
                category_pages_downloaded,
                depth + 1,
            )
            num_total_pages_downloaded += subcategory_total_pages_downloaded
            proc_context.redis.sadd("downloaded_categories", subcategory_title)

        return num_total_pages_downloaded

    except WikiDownloadError as e:
        proc_context.logger.error(
            f"Error fetching data for category {category}: {e}", exc_info=True
        )
        return -1
    except Exception as e:
        proc_context.logger.error(
            f"Unexpected error fetching data for category {category}: {e}",
            exc_info=True,
        )
        return -1


def main():
    load_dotenv()

    log_level = config.get("level", "INFO")
    log_format = config.get("format", "%(asctime)s - %(levelname)s - %(message)s")

    logging.basicConfig(level=log_level, format=log_format)
    proc_context.logger = logging.getLogger("main")

    proc_context.data_ver = config.get("data_ver", "v100")

    category = "Dinosaurs"
    filepath = f"data/{proc_context.data_ver}/Dinosaurs"

    redis_host = os.getenv("REDIS_HOST")
    redis_port = int(os.getenv("REDIS_PORT"))
    redis_db = int(os.getenv("REDIS_DB"))
    proc_context.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    proc_context.logger.info(f"Downloading category members for {category}")
    category_pages_downloaded = {}
    exclude_keywords = [
        "bird",
        "list of",
        "lists of",
    ]  # Exclude pages and categories with these keywords in their title
    depth = (
        0 if proc_context.data_ver == "v3000" else 99
    )  # Set depth to 99 for v100 data version, so that only about 100 pages are downloaded for testing purposes
    num_pages_downloaded = fetch_wiki_data(
        category, filepath, exclude_keywords, category_pages_downloaded, depth
    )

    proc_context.logger.info(f"Downloaded total {num_pages_downloaded} pages")
    proc_context.logger.info(f"Category pages downloaded: {category_pages_downloaded}")


if __name__ == "__main__":
    main()
