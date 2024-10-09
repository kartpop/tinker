from bs4 import BeautifulSoup
import re
from typing import List


def html_to_text_chunks(html_str: str) -> List[str]:
    """
    Extracts text chunks from a Wikipedia page HTML string. The chunks are cleaned and returned as a list of strings.

    The logic is not exhaustive and currently only extracts clean text from paragraph and list items.
    All other tags are returned as strings.
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
                if li_text: # Skip empty list items (images etc.)
                    chunks.append(
                        "- " + li_text
                    )  # Clean and add each list item text to chunks with prefix
        else:
            chunks.append(str(tag))  # Add other tags as strings

    return chunks
