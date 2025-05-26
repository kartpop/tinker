# AI
RAG, Agents etc.

## Wikipedia RAG

This project details the creation of an advanced system for retrieving information and answering questions, specifically tailored to process and understand the extensive content related to "Dinosaurs" on Wikipedia. The system handles a large dataset of approximately 3,800 Wikipedia pages, carefully excluding content related to "birds" to maintain domain specificity.

Data Ingestion and Multi-Faceted Indexing:

The foundation of the system is a robust data processing pipeline. It begins by automatically downloading the relevant Wikipedia pages. This content is then intelligently broken down into smaller, paragraph-level segments. A key architectural feature is the use of three distinct database technologies for indexing these segments, each serving a specialized role:

A full-text search database (like Elasticsearch) is used to store the raw text segments, enabling fast keyword-based searches and direct content access.
A vector database (like Weaviate) stores numerical representations (embeddings) of these text segments. These embeddings capture the semantic meaning, allowing the system to find content that is conceptually similar to a query, even if the exact keywords don't match.
A graph database (like Neo4j) is employed to build and maintain a detailed hierarchical model of the Wikipedia content. This model represents the relationships between categories, pages, sections (H2, H3, H4 headings), and individual text segments, effectively mapping out the structural organization of the information.
Two-Stage Retrieval Augmented Generation (RAG) for Question Answering:

When a user asks a question, the system initiates a sophisticated two-stage process to generate an answer.

Stage 1: Hybrid Initial Retrieval and Answer Generation: The first stage focuses on quickly identifying potentially relevant information.

The user's question is processed in two ways:
It's converted into a semantic embedding to search the vector database for conceptually similar text segments.
It's used directly for a keyword-based search in the full-text search database.
The results from both semantic and keyword searches are then combined and re-ranked (using a technique like reciprocal rank fusion) to produce a consolidated list of the most relevant initial text segments (chunks).
These retrieved segments are then presented as context to a large language model (LLM). The LLM attempts to answer the user's question based on this initial context. Crucially, the LLM is also tasked to determine if the provided context is sufficient for a comprehensive answer or if more information is needed. This determination is often guided by a predefined output structure that the LLM must follow, which includes a flag indicating the need for more context.
Transition to Stage 2: The system transitions to the second stage if the LLM in Stage 1 indicates that the initial context is insufficient to provide a complete or accurate answer. The text segments retrieved in Stage 1 serve as the starting point for this deeper exploration.

Stage 2: Graph-Powered Context Expansion and Refined Answer Generation: This stage leverages the graph database to build a much richer and more targeted context.

Hierarchy Reconstruction: Using the document chunks identified in Stage 1, the system queries the graph database. For each page associated with these initial chunks, it reconstructs the full hierarchical structure of that Wikipedia page (e.g., Page Title -> Section 1 -> Subsection 1.1 -> Sub-subsection 1.1.1). This process involves traversing relationships in the graph that define how sections are ordered and nested.
Intelligent Path Prediction: The reconstructed page hierarchies, along with the original user question, are then presented to another LLM. This LLM's task is to predict the most probable path(s) within these hierarchies that are likely to contain the specific information needed to answer the question. For example, it might predict a path like "Dinosaur > Paleobiology > Diet."
Targeted Context Creation: Based on the path(s) predicted by the LLM, the system navigates the detailed chunk hierarchies (which link specific text chunks to their respective sections/subsections in the graph). It then retrieves all the text chunks belonging to these identified hierarchical paths from the full-text search database. This content is then assembled, preserving its structural order, to create a highly relevant and comprehensive block of text.
Final Answer Synthesis: This newly assembled, rich contextual information is fed to a final LLM instance. With this expanded and targeted context, the LLM generates a more detailed, accurate, and comprehensive answer to the user's original question.
The system is designed to provide not just an answer but also references, linking back to the specific sections of the Wikipedia pages from which the information was derived. This is achieved by tracking the metadata (like page title and section headings) associated with the text segments used in generating the final answer. The entire process, including the conditional execution of the second stage and interactions with multiple LLMs and databases, is orchestrated to ensure an efficient and effective information retrieval and question-answering experience.

## Setup

### Set configs and envs

Update the following files before running:
- ```.env```: Copy the ```.env.sample``` in the root directory itself and rename it to ```.env```. Set the credentials for the databases.
- ```config.yml```: Set the required configurations.
- ```docker-compose.databases.yml```: All database volumes are bind mount that map the host directory into the container. Set the filepath for each database in the ```volumes.<database>.driver.device```.


### Databases

To start Redis, Weaviate, Elasticsearch, Neo4j in Docker, run the following in the terminal from the root ```ai/``` directory:

```sh
docker compose -f docker-compose.databases.yml up -d
```

Stop databases:

```sh
docker compose -f docker-compose.databases.yml down
```

***Tip***
- Run ```docker compose -f docker-compose.databases.yml down -v``` when switching between different datasets (v100 and v3000). As the volume name is same (because a common docker-compose file is used), the volume first needs to be removed before plugging in a different device file path to it.


### Run

- ***Indexing***: Run the following from project root for downloading, chunking and indexing the wikipedia category data:

```sh
python wiki/index/main.py
```

- ***RAG server***: Run the following from project root for starting the RAG API server:

```sh
fastapi dev wiki/rag/main.py
```

Or 

```sh
fastapi run wiki/rag/main.py
```




## Tests

Run the following in the terminal from the root ```ai/``` directory:

```sh
python -m unittest discover -s tests -t .
```

Or run with ```- v``` for verbose output:

```sh
python -m unittest discover -s tests -t . -v
```
