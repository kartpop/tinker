from typing import List, Dict, Any
import uuid
from haystack import Document
from haystack import component
from lib.wiki.index.chunk.helpers import html_to_text_chunks


class Chunk:
    def __init__(self, id: str, next: str = None):
        self.id = id


class Section:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type
        self.chunks = []
        self.sections = []


class Page:
    def __init__(self, title: str):
        self.title = title
        self.sections = []
        self.chunks = []


@component
class WikiPageChunker:
    """
    A component that splits the content of Wikipedia pages into chunks.

    The document content is expected to be in HTML format fetched via wikipediaapi and
    which has been run through TextFileToDocument converter. Each chunk is a paragraph,
    list, or table in the Wikipedia page. Each chunk is stored as a separate document
    with text in the 'content' field. Each chunk also stores title, h2, h3, etc. in the
    meta field. This custom component also creates a hierarchical structure of the chunks
    based on title, h2, h3, etc.
    """

    @component.output_types(documents=List[Document], hierarchy=dict)
    def run(self, documents: List[Document]):
        """
        Chunks the content of Wikipedia pages and creates a hierarchical structure.
        
        Args:
            documents (List[Document]): List of documents with Wikipedia page content in HTML format.
            
        Returns:
            Dict[str, Any]: A dictionary containing the list of chunks and a hierarchical structure of the chunks
            
            Example:
            {
                "documents": [
                    Document(id="1", content="Chunk 1", meta={"file_path": "path", "source_id": "source", "split_id": 0, "title": "Page1", "h2": "Section1", "h3": "SubSection1"}),
                    Document(id="2", content="Chunk 2", meta={"file_path": "path", "source_id": "source", "split_id": 1, "title": "Page1", "h2": "Section1", "h3": "SubSection1"}),
                    ...
                ],
                "hierarchy": {
                    "Page1": {
                        "title": "Page1",
                        "sections": [
                            {
                                "name": "Section1",
                                "type": "h2",
                                "chunks": [...],
                                "sections": [
                                    {
                                        "name": "SubSection1",
                                        "type": "h3",
                                        "chunks": [...],
                                        "sections": [...]
                                    },
                                    ...
                                ]
                            },
                            ...
                        ],
                        "chunks": [...]
                    },
                    ...
                }
            }
            
        """
        chunks = []
        hierarchy = {}

        for doc in documents:
            page_title = doc.meta["page_title"]
            page = Page(page_title)

            html_content = doc.content
            page_chunks = html_to_text_chunks(html_content)
            i = 0
            current_h2 = ""
            current_h3 = ""
            current_h4 = ""
            current_section = None
            current_sub_section = None
            current_sub_sub_section = None

            for chunk in page_chunks:
                if chunk == "":
                    continue
                if chunk.startswith("<h2>"):
                    current_h2 = chunk[4:-5]  # Extract text between <h2> and </h2>
                    current_h3 = ""  # Reset h3 when a new h2 is found
                    current_h4 = ""  # Reset h4 when a new h2 is found
                    current_section = Section(current_h2, "h2")
                    page.sections.append(current_section)
                    current_sub_section = None
                    current_sub_sub_section = None
                elif chunk.startswith("<h3>"):
                    current_h3 = chunk[4:-5]  # Extract text between <h3> and </h3>
                    current_h4 = ""  # Reset h4 when a new h3 is found
                    if current_section:
                        current_sub_section = Section(current_h3, "h3")
                        current_section.sections.append(current_sub_section)
                        current_sub_sub_section = None
                elif chunk.startswith("<h4>"):
                    current_h4 = chunk[4:-5]  # Extract text between <h4> and </h4>
                    if current_sub_section:
                        current_sub_sub_section = Section(current_h4, "h4")
                        current_sub_section.sections.append(current_sub_sub_section)
                else:
                    meta = {
                        "file_path": doc.meta["file_path"],
                        "source_id": doc.id,
                        "split_id": i,
                        "title": page_title,
                    }
                    if current_h2:
                        meta["h2"] = current_h2
                    if current_h3:
                        meta["h3"] = current_h3
                    if current_h4:
                        meta["h4"] = current_h4

                    chunk_obj = Chunk(str(uuid.uuid4()))
                    chunks.append(Document(id=chunk_obj.id, content=chunk, meta=meta))
                    if current_sub_sub_section:
                        current_sub_sub_section.chunks.append(chunk_obj)
                    elif current_sub_section:
                        current_sub_section.chunks.append(chunk_obj)
                    elif current_section:
                        current_section.chunks.append(chunk_obj)
                    else:
                        page.chunks.append(chunk_obj)
                    i += 1

            hierarchy[page_title] = self.page_to_dict(page)

        return {"documents": chunks, "hierarchy": hierarchy}

    def page_to_dict(self, page: Page) -> Dict[str, Any]:
        return {
            "title": page.title,
            "sections": [self.section_to_dict(section) for section in page.sections],
            "chunks": [self.chunk_to_dict(chunk) for chunk in page.chunks],
        }

    def section_to_dict(self, section: Section) -> Dict[str, Any]:
        return {
            "name": section.name,
            "type": section.type,
            "chunks": [self.chunk_to_dict(chunk) for chunk in section.chunks],
            "sections": [
                self.section_to_dict(sub_section) for sub_section in section.sections
            ],
        }

    def chunk_to_dict(self, chunk: Chunk) -> Dict[str, Any]:
        return {
            "id": chunk.id,
        }
