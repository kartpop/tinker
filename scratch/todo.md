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
- create Dinosaur category/page directory with 1 sub-directory level (done)
- create integrated download + indexing pipeline 
    - figure out strategy for checkpointing download/indexing pages or categories (redis?) (partial) 
        - checkpointing done at directory level, pages fetched and downloaded (done)
        - indexing pipeline (not done)
- get references marked from LLM during question/answering
 