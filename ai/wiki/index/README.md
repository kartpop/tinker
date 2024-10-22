# Wikipedia Category Indexer

This package prepares multiple retrieval indexes for a Wikipedia category (eg. Dinosaurs) to be used later in RAG (retrieval augmented generation). Specifically, it:
- Downloads the wiki pages belonging to the category
- Chunks the pages
- Stores and indexes the chunks in three databases:
    - ```Elasticsearch```: raw chunks are stored for fulltext search and retrieving chunks by id
    - ```Weaviate```: embeddings of the chunks are stored in the vector database
    - ```Neo4j```: hierarchy of the wiki category (category, subcategory, page, section, subsection, chunk) are stored as a graph


## Downloader

Downloads the wiki pages belonging to the category in HTML format using the ```wikipedia-api``` package


## Chunker

Chunks the pages (currently <p> and <li> tags are used as separators for chunking)
    ***Note***: Current implentation focusses on text data; tables, images and other data representation formats are not handled properly.

## Indexer

