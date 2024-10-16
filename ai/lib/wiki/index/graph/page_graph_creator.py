from neo4j import GraphDatabase
import uuid

class Neo4jPageGraphCreator:
    """
    Creates a graph in Neo4j representing a page and its sections and chunks. Creates the relevant indexes for efficient lookups.
    """
    def __init__(self, driver: GraphDatabase.driver):
        self.driver = driver
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
                session.run(query)

    def close(self):
        self.driver.close()

    def create_graph(self, page_dict):
        """
        Creates a graph in Neo4j representing a page and its sections and chunks.
        
        Creates the following nodes and relationships:
        - Page: HAS_CHUNK -> Chunk, FIRST_CHUNK -> Chunk, FIRST_SECTION -> Section, NEXT_SECTION -> Section
        - Section: HAS_CHUNK -> Chunk, FIRST_CHUNK -> Chunk, NEXT_SECTION -> Section
        - Chunk: NEXT_CHUNK -> Chunk
        """
        with self.driver.session() as session:
            # Create Page node with UUID
            page_uuid = str(uuid.uuid4())
            page_query = """
            MERGE (p:Page {title: $title})
            ON CREATE SET p.uuid = $uuid
            RETURN p.uuid AS page_uuid
            """
            result = session.run(page_query, title=page_dict["title"], uuid=page_uuid)
            record = result.single()

            if record:
                page_uuid = record["page_uuid"]
            else:
                raise RuntimeError("Failed to retrieve page_uuid; transaction may be closed unexpectedly.")

            # Create sections and chunks
            self.create_sections_and_chunks(session, page_uuid, page_dict["sections"], "Page")
            self.create_chunks(session, page_uuid, page_dict["chunks"], "Page")

    def create_sections_and_chunks(self, session, parent_uuid, sections, parent_type):
        first_section_created = False
        section_uuids = []

        for i, section in enumerate(sections):
            section_uuid = str(uuid.uuid4())
            section_labels = f":Section:{section['type']}"
            section_query = f"""
            MATCH (parent:{parent_type} {{uuid: $parent_uuid}})
            MERGE (s{section_labels} {{name: $name, parent_uuid: $parent_uuid}})
            ON CREATE SET s.uuid = $uuid
            MERGE (parent)-[:HAS_SECTION]->(s)
            RETURN s.uuid AS section_uuid
            """
            result = session.run(
                section_query,
                parent_uuid=parent_uuid,
                name=section["name"],
                uuid=section_uuid,
            )
            record = result.single()
            if record:
                section_uuid = record["section_uuid"]
                section_uuids.append(section_uuid)
            else:
                raise RuntimeError("Failed to retrieve section_uuid; transaction may be closed unexpectedly.")

            # Create the FIRST_SECTION relationship if first_section not yet created
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
                session.run(
                    first_section_query,
                    parent_uuid=parent_uuid,
                    section_uuid=section_uuid,
                )
                first_section_created = True

            self.create_sections_and_chunks(session, section_uuid, section["sections"], "Section")
            self.create_chunks(session, section_uuid, section["chunks"], "Section")

        # Create NEXT_SECTION relationships between sections once all sections are created
        for i, section_uuid in enumerate(section_uuids):
            if i < len(section_uuids) - 1:
                next_section_query = """
                MATCH (s1:Section {uuid: $uuid1})
                OPTIONAL MATCH (s1)-[r:NEXT_SECTION]->()
                DELETE r
                WITH s1
                MATCH (s2:Section {uuid: $uuid2})
                MERGE (s1)-[:NEXT_SECTION]->(s2)
                RETURN s1, s2
                """
                session.run(
                    next_section_query,
                    uuid1=section_uuids[i],
                    uuid2=section_uuids[i + 1],
                )

    def create_chunks(self, session, parent_uuid, chunks, parent_type):
        first_chunk_created = False

        for i, chunk in enumerate(chunks):
            chunk_uuid = chunk["id"]
            chunk_query = f"""
            MATCH (parent:{parent_type} {{uuid: $parent_uuid}})
            MERGE (c:Chunk {{uuid: $uuid}})
            MERGE (parent)-[:HAS_CHUNK]->(c)
            RETURN c
            """
            session.run(chunk_query, parent_uuid=parent_uuid, uuid=chunk_uuid)

            # Create the FIRST_CHUNK relationship if first_chunk not yet created
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
                session.run(
                    first_chunk_query,
                    parent_uuid=parent_uuid,
                    chunk_uuid=chunk["id"],
                )
                first_chunk_created = True

        # Create NEXT_CHUNK relationships between chunks once all chunks are created
        for i, chunk in enumerate(chunks):
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
                session.run(
                    next_chunk_query,
                    uuid1=chunk["id"],
                    uuid2=chunks[i + 1]["id"],
                )

