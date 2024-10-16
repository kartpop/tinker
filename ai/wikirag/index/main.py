import os
import logging
from config import config
import redis
from dotenv import load_dotenv
from downloader import Downloader
from chunker import Chunker
from indexer import Indexer
from datetime import datetime
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack_integrations.document_stores.weaviate.document_store import (
    WeaviateDocumentStore,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from neo4j import GraphDatabase
from lib.wiki.index.graph.page_graph_creator import Neo4jPageGraphCreator
from lib.wiki.index.graph.category_graph_creator import Neo4jCategoryGraphCreator


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
    log_filepath = config.get("index.log_filepath", "/aux/data/wiki/v100/logs/index/")
    log_filename = f"{log_filepath}{timestamp}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))
    REDIS_DB = int(os.getenv("REDIS_DB"))
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    category = config.get("index.category", "Dinosaurs")
    filepath = config.get("index.filepath", f"/aux/data/wiki/v100/Dinosaurs")

    # Download wiki data
    downloader = Downloader(logger, redis_client)
    logger.info(f"Downloading category members for {category}")
    category_pages_downloaded = {}
    exclude_keywords = config.get(
        "index.exclude_keywords", ["bird", "list of", "lists of"]
    )  # Exclude pages and categories with these keywords in their title
    max_depth = config.get("index.max_depth", 2)
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

    # Index wiki data
    logger.info(f"Indexing category members for {category}")
    NEO4J_HOST = os.getenv("NEO4J_HOST")
    NEO4J_PORT = int(os.getenv("NEO4J_PORT"))
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    WEAVIATE_HOST = os.getenv("WEAVIATE_HOST")
    WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT"))

    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
    ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT"))

    embedding_model = config.get("embedding_model", "text-embedding-3-small")
    embedder = OpenAIDocumentEmbedder(model=embedding_model)
    w_store = WeaviateDocumentStore(url=f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}")
    e_store = ElasticsearchDocumentStore(
        hosts=[f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"]
    )
    graph_creator_driver = GraphDatabase.driver(
        f"bolt://{NEO4J_HOST}:{NEO4J_PORT}", auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    page_graph_creator = Neo4jPageGraphCreator(graph_creator_driver)
    category_graph_creator = Neo4jCategoryGraphCreator(graph_creator_driver)

    indexer = Indexer(
        logger,
        redis_client,
        embedder,
        w_store,
        e_store,
        page_graph_creator,
        category_graph_creator,
    )
    category_pages_indexed = {}
    try:
        num_pages_indexed = indexer.index_wiki_data(
            category, filepath, category_pages_indexed
        )
        if num_pages_indexed == -1:
            logger.error(f"Failed to index data for category {category}")
        else:
            logger.info(
                f"Successfully indexed {num_pages_indexed} total pages.\nIndexed category pages: {category_pages_indexed}"
            )
    finally:
        w_store.client.close()
        e_store.client.close()
        page_graph_creator.close()
        category_graph_creator.close()


if __name__ == "__main__":
    main()
