from neo4j import GraphDatabase
import uuid


class Neo4jCategoryGraphCreator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.create_indexes()

    def create_indexes(self):
        index_queries = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Category) ON (n.title);",
            "CREATE INDEX IF NOT EXISTS FOR (n:Category) ON (n.uuid);"
        ]
        with self.driver.session() as session:
            for query in index_queries:
                session.execute_write(self._run_query, query)

    def close(self):
        self.driver.close()


    def create_category_to_page_relationship(self, category: str, page: str):
        query = """
        MERGE (c:Category {title: $category_title})
        ON CREATE SET c.uuid = $category_uuid
        WITH c
        MATCH (p:Page {title: $page_title})
        WHERE p.uuid IS NOT NULL
        MERGE (c)-[:HAS_PAGE]->(p)
        """
        with self.driver.session() as session:
            session.execute_write(
                self._run_query,
                query,
                category_title=category,
                page_title=page,
                category_uuid=str(uuid.uuid4()),
            )


    def create_category_to_subcategory_relationship(self, category: str, subcategory: str):
        query = """
        MERGE (c:Category {title: $category_title})
        ON CREATE SET c.uuid = $category_uuid
        MERGE (sc:Category {title: $subcategory_title})
        ON CREATE SET sc.uuid = $subcategory_uuid
        MERGE (c)-[:HAS_SUBCATEGORY]->(sc)
        """
        with self.driver.session() as session:
            session.execute_write(
                self._run_query,
                query,
                category_title=category,
                subcategory_title=subcategory,
                category_uuid=str(uuid.uuid4()),
                subcategory_uuid=str(uuid.uuid4()),
            )

    @staticmethod
    def _run_query(tx, query, **parameters):
        return tx.run(query, **parameters)
