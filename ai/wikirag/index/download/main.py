import os
import logging
from lib.wiki.index.helpers import get_title_pathname_map, download_page
from typing import List
from config import config
import redis


class ProcContext:
    redis = None
    logger = None
    data_ver = ""


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
        if depth > 100:
            return 0

        if not os.path.exists(filepath):
            os.makedirs(filepath)

        num_total_pages_downloaded = 0
        title_pathname = get_title_pathname_map(
            category, filepath, inverse_filter, create=True
        )

        pages = title_pathname["pages"]
        for page_title, page_filename in pages.items():
            if proc_context.redis.sismember(
                f"downloaded_pages_{proc_context.data_ver}", page_title
            ):
                continue
            download_page(page_title, page_filename, filepath)
            num_total_pages_downloaded += 1
            proc_context.redis.sadd(
                f"downloaded_pages_{proc_context.data_ver}", page_title
            )

        if num_total_pages_downloaded > 0:
            category_pages_downloaded[category] = num_total_pages_downloaded

        subcategories = title_pathname["categories"]
        for subcategory_title, subcategory_path in subcategories.items():
            if proc_context.redis.sismember(
                f"downloaded_categories_{proc_context.data_ver}", subcategory_title
            ):
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
            proc_context.redis.sadd(
                f"downloaded_categories_{proc_context.data_ver}", subcategory_title
            )

        return num_total_pages_downloaded

    except Exception as e:
        proc_context.logger.error(f"Error fetching data for category {category}: {e}")
        return 0


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    proc_context.logger = logging.getLogger()

    proc_context.data_ver = config.get("data_ver")

    category = "Dinosaurs"
    filepath = f"/data/{proc_context.data_ver}/Dinosaurs"

    redis_host, redis_port, redis_db = (
        config.get("databases.redis.host"),
        config.get("databases.redis.port"),
        config.get("databases.redis.db"),
    )
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
