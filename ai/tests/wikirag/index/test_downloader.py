import unittest
from unittest.mock import patch, MagicMock
from wikirag.index.downloader import Downloader


class TestDownloader(unittest.TestCase):
    @patch("wikirag.index.downloader.os.path.exists")
    @patch("wikirag.index.downloader.os.makedirs")
    @patch("wikirag.index.downloader.get_title_pathname_map")
    @patch("wikirag.index.downloader.download_page")
    @patch("wikirag.index.downloader.redis.Redis")
    def test_fetch_wiki_data(
        self,
        mock_redis_class,
        mock_download_page,
        mock_get_title_pathname_map,
        mock_makedirs,
        mock_exists,
    ):
        # Setup mock responses and behavior
        mock_exists.return_value = False
        mock_get_title_pathname_map.side_effect = [
            {
                "pages": {"Page1": "page1.txt", "Page2": "page2.txt"},
                "categories": {"SubCategory1": "subcategory1"},
            },
            {
                "pages": {"SubPage1": "subpage1.txt"},
                "categories": {},
            },
        ]
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.sismember.side_effect = [False, False, False, False, False, False]

        logger = MagicMock()
        downloader = Downloader(logger, mock_redis_instance)
        category_pages_downloaded = {}
        num_pages_downloaded = downloader.fetch_wiki_data(
            "TestCategory", "/test/path", [], category_pages_downloaded, 0
        )

        # Assertions
        self.assertEqual(num_pages_downloaded, 3)
        self.assertEqual(category_pages_downloaded, {"TestCategory": 2, "SubCategory1": 1})
        mock_download_page.assert_any_call("Page1", "page1.txt", "/test/path")
        mock_download_page.assert_any_call("Page2", "page2.txt", "/test/path")
        mock_download_page.assert_any_call("SubPage1", "subpage1.txt", "/test/path/subcategory1")
        mock_redis_instance.sadd.assert_any_call("downloaded_pages", "Page1")
        mock_redis_instance.sadd.assert_any_call("downloaded_pages", "Page2")
        mock_redis_instance.sadd.assert_any_call("downloaded_pages", "SubPage1")
        mock_redis_instance.sadd.assert_any_call("downloaded_categories", "SubCategory1")


if __name__ == "__main__":
    unittest.main()
