from neo4j import GraphDatabase
import uuid


class Neo4jPageGraphCreator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.create_indexes()

    def create_indexes(self):
        index_queries = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Chunk) ON (n.uuid);",
            "CREATE INDEX IF NOT EXISTS FOR (n:Page) ON (n.uuid);",
            "CREATE INDEX IF NOT EXISTS FOR (n:Page) ON (n.title);",
            "CREATE INDEX IF NOT EXISTS FOR (n:Section) ON (n.uuid);",
            "CREATE INDEX IF NOT EXISTS FOR (n:Section) ON (n.parent_uuid, n.name);"
        ]
        with self.driver.session() as session:
            for query in index_queries:
                session.execute_write(self._run_query, query)

    def close(self):
        self.driver.close()

    def create_graph(self, page_dict):
        with self.driver.session() as session:
            # Create Page node with UUID
            # Unique constraint on Page title
            page_uuid = str(uuid.uuid4())
            page_query = """
            MERGE (p:Page {title: $title})
            ON CREATE SET p.uuid = $uuid
            RETURN p
            """
            session.execute_write(
                self._run_query, page_query, title=page_dict["title"], uuid=page_uuid
            )

            # Create sections and chunks
            self.create_sections_and_chunks(session, page_uuid, page_dict["sections"])
            self.create_chunks(session, page_uuid, page_dict["chunks"])

    def create_sections_and_chunks(self, session, parent_uuid, sections):
        for section in sections:
            section_uuid = str(uuid.uuid4())
            section_labels = f":Section:{section['type']}"

            # Query to find either Page or Section as parent
            # Uniqueness constraint on {parent_uuid, name, section_labels}
            section_query = f"""
            MATCH (parent {{uuid: $parent_uuid}})
            MERGE (s{section_labels} {{name: $name, parent_uuid: $parent_uuid}})
            ON CREATE SET s.uuid = $uuid
            MERGE (parent)-[:HAS_SECTION]->(s)
            RETURN s
            """
            session.execute_write(
                self._run_query,
                section_query,
                parent_uuid=parent_uuid,
                name=section["name"],
                uuid=section_uuid,
            )

            # Recursively create sub-sections and chunks
            self.create_sections_and_chunks(session, section_uuid, section["sections"])
            self.create_chunks(session, section_uuid, section["chunks"])

    def create_chunks(self, session, parent_uuid, chunks):
        first_chunk_created = False

        for i, chunk in enumerate(chunks):
            # Use chunk['id'] as the UUID
            chunk_uuid = chunk["id"]

            chunk_query = """
            MATCH (parent {uuid: $parent_uuid})
            MERGE (c:Chunk {uuid: $uuid})
            MERGE (parent)-[:HAS_CHUNK]->(c)
            RETURN c
            """
            session.execute_write(
                self._run_query, chunk_query, parent_uuid=parent_uuid, uuid=chunk_uuid
            )

            # Create the FIRST_CHUNK relationship if first_chunk not yet created
            # Additionally also check if parent already has a FIRST_CHUNK relationship, delete if so before creating new one
            if not first_chunk_created and i == 0:
                first_chunk_query = """
                MATCH (parent {uuid: $parent_uuid})
                OPTIONAL MATCH (parent)-[r:FIRST_CHUNK]->()
                DELETE r
                WITH parent
                MATCH (c:Chunk {uuid: $chunk_uuid})
                MERGE (parent)-[:FIRST_CHUNK]->(c)
                RETURN parent, c
                """
                session.execute_write(
                    self._run_query,
                    first_chunk_query,
                    parent_uuid=parent_uuid,
                    chunk_uuid=chunk["id"],
                )
                first_chunk_created = True

        # Create NEXT relationships between chunks once all chunks are created
        for i, chunk in enumerate(chunks):
            # Set the NEXT relationship
            # Additionally also check if chunk already has NEXT relationship, delete if so before creating new one
            if i < len(chunks) - 1:
                next_chunk_query = """
                MATCH (c1:Chunk {uuid: $uuid1})
                OPTIONAL MATCH (c1)-[r:NEXT]->()
                DELETE r
                WITH c1
                MATCH (c2:Chunk {uuid: $uuid2})
                MERGE (c1)-[:NEXT]->(c2)
                RETURN c1, c2
                """
                session.execute_write(
                    self._run_query,
                    next_chunk_query,
                    uuid1=chunk["id"],
                    uuid2=chunks[i + 1]["id"],
                )

    @staticmethod
    def _run_query(tx, query, **parameters):
        return tx.run(query, **parameters)
