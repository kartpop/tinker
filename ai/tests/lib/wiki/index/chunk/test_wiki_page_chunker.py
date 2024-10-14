import unittest
from haystack import Document
from lib.wiki.index.chunk.wiki_page_chunker import WikiPageChunker


class TestWikiPageChunker(unittest.TestCase):
    def test_wiki_page_chunker(self):
        # Sample HTML content with h2, h3, and paragraphs
        html_content = """
        <h2>Section 1</h2>
        <p>Paragraph 1 in Section 1.</p>
        <h3>Subsection 1.1</h3>
        <p>Paragraph 1 in Subsection 1.1.</p>
        <p>Paragraph 2 in Subsection 1.1.</p>
        <h2>Section 2</h2>
        <p>Paragraph 1 in Section 2.</p>
        """

        # Create a sample Document
        doc = Document(
            id="1",
            content=html_content,
            meta={"page_title": "Sample Page", "file_path": "/path/to/file"},
        )

        # Initialize the WikiPageChunker component
        chunker = WikiPageChunker()

        # Run the chunker on the sample document
        result = chunker.run([doc])

        # Extract the documents and hierarchy from the result
        documents = result["documents"]
        hierarchy = result["hierarchy"]

        # Assertions to verify the chunking and hierarchy
        self.assertEqual(len(documents), 4)
        self.assertEqual(documents[0].content, "Paragraph 1 in Section 1.")
        self.assertEqual(documents[1].content, "Paragraph 1 in Subsection 1.1.")
        self.assertEqual(documents[2].content, "Paragraph 2 in Subsection 1.1.")
        self.assertEqual(documents[3].content, "Paragraph 1 in Section 2.")

        self.assertIn("Sample Page", hierarchy)
        self.assertEqual(hierarchy["Sample Page"]["title"], "Sample Page")
        self.assertEqual(len(hierarchy["Sample Page"]["sections"]), 2)

        section_1 = hierarchy["Sample Page"]["sections"][0]
        self.assertEqual(section_1["name"], "Section 1")
        self.assertEqual(section_1["type"], "h2")
        self.assertEqual(len(section_1["chunks"]), 1)
        self.assertEqual(len(section_1["sections"]), 1)

        subsection_1_1 = section_1["sections"][0]
        self.assertEqual(subsection_1_1["name"], "Subsection 1.1")
        self.assertEqual(subsection_1_1["type"], "h3")
        self.assertEqual(len(subsection_1_1["chunks"]), 2)

        section_2 = hierarchy["Sample Page"]["sections"][1]
        self.assertEqual(section_2["name"], "Section 2")
        self.assertEqual(section_2["type"], "h2")
        self.assertEqual(len(section_2["chunks"]), 1)


if __name__ == "__main__":
    unittest.main()
