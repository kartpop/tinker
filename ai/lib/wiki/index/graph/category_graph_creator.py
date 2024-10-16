from neo4j import GraphDatabase
import uuid

class Neo4jCategoryGraphCreator:
    """
    Creates a graph in Neo4j representing a category and its pages and subcategories. Creates the relevant indexes for efficient lookups.
    """
    def __init__(self, driver: GraphDatabase.driver):
        self.driver = driver
        self.create_indexes()

    def create_indexes(self):
        index_queries = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Category) ON (n.title);",
            "CREATE INDEX IF NOT EXISTS FOR (n:Category) ON (n.uuid);"
        ]
        with self.driver.session() as session:
            for query in index_queries:
                session.run(query)

    def close(self):
        self.driver.close()

    def create_category_to_page_relationship(self, category: str, page: str):
        """
        Creates a relationship in Neo4j between a category and a page. Creates the category node if it does not exist. Does NOT create the page node if it does not exist.
        - Category: HAS_PAGE -> Page
        """
        query = """
        MERGE (c:Category {title: $category_title})
        ON CREATE SET c.uuid = $category_uuid
        WITH c
        MATCH (p:Page {title: $page_title})
        WHERE p.uuid IS NOT NULL
        MERGE (c)-[:HAS_PAGE]->(p)
        """
        with self.driver.session() as session:
            session.run(
                query,
                category_title=category,
                page_title=page,
                category_uuid=str(uuid.uuid4()),
            )

    def create_category_to_subcategory_relationship(self, category: str, subcategory: str):
        """
        Creates a relationship in Neo4j between a category and a subcategory. Creates the category and subcategory nodes if they do not exist.
        - Category: HAS_SUBCATEGORY -> Category
        """
        query = """
        MERGE (c:Category {title: $category_title})
        ON CREATE SET c.uuid = $category_uuid
        MERGE (sc:Category {title: $subcategory_title})
        ON CREATE SET sc.uuid = $subcategory_uuid
        MERGE (c)-[:HAS_SUBCATEGORY]->(sc)
        """
        with self.driver.session() as session:
            session.run(
                query,
                category_title=category,
                subcategory_title=subcategory,
                category_uuid=str(uuid.uuid4()),
                subcategory_uuid=str(uuid.uuid4()),
            )
