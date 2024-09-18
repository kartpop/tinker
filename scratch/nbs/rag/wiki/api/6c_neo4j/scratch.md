How to effectively handle storing Documents and creating graph in Neo4j?


Option 1
- WikiChunker outputs list of chunks (type Document) and a hierarchical tree (dict) of the Wikipedia article
- Indexing pipeline options
    - Option 1a
        - use haystack integration's Neo4jDocumentStore to first store document chunks
        - somehow invoke a custom component to create graph from hierarchial tree
    - Option 1b
        - use custom component which takes documents and hierarchial tree as inputs
        - wrap the above two functionalities inside it 
            - use Neo4jDocumentStore inside custom component to first store chunks
            - use hierarchial tree with custom cypher queries to create graph