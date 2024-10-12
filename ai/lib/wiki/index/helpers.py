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
    else:
        # Make the initial request to get the category information
        url = config.get("wiki.url").format(category=category)
        headers = config.get("wiki.headers")
        response = requests.get(url, headers=headers)
        response_data = response.json()

        with open(response_filepath, "w") as file:
            json.dump(response_data, file)

    # Check if 'query' and 'categorymembers' keys exist
    if "query" not in response_data or "categorymembers" not in response_data["query"]:
        raise KeyError(
            "'query' and 'categorymembers' keys must be present in the response data"
        )

    return response_data["query"]["categorymembers"]


def get_title_pathname_map(
    category: str,
    filepath: str,
    inverse_filter: List[str] = [],
    create: bool = False,
) -> dict:
    """
    Returns a map of page title to file name and category title to directory name derived from Wikipedia response query.
    Pages/categories in the inverse_filter list are excluded. In case the title_pathname.json file does not exist, it is created
    if 'create' flag is set to True, else a FileNotFoundError is raised.
    """
    metadata_download_path = os.path.join(filepath, ".metadata/download")
    if not os.path.exists(metadata_download_path) and not create:
        raise FileNotFoundError("Metadata download path does not exist.")

    title_pathname_filepath = os.path.join(
        metadata_download_path, "title_pathname.json"
    )
    if os.path.exists(title_pathname_filepath):
        with open(title_pathname_filepath, "r") as file:
            title_pathname_data = json.load(file)
        return title_pathname_data

    title_pathname = {"pages": {}, "categories": {}}

    category_members = get_wiki_category_members(category, filepath)

    for member in category_members:
        # Skip members to filter out based on keywords or phrases in inverse_filter
        # Example: inverse_filter = ["birds", "list of"] will filter out all pages/categories with "birds" or "list of" in their title
        if any(
            keyword.lower() in member["title"].lower() for keyword in inverse_filter
        ):
            continue

        if member["ns"] == 0:
            page_title = member["title"]
            underscored_page_title = page_title.replace(" ", "_")
            page_filename = f"{underscored_page_title}.html"
            title_pathname["pages"][page_title] = page_filename
        elif member["ns"] == 14:
            category_title = member["title"].replace("Category:", "")
            underscored_category_title = category_title.replace(" ", "_")
            category_dirname = f"{underscored_category_title}"
            title_pathname["categories"][category_title] = category_dirname

    # Save the title_pathname map to a file
    with open(title_pathname_filepath, "w") as file:
        json.dump(title_pathname, file)

    return title_pathname
