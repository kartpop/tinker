import os
import logging
from config import config
import redis
from dotenv import load_dotenv
from downloader import Downloader
from datetime import datetime


class CollectLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_messages = []

    def emit(self, record):
        self.log_messages.append(self.format(record))


def main():
    load_dotenv()

    # Logging
    log_level = config.get("level", "INFO")
    log_format = config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger(__name__)
    collect_handler = CollectLogHandler()
    collect_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(collect_handler)

    # Redis
    redis_host = os.getenv("REDIS_HOST")
    redis_port = int(os.getenv("REDIS_PORT"))
    redis_db = int(os.getenv("REDIS_DB"))
    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    data_ver = config.get("data_ver", "v100")
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

    # Write logs to file
    if not os.path.exists("logs"):
        os.makedirs("logs")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/download_{timestamp}.log"
    with open(log_filename, "w") as log_file:
        for message in collect_handler.log_messages:
            log_file.write(message + "\n")


if __name__ == "__main__":
    main()
