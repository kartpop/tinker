import json
from typing import List
import os
import requests
from config import config
import wikipediaapi


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
        url = config.get("wiki.category_info_url").format(category=category)
        headers = config.get("wiki.headers")
        response = requests.get(url, headers=headers)
        response_data = response.json()

        with open(response_filepath, "w") as file:
            json.dump(response_data, file)

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

    Args:
        category (str): The Wikipedia category to fetch data for.
        filepath (str): The directory path to save the data.
        inverse_filter (List[str]): A list of page/category titles to exclude.
        create (bool): Flag to create the title_pathname.json file if it does not exist.

    Returns:
        dict: A dictionary with page titles mapped to file names and category titles mapped to directory names.

    Raises:
        FileNotFoundError: If the title_pathname.json file does not exist and 'create' is set to False.

    Example return dict:
    {
        "pages": {
            "Page1 title": "Page1_title.html",
            "Page2 title": "Page2_title.html"
        },
        "categories": {
            "Category1 title": "Category1_title",
            "Category2 title": "Category2_title"
        }
    }
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

    with open(title_pathname_filepath, "w") as file:
        json.dump(title_pathname, file)

    return title_pathname


def download_page(page_title: str, page_filename: str, filepath: str) -> None:
    """
    Fetches the page content from Wikipedia, saves it in an HTML file in the specified directory, and returns the file name.
    """
    wiki_html = wikipediaapi.Wikipedia(
        user_agent=config.get("wiki.headers.User-Agent"),
        language="en",
        extract_format=wikipediaapi.ExtractFormat.HTML,
    )

    p_html = wiki_html.page(page_title)
    file_path = os.path.join(filepath, page_filename)
    with open(file_path, "w") as file:
        file.write(p_html.text)
