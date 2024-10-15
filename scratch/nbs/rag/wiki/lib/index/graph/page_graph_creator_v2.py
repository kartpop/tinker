from neo4j import GraphDatabase
import uuid

# v2: 
# - added :FRIST_SECTION and :NEXT_SECTION relationships
# - renamed :NEXT to :NEXT_CHUNK
# - optimized cypher queries to use indexes
# - capture page_uuid and section_uuid from the result of the cypher queries, in case the page or section already existed

class Neo4jPageGraphCreatorv2:
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
            RETURN p.uuid AS page_uuid
            """
            result = session.execute_write(
                self._run_query, page_query, title=page_dict["title"], uuid=page_uuid
            )

            # Extract the page_uuid from the result
            # If page already existed, get the existing page_uuid
            page_uuid = result.single()["page_uuid"]

            # Create sections and chunks
            self.create_sections_and_chunks(session, page_uuid, page_dict["sections"], "Page")
            self.create_chunks(session, page_uuid, page_dict["chunks"])

    def create_sections_and_chunks(self, session, parent_uuid, sections, parent_type):
        first_section_created = False

        for i, section in enumerate(sections):
            section_uuid = str(uuid.uuid4())
            section_labels = f":Section:{section['type']}"

            # Query to find either Page or Section as parent
            # Uniqueness constraint on {parent_uuid, name, section_labels}
            section_query = f"""
            MATCH (parent:{parent_type} {{uuid: $parent_uuid}})
            MERGE (s{section_labels} {{name: $name, parent_uuid: $parent_uuid}})
            ON CREATE SET s.uuid = $uuid
            RETURN s.uuid AS section_uuid
            """
            result = session.execute_write(
                self._run_query,
                section_query,
                parent_uuid=parent_uuid,
                name=section["name"],
                uuid=section_uuid,
            )

            # Extract the section_uuid from the result
            # If section already existed, get the existing section_uuid
            section_uuid = result.single()["section_uuid"]

            # Create the FIRST_SECTION relationship if first_section not yet created
            # Additionally also check if parent already has a FIRST_SECTION relationship, delete if so before creating new one
            if not first_section_created and i == 0:
                first_section_query = f"""
                MATCH (parent:{parent_type} {{uuid: $parent_uuid}})
                OPTIONAL MATCH (parent)-[r:FIRST_SECTION]->()
                DELETE r
                WITH parent
                MATCH (s:Section {{uuid: $section_uuid}})
                MERGE (parent)-[:FIRST_SECTION]->(s)
                RETURN parent, s
                """
                session.execute_write(
                    self._run_query,
                    first_section_query,
                    parent_uuid=parent_uuid,
                    section_uuid=section_uuid,
                )
                first_section_created = True

            # Recursively create sub-sections and chunks
            self.create_sections_and_chunks(session, section_uuid, section["sections"], "Section")
            self.create_chunks(session, section_uuid, section["chunks"])

        # Create NEXT_SECTION relationships between sections once all sections are created
        for i, section in enumerate(sections):
            # Set the NEXT_SECTION relationship
            # Additionally also check if section already has NEXT_SECTION relationship, delete if so before creating new one
            if i < len(sections) - 1:
                next_section_query = """
                MATCH (s1:Section {uuid: $uuid1})
                OPTIONAL MATCH (s1)-[r:NEXT_SECTION]->()
                DELETE r
                WITH s1
                MATCH (s2:Section {uuid: $uuid2})
                MERGE (s1)-[:NEXT_SECTION]->(s2)
                RETURN s1, s2
                """
                session.execute_write(
                    self._run_query,
                    next_section_query,
                    uuid1=sections[i]["uuid"],
                    uuid2=sections[i + 1]["uuid"],
                )

    def create_chunks(self, session, parent_uuid, chunks, parent_type):
        first_chunk_created = False

        for i, chunk in enumerate(chunks):
            # Use chunk['id'] as the UUID
            chunk_uuid = chunk["id"]

            chunk_query = f"""
            MATCH (parent:{parent_type} {{uuid: $parent_uuid}})
            MERGE (c:Chunk {{uuid: $uuid}})
            MERGE (parent)-[:HAS_CHUNK]->(c)
            RETURN c
            """
            session.execute_write(
                self._run_query, chunk_query, parent_uuid=parent_uuid, uuid=chunk_uuid
            )

            # Create the FIRST_CHUNK relationship if first_chunk not yet created
            # Additionally also check if parent already has a FIRST_CHUNK relationship, delete if so before creating new one
            if not first_chunk_created and i == 0:
                first_chunk_query = f"""
                MATCH (parent:{parent_type} {{uuid: $parent_uuid}})
                OPTIONAL MATCH (parent)-[r:FIRST_CHUNK]->()
                DELETE r
                WITH parent
                MATCH (c:Chunk {{uuid: $chunk_uuid}})
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

        # Create NEXT_CHUNK relationships between chunks once all chunks are created
        for i, chunk in enumerate(chunks):
            # Set the NEXT_CHUNK relationship
            # Additionally also check if chunk already has NEXT_CHUNK relationship, delete if so before creating new one
            if i < len(chunks) - 1:
                next_chunk_query = """
                MATCH (c1:Chunk {uuid: $uuid1})
                OPTIONAL MATCH (c1)-[r:NEXT_CHUNK]->()
                DELETE r
                WITH c1
                MATCH (c2:Chunk {uuid: $uuid2})
                MERGE (c1)-[:NEXT_CHUNK]->(c2)
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
