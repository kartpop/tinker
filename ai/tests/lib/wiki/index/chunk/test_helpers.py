import unittest
from lib.wiki.index.chunk.helpers import html_to_text_chunks

class TestHtmlToTextChunks(unittest.TestCase):
    def test_generic(self):
        html_str = """
        <html>
            <body>
                <p>This is a paragraph.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
                <p>Another paragraph.</p>
            </body>
        </html>
        """
        expected_output = [
            "This is a paragraph.",
            "- Item 1",
            "- Item 2",
            "Another paragraph."
        ]
        self.assertEqual(html_to_text_chunks(html_str), expected_output)

    def test_clean_text_removes_spaces_between_digits(self):
        html_str = """
        <html>
            <body>
                <p>Number 1 234 567 should be 1234567.</p>
            </body>
        </html>
        """
        expected_output = [
            "Number 1234567 should be 1234567."
        ]
        self.assertEqual(html_to_text_chunks(html_str), expected_output)

    def test_empty_list_items_are_skipped(self):
        html_str = """
        <html>
            <body>
                <ul>
                    <li>Item 1</li>
                    <li></li>
                    <li>Item 2</li>
                </ul>
            </body>
        </html>
        """
        expected_output = [
            "- Item 1",
            "- Item 2"
        ]
        self.assertEqual(html_to_text_chunks(html_str), expected_output)

    def test_list_items_properly_formatted_with_prefix(self):
        html_str = """
        <html>
            <body>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
            </body>
        </html>
        """
        expected_output = [
            "- Item 1",
            "- Item 2"
        ]
        self.assertEqual(html_to_text_chunks(html_str), expected_output)

if __name__ == "__main__":
    unittest.main()