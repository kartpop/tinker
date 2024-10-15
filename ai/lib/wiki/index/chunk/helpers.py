import json
import os
from bs4 import BeautifulSoup
import re
from typing import List, Tuple

from haystack import Document


def html_to_text_chunks(html_str: str) -> List[str]:
    """
    Extracts text chunks from a Wikipedia page HTML string. The chunks are cleaned and returned as a list of strings.

    The logic is not exhaustive and currently only extracts clean text from paragraph and list items.
    All other tags are returned as strings.

    Args:
        html_str (str): The HTML content of a Wikipedia page as a string.

    Returns:
        List[str]: A list of cleaned text chunks extracted from the HTML content.
    """
    soup = BeautifulSoup(html_str, "html.parser")  # Parse the HTML content

    chunks = []

    def clean_text(text):
        cleaned_text = text.replace("\n", " ").replace(
            "\xa0", " "
        )  # Replace newlines and non-breaking spaces with regular spaces
        cleaned_text = re.sub(
            r"\s+", " ", cleaned_text
        )  # Replace multiple spaces with a single space
        cleaned_text = re.sub(
            r"(\d)\s+(\d)", r"\1\2", cleaned_text
        )  # Remove spaces between digits
        cleaned_text = cleaned_text.strip()  # Remove leading and trailing spaces
        return cleaned_text

    html_soup = (
        soup.body or soup
    )  # Use the body of the HTML if it exists, otherwise use the whole soup
    nested = ["ul", "ol", "dl", "li", "dt", "dd"]  # Tags that represent nested lists
    for tag in html_soup.find_all(
        recursive=False
    ):  # Iterate over top-level tags in the HTML
        if tag.name == "p":
            chunks.append(
                clean_text(tag.get_text(separator=" "))
            )  # Clean and add paragraph text to chunks
        elif tag.name == "link":
            continue  # Skip link tags
        elif tag.name in nested:
            list_items = tag.find_all("li")  # Find all list items
            for li in list_items:
                li_text = clean_text(li.get_text(separator=" "))
                if li_text:  # Skip empty list items (images etc.)
                    chunks.append(
                        "- " + li_text
                    )  # Clean and add each list item text to chunks with prefix
        else:
            chunks.append(str(tag))  # Add other tags as strings

    return chunks


def get_documents_and_page_hierarchy(
    filepath: str, page_title: str, page_filename: str
) -> Tuple[List[Document], dict]:
    """
    Extracts the documents and hierarchy of a page from the stored chunks in the .metadata/chunk/{page_filename}.json file.
    """
    page_filename_wo_ext = os.path.splitext(page_filename)[0]   # Remove file extension (*.html)
    chunk_filepath = os.path.join(
        filepath, ".metadata/chunk", f"{page_filename_wo_ext}.json"
    )
    if not os.path.exists(chunk_filepath):
        raise FileNotFoundError(f"The file '{chunk_filepath}' does not exist.")

    with open(chunk_filepath, "r") as file:
        data = json.load(file)

    if not "splitter" in data:
        raise KeyError(
            f"The 'splitter' key is missing in the chunk file {chunk_filepath}."
        )
    if not "documents" in data["splitter"]:
        raise KeyError(
            f"The 'documents' key is missing in the 'splitter' key in the chunk file {chunk_filepath}."
        )
    if not "hierarchy" in data["splitter"]:
        raise KeyError(
            f"The 'hierarchy' key is missing in the 'splitter' key in the chunk file {chunk_filepath}."
        )

    documents = [
        Document.from_dict(doc) for doc in data["splitter"]["documents"]
    ]  # convert dict to Haystack Document object
    hierarchy = data["splitter"]["hierarchy"][page_title]

    return documents, hierarchy
