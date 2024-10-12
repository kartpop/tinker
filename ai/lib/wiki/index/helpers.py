import json
from typing import List
import os
import requests
from config import config


def get_wiki_category_members(category: str, filepath: str) -> list:
    """
    Returns the list of pages and sub-categories of a given Wikipedia category.
    """
    metadata_download_path = os.path.join(filepath, ".metadata/download")
    if not os.path.exists(metadata_download_path):
        os.makedirs(metadata_download_path)

    response_filepath = os.path.join(metadata_download_path, "response.json")
    if os.path.exists(response_filepath):
        with open(response_filepath, "r") as file:
            response_data = json.load(file)
        return response_data["query"]["categorymembers"]

    # Make the initial request to get the category information
    url = config.get("wiki.url").format(category=category)
    headers = config.get("wiki.headers")
    response = requests.get(url, headers=headers)
    write_response_data = response.json()

    with open(response_filepath, "w") as file:
        json.dump(write_response_data, file)

    response_data = response.json()

    return response_data["query"]["categorymembers"]


def get_title_pathname_map(
    category: str,
    filepath: str,
    inverse_filter: List[str] = [],
    create_if_not_exists: bool = False,
) -> dict:
    """
    Returns a map of page_title to file name and category title to directory name derived from Wikipedia response query.
    Pages/categories in the inverse_filter list are not included.
    """
    metadata_download_path = os.path.join(filepath, ".metadata/download")

    title_pathname_filepath = os.path.join(
        metadata_download_path, "title_pathname.json"
    )
    if os.path.exists(title_pathname_filepath):
        with open(title_pathname_filepath, "r") as file:
            title_pathname_data = json.load(file)
        return title_pathname_data

    if not os.path.exists(metadata_download_path):
        if create_if_not_exists:
            os.makedirs(metadata_download_path)
        else:
            raise FileNotFoundError("Metadata download path does not exist.")

    title_pathname = {"pages": {}, "categories": {}}

    category_members = get_wiki_category_members(category, filepath)

    for member in category_members:
        # Skip members to filter out based on keywords or phrases in inverse_filter
        # Example: inverse_filter = ["birds", "list of"] will filter out all pages/categories with "birds" or "list of" in their title
        if any(
            keyword.lower() in member["title"].lower() for keyword in inverse_filter
        ):
            continue

        if member["ns"] == 0:  # Page
            title_pathname["pages"][member["title"]] = f"{member['title']}.html"
        elif member["ns"] == 14:  # Category
            title_pathname["categories"][member["title"]] = member["title"]

    # Save the title_pathname map to a file
    with open(title_pathname_filepath, "w") as file:
        json.dump(title_pathname, file)

    return title_pathname
