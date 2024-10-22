import unittest
from unittest.mock import patch, MagicMock
from wiki.index.chunker import Chunker
from pathlib import Path
@patch("wiki.index.chunker.Path.glob")
@patch("wiki.index.chunker.Path.iterdir")
class TestChunker(unittest.TestCase):
    @patch("wiki.index.chunker.os.path.exists")
    @patch("wiki.index.chunker.os.makedirs")
    @patch("wiki.index.chunker.get_title_pathname_map")
    @patch("wiki.index.chunker.Chunker.chunk_page")
    @patch("wiki.index.chunker.redis.Redis")
    def test_chunk_wiki_data(
        self,
        mock_redis_class,
        mock_chunk_page,
        mock_get_title_pathname_map,
        mock_makedirs,
        mock_exists,
        mock_iterdir,
        mock_glob
    ):
        # Setup mock responses and behavior
        mock_exists.return_value = True
        mock_get_title_pathname_map.side_effect = [
            {
                "pages": {"Page1": "page1.html", "Page2": "page2.html"},
                "categories": {"SubCategory1": "subcategory1"},
            },
            {
                "pages": {},
                "categories": {},
            },
        ]
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.sismember.side_effect = [
            False,
            False,
            False,
            False,
            False,
            False,
        ]

        mock_page1 = MagicMock(spec=Path)
        mock_page1.name = "page1.html"
        mock_page2 = MagicMock(spec=Path)
        mock_page2.name = "page2.html"
        mock_glob.return_value = [mock_page1, mock_page2]

        mock_subcategory = MagicMock(spec=Path)
        mock_subcategory.name = "subcategory1"
        mock_subcategory.is_dir.return_value = True
        mock_iterdir.return_value = [mock_subcategory]

        logger = MagicMock()
        chunker = Chunker(logger, mock_redis_instance)
        category_pages_chunked = {}
        num_pages_chunked = chunker.chunk_wiki_data(
            "TestCategory", "/test/path", category_pages_chunked
        )

        # Assertions
        self.assertEqual(num_pages_chunked, 2)
        self.assertEqual(category_pages_chunked, {"TestCategory": 2})
        mock_chunk_page.assert_any_call("/test/path", "Page1", "page1.html")
        mock_chunk_page.assert_any_call("/test/path", "Page2", "page2.html")
        mock_redis_instance.sadd.assert_any_call("chunked_pages", "Page1")
        mock_redis_instance.sadd.assert_any_call("chunked_pages", "Page2")
        mock_redis_instance.sadd.assert_any_call("chunked_categories", "SubCategory1")


if __name__ == "__main__":
    unittest.main()
