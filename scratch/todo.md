# Frontend
- custom scrollbar 
- change background theme from orange to white/transparent, keep orange highlights


# AI
- https://huggingface.co/datasets/bigdata-pw/Dinosaurs - source for structured dinosaur data

### Indexing pipeline
- Create embedder with metadata_fields_to_embed


---------------------------------------

### Adhoc tasks
- chunking experiments: lists, tables etc. (abandoned for later)
- get references marked from LLM during question/answering
    - fix the hierarchy path returned by phase 2
        - Instead of ["Dinosaur", "Paloebiology"], get more granular { "page_title": "Dinosaurs", "h2": "Paleobiology"}
            - Multiple components and their interface might need to change
        - Optimize wiki/api/lib/wiki_hierarchy.py. Some 'Match' clauses are working on generic node right now, but indexes are on specific node types - Category, Page, Section + Parent_id, Chunk_id etc...make use of these indexes to optimize the hierarchy builder query
 