import os
import logging
from config import config
import redis
from dotenv import load_dotenv
from downloader import Downloader
from chunker import Chunker
from datetime import datetime


def main():
    load_dotenv()

    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Logging
    log_level = config.get("level", "INFO")
    log_format = config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger(__name__)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename_prefix = config.get("index_log_filename_prefix", "logs/index")
    log_filename = f"logs/{log_filename_prefix}_{timestamp}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    # Redis
    redis_host = os.getenv("REDIS_HOST")
    redis_port = int(os.getenv("REDIS_PORT"))
    redis_db = int(os.getenv("REDIS_DB"))
    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    category = config.get("index_category", "Dinosaurs")
    filepath = config.get("index_filepath", f"data/v100/Dinosaurs")

    # Download wiki data
    downloader = Downloader(logger, redis_client)
    logger.info(f"Downloading category members for {category}")
    category_pages_downloaded = {}
    exclude_keywords = config.get("index_exclude_keywords", ["bird", "list of", "lists of"])  # Exclude pages and categories with these keywords in their title
    max_depth = config.get("index_max_depth", 2)
    num_pages_downloaded = downloader.fetch_wiki_data(
        category, filepath, exclude_keywords, category_pages_downloaded, max_depth
    )
    if num_pages_downloaded == -1:
        logger.error(f"Failed to download data for category {category}")
    else:
        logger.info(
            f"Successfully downloaded {num_pages_downloaded} total pages.\nDownloaded category pages: {category_pages_downloaded}"
        )

    # Chunk wiki data
    chunker = Chunker(logger, redis_client)
    logger.info(f"Chunking category members for {category}")
    category_pages_chunked = {}
    num_pages_chunked = chunker.chunk_wiki_data(
        category, filepath, category_pages_chunked
    )
    if num_pages_chunked == -1:
        logger.error(f"Failed to chunk data for category {category}")
    else:
        logger.info(
            f"Successfully chunked {num_pages_chunked} total pages.\nChunked category pages: {category_pages_chunked}"
        )

if __name__ == "__main__":
    main()
