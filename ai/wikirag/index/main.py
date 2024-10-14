import os
import logging
from config import config
import redis
from dotenv import load_dotenv
from downloader import Downloader
from datetime import datetime


def main():
    load_dotenv()

    if not os.path.exists("logs"):
        os.makedirs("logs")

    data_ver = config.get("data_ver", "v100")

    # Logging
    log_level = config.get("level", "INFO")
    log_format = config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger(__name__)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/index_{data_ver}_{timestamp}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    # Redis
    redis_host = os.getenv("REDIS_HOST")
    redis_port = int(os.getenv("REDIS_PORT"))
    redis_db = int(os.getenv("REDIS_DB"))
    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    category = "Dinosaurs"
    filepath = f"data/{data_ver}/Dinosaurs"

    # Download wiki data
    downloader = Downloader(logger, redis_client)
    logger.info(f"Downloading category members for {category}")
    category_pages_downloaded = {}
    exclude_keywords = [
        "bird",
        "list of",
        "lists of",
    ]  # Exclude pages and categories with these keywords in their title
    depth = (
        0 if data_ver == "v3000" else 99
    )  # Set depth to 99 for v100 data version, so that only about 100 pages are downloaded for testing purposes
    num_pages_downloaded = downloader.fetch_wiki_data(
        category, filepath, exclude_keywords, category_pages_downloaded, depth
    )
    if num_pages_downloaded == -1:
        logger.error(f"Failed to download data for category {category}")
    else:
        logger.info(
            f"Successfully downloaded {num_pages_downloaded} total pages.\nCategory pages: {category_pages_downloaded}"
        )


if __name__ == "__main__":
    main()
