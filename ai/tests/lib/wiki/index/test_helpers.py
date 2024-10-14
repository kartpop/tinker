import unittest
from unittest.mock import patch, mock_open
import os
import json
from lib.wiki.index.helpers import get_wiki_category_members, get_title_pathname_map


class TestHelpers(unittest.TestCase):
    
    # ------------------------------------------
    # Test Cases for get_wiki_category_members
    # ------------------------------------------
    
    @patch("lib.wiki.index.helpers.os.path.exists")
    @patch("lib.wiki.index.helpers.os.makedirs")
    @patch(
        "lib.wiki.index.helpers.open",
        new_callable=mock_open,
        read_data='{"query": {"categorymembers": [{"title": "Page1", "ns": 0}, {"title": "Category1", "ns": 14}]}}',
    )
    @patch("lib.wiki.index.helpers.requests.get")
    @patch("lib.wiki.index.helpers.config.get")
    def test_get_wiki_category_members(
        self,
        mock_config_get,
        mock_requests_get,
        mock_open,
        mock_makedirs,
        mock_path_exists,
    ):
        # Mock the config.get method
        mock_config_get.side_effect = lambda key: {
            "wiki.url": "https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{category}&format=json",
            "wiki.headers": {"User-Agent": "test-agent"},
        }.get(key)

        # Mock the os.path.exists method
        mock_path_exists.side_effect = lambda path: path.endswith("response.json")

        # Mock the requests.get method
        mock_requests_get.return_value.json.return_value = {
            "query": {
                "categorymembers": [
                    {"title": "Page1", "ns": 0},
                    {"title": "Category1", "ns": 14},
                ]
            }
        }

        category = "TestCategory"
        filepath = "/test/path"

        result = get_wiki_category_members(category, filepath)

        expected_result = [
            {"title": "Page1", "ns": 0},
            {"title": "Category1", "ns": 14},
        ]

        self.assertEqual(result, expected_result)

    @patch("lib.wiki.index.helpers.os.path.exists")
    @patch("lib.wiki.index.helpers.os.makedirs")
    @patch("lib.wiki.index.helpers.open", new_callable=mock_open, read_data='{}')
    def test_get_wiki_category_members_key_error(self, mock_open, mock_makedirs, mock_path_exists):
        # Mock the os.path.exists method to return True for the response file
        mock_path_exists.side_effect = lambda path: path.endswith("response.json")

        category = "TestCategory"
        filepath = "/test/path"

        with self.assertRaises(KeyError):
            get_wiki_category_members(category, filepath)
            
    
    
    # ------------------------------------------
    # Test Cases for get_title_pathname_map
    # ------------------------------------------

    @patch("lib.wiki.index.helpers.os.path.exists")
    @patch("lib.wiki.index.helpers.os.makedirs")
    @patch(
        "lib.wiki.index.helpers.open",
        new_callable=mock_open,
        read_data='{"pages": {"Page1": "Page1.html"}, "categories": {"Category1": "Category1"}}',
    )
    def test_get_title_pathname_map_file_exists(self, mock_open, mock_makedirs, mock_path_exists):
        # Mock the os.path.exists method to return True for the metadata download path and the JSON file
        def path_exists_side_effect(path):
            if path.endswith(".metadata/download") or path.endswith("title_pathname.json"):
                return True
            return False
        mock_path_exists.side_effect = path_exists_side_effect

        category = "TestCategory"
        filepath = "/test/path"
        inverse_filter = []

        result = get_title_pathname_map(category, filepath, inverse_filter, create=True)

        expected_result = {
            "pages": {"Page1": "Page1.html"},
            "categories": {"Category1": "Category1"},
        }

        self.assertEqual(result, expected_result)

    @patch("lib.wiki.index.helpers.os.path.exists")
    def test_get_title_pathname_map_file_not_exists_create_false(self, mock_path_exists):
        # Mock the os.path.exists method to return False
        mock_path_exists.return_value = False

        category = "TestCategory"
        filepath = "/test/path"
        inverse_filter = []

        with self.assertRaises(FileNotFoundError):
            get_title_pathname_map(category, filepath, inverse_filter, create=False)

    @patch("lib.wiki.index.helpers.os.path.exists")
    @patch("lib.wiki.index.helpers.os.makedirs")
    @patch("lib.wiki.index.helpers.open", new_callable=mock_open)
    @patch("lib.wiki.index.helpers.get_wiki_category_members")
    def test_get_title_pathname_map_file_not_exists_create_true(self, mock_get_wiki_category_members, mock_open, mock_makedirs, mock_path_exists):
        # Mock the os.path.exists method
        def path_exists_side_effect(path):
            if path.endswith("title_pathname.json"):
                return False
            return True
        mock_path_exists.side_effect = path_exists_side_effect

        # Mock the get_wiki_category_members function
        mock_get_wiki_category_members.return_value = [
            {"title": "Page1 title", "ns": 0},
            {"title": "Category1 title", "ns": 14},
        ]

        category = "TestCategory"
        filepath = "/test/path"
        inverse_filter = []

        result = get_title_pathname_map(category, filepath, inverse_filter, create=True)

        expected_result = {
            "pages": {"Page1 title": "Page1_title.html"},
            "categories": {"Category1 title": "Category1_title"},
        }

        self.assertEqual(result, expected_result)
        mock_get_wiki_category_members.assert_called_once_with(category, filepath)
        mock_open.assert_called_once_with(os.path.join(filepath, ".metadata/download", "title_pathname.json"), "w")

    @patch("lib.wiki.index.helpers.os.path.exists")
    @patch("lib.wiki.index.helpers.os.makedirs")
    @patch("lib.wiki.index.helpers.open", new_callable=mock_open)
    @patch("lib.wiki.index.helpers.get_wiki_category_members")
    def test_get_title_pathname_map_inverse_filter(self, mock_get_wiki_category_members, mock_open, mock_makedirs, mock_path_exists):
        # Mock the os.path.exists method
        def path_exists_side_effect(path):
            if path.endswith("title_pathname.json"):
                return False
            return True
        mock_path_exists.side_effect = path_exists_side_effect

        # Mock the get_wiki_category_members function
        mock_get_wiki_category_members.return_value = [
            {"title": "Page1", "ns": 0},
            {"title": "Birds of Prey", "ns": 0},
            {"title": "Category1", "ns": 14},
            {"title": "List of Birds", "ns": 14},
        ]

        category = "TestCategory"
        filepath = "/test/path"
        inverse_filter = ["birds", "list of"]

        result = get_title_pathname_map(category, filepath, inverse_filter, create=True)

        expected_result = {
            "pages": {"Page1": "Page1.html"},
            "categories": {"Category1": "Category1"},
        }

        self.assertEqual(result, expected_result)
        mock_get_wiki_category_members.assert_called_once_with(category, filepath)
        mock_open.assert_called_once_with(os.path.join(filepath, ".metadata/download", "title_pathname.json"), "w")


if __name__ == "__main__":
    unittest.main()
