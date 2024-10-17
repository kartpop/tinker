from datetime import datetime
from logging import config
import logging
import os
from haystack_integrations.document_stores.weaviate.document_store import (
    WeaviateDocumentStore,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from neo4j import GraphDatabase


class Resources:
    def __init__(
        self,
        w_store: WeaviateDocumentStore,
        e_store: ElasticsearchDocumentStore,
        neo4j_driver: GraphDatabase.driver,
    ):
        self.w_store = w_store
        self.e_store = e_store
        self.neo4j_driver = neo4j_driver

    def close(self):
        self.w_store.client.close()
        self.e_store.client.close()
        self.neo4j_driver.close()


def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_level = config.get("level", "INFO")
    log_format = config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger(__name__)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filepath = config.get("rag.log_filepath", "/aux/data/wiki/v3000/logs/rag/")
    log_filename = f"{log_filepath}{timestamp}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    return logger

