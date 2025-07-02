Help me write a detailed clear markdown documentation for the repo attached. 

Instruction:
- First read the ai/README.md which gives a good overview of the two stage multi-hop RAG pipeline built
- The /ai/wiki/index/main.py and /ai/wiki/rag/main.py are the main entry points for indexing and retrieval stages respectively. Go through the code thoroughly including the /ai/lib which details how chunking and indexing is being done. 
- Go through both the /fe and /be - these are relatively small compared to ai/ --> they form the thin frontend and backend. 
- Frontend does have some logic related to how references are being showed and wikipedia urls are created based on data from backend. This gives the user direct references to wikipedia urls from where the answer has been picked up.
- document should be as detailed as possible; a new developer should quickly be able to know the workflows, should be able to navigate the codebase easily
- having worked on this project a while ago, this documentation should also act like a refresher for me to know all the important pieces and how they work
- explain all the workflows clearly
- for each workflow, explain how the chain of execution passes through different modules in the code
- IMPORTANT - Create an architecture and workflow diagram using mermaid for frontend, backend, ai modules. Be as detailed as possible especially for the ai/ module. Try to capture the RAG pipeline (Stage 1 and Stage 2) is as much detail  as possible.