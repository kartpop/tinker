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

- Optimize wiki/api/lib/wiki_hierarchy.py. Some 'Match' clauses are working on generic node right now, but indexes are on specific node types - Category, Page, Section + Parent_id, Chunk_id etc...make use of these indexes to optimize the hierarchy builder query -- partially done
    - reindex everything in depth=1 data in order to include :FIRST_SECTION and :NEXT_SECTION relationships
        - cross-check if all functions in download, chunk, index are efficient (eg. do not unnecessarily write to file and read from file during same execution of function/method)
    - incorporate wiki_hierarchy_v2, possibly not much difference...
        - change implementation of get all sections in wiki_hierarchy_v2 to make use of new relationships...which will ensure proper order amongst sections as well...


 