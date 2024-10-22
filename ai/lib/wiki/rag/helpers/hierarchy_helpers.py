def get_subhierarchy_and_metadata_from_path(page_hierarchy, path):
    """
    Get sub-hierarchy by path from the page hierarchy.
    Also extract metadata from the hierarchy. Example, "metadata": {"title": "Dinosaur", "h2": "Paleobiology", "h3": "Size"}
    """

    def get_hierarchy_by_path_recursive(hierarchy, sections, metadata):
        # Base case: if no more sections to traverse, return the current level
        if not sections:
            return hierarchy

        # Get the current section to look for
        current_section = sections[0]

        # Check if the current level has subsections
        if "sections" in hierarchy:
            for sub_section in hierarchy["sections"]:
                if sub_section["name"] == current_section:
                    # Set the metadata for the current section
                    metadata[sub_section["type"]] = sub_section["name"]
                    # Recursively call the function with the remaining sections
                    return get_hierarchy_by_path_recursive(
                        sub_section, sections[1:], metadata
                    )

        # If the section is not found, raise an exception
        raise Exception(f"Section '{current_section}' not found in the hierarchy.")

    sections = path[1:]  # Skip the first element which is the page title
    metadata = {"title": path[0]}
    try:
        page_sub_hierarchy = get_hierarchy_by_path_recursive(
            page_hierarchy, sections, metadata
        )
    except Exception as e:
        raise e
    # Call the recursive function
    return page_sub_hierarchy, metadata


def extract_chunks_from_hierarchy(chunks_hierarchy):
    """
    Extract all chunk IDs from the hierarchy.
    """
    # Initialize an empty list to store chunk IDs
    chunks_list = []

    # Recursive function to traverse the hierarchy and collect chunk IDs
    def traverse_hierarchy(hierarchy):
        # Add the chunks at the current level to the list
        if "chunks" in hierarchy:
            chunks_list.extend(hierarchy["chunks"])

        # Recursively traverse the sections
        if "sections" in hierarchy:
            for section in hierarchy["sections"]:
                traverse_hierarchy(section)

    # Start the traversal from the root of the hierarchy
    traverse_hierarchy(chunks_hierarchy)

    return chunks_list


def create_context_text_from_hierarchy(chunk_hierarchy, chunk_docs):
    """
    Create context text from the chunk hierarchy and chunk contents.
    """
    # Create a mapping of chunk IDs to document content
    chunk_id_to_content = {doc.id: doc.content for doc in chunk_docs}

    # Recursive function to traverse the hierarchy and construct plain text output
    def traverse_and_construct_text(hierarchy, level=0):
        output = []
        indent = "  " * level  # Indentation based on the hierarchy level

        # Add the section title and type
        if "name" in hierarchy and "type" in hierarchy:
            output.append(f"{indent}{hierarchy['name']} ({hierarchy['type']}):")

        # Add the chunks content as a paragraph
        if "chunks" in hierarchy:
            chunk_contents = [
                chunk_id_to_content.get(
                    chunk_id, f"Missing content for chunk {chunk_id}"
                )
                for chunk_id in hierarchy["chunks"]
            ]
            indented_chunk_contents = [
                f"{indent}{content}" for content in chunk_contents
            ]
            output.append(
                "\n\n".join(indented_chunk_contents)
            )  # Add extra newlines between chunks

        # Recursively traverse the sections
        if "sections" in hierarchy:
            for section in hierarchy["sections"]:
                output.append(
                    "\n\n" + traverse_and_construct_text(section, level + 1)
                )  # Add extra newlines between sections

        return "\n".join(output)

    # Start the traversal and construction from the root of the hierarchy
    return traverse_and_construct_text(chunk_hierarchy)
