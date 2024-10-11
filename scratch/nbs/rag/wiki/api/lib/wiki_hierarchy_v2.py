from neo4j import GraphDatabase

# v2: optimized cypher queries


class WikiHierarchyV2:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_hierarchy(self, chunk_id):
        with self.driver.session() as session:
            # Step 1: Find the title node from the chunk ID
            page_node = session.run(
                """
                MATCH (chunk:Chunk {uuid: $chunk_id})
                OPTIONAL MATCH (page:Page)-[:HAS_SECTION*0..]->(section)-[:HAS_CHUNK]->(chunk)
                WHERE page IS NOT NULL
                RETURN DISTINCT page
                """,
                chunk_id=chunk_id,
            ).single()

            if not page_node:
                return None, None

            page_node = page_node["page"]

            # Step 2: Build the hierarchies for sections and chunks attached to the Page node
            section_hierarchy, chunks_hierarchy = self.build_section_hierarchy(
                session, page_node["uuid"], "Page"
            )

            return page_node["title"], section_hierarchy, chunks_hierarchy

    def build_section_hierarchy(self, session, node_uuid, node_type):
        # Initialize the hierarchies
        section_hierarchy = {}
        chunks_hierarchy = {"chunks": []}

        # Get the sections connected to this node
        
        ### TODO:
        ### CHANGE IMPLEMENTATION - USE :FIRST_SECTION and :NEXT_SECTION relationships
        
        query = f"""
        MATCH (n:{node_type} {{uuid: $uuid}})-[:HAS_SECTION]->(s:Section)
        RETURN s, labels(s) AS labels
        """

        sections = session.run(query, uuid=node_uuid)

        section_list = []
        chunks_list = []
        for section in sections:
            section_node = section["s"]
            labels = section["labels"]
            # Determine the type from the labels
            section_type = next(
                label for label in labels if label in {"h2", "h3", "h4"}
            )
            section_hierarchy_entry = {
                "name": section_node["name"],
                "type": section_type,
            }
            chunks_hierarchy_entry = {
                "name": section_node["name"],
                "type": section_type,
                "chunks": [],
            }
            # Recursively build the hierarchy for subsections
            subsection_section_hierarchy, subsection_chunks_hierarchy = (
                self.build_section_hierarchy(session, section_node["uuid"], "Section")
            )
            if "sections" in subsection_section_hierarchy:
                section_hierarchy_entry["sections"] = subsection_section_hierarchy[
                    "sections"
                ]
            if "sections" in subsection_chunks_hierarchy:
                chunks_hierarchy_entry["sections"] = subsection_chunks_hierarchy[
                    "sections"
                ]
            section_list.append(section_hierarchy_entry)

            # Get the chunks directly connected to this section node.
            # Note: We could directly get the chunks connected to the section using :HAS_CHUNK relationship.
            # However, the returned chunks may not be ordered correctly.
            # Hence, we traverse the chunks using the :FIRST_CHUNK and :NEXT relationships.
            section_chunks = session.run(
                """
                MATCH (s:Section {uuid: $uuid})-[:FIRST_CHUNK]->(first_chunk)
                OPTIONAL MATCH path = (first_chunk)-[:NEXT*]->(c)
                WITH first_chunk, collect(c) AS subsequent_chunks
                WITH [first_chunk] + subsequent_chunks AS chunks
                UNWIND chunks AS chunk
                RETURN chunk
                """,
                uuid=section_node["uuid"],
            )
            for chunk in section_chunks:
                chunk_node = chunk["chunk"]
                chunks_hierarchy_entry["chunks"].append(chunk_node["uuid"])

            chunks_list.append(chunks_hierarchy_entry)

        # Get the chunks directly connected to this node.
        query = f"""
        MATCH (n:{node_type} {{uuid: $uuid}})-[:FIRST_CHUNK]->(first_chunk)
        OPTIONAL MATCH path = (first_chunk)-[:NEXT*]->(c)
        WITH first_chunk, collect(c) AS subsequent_chunks
        WITH [first_chunk] + subsequent_chunks AS chunks
        UNWIND chunks AS chunk
        RETURN chunk
        """

        chunks = session.run(query, uuid=node_uuid)
        for chunk in chunks:
            chunk_node = chunk["chunk"]
            chunks_hierarchy["chunks"].append(chunk_node["uuid"])

        if section_list:
            section_hierarchy["sections"] = section_list
        if chunks_list:
            chunks_hierarchy["sections"] = chunks_list

        return section_hierarchy, chunks_hierarchy
