# AI
RAG, Agents etc.

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
python wikirag/index/main.py
```

- ***RAG server***: Run the following from project root for starting the RAG API server:

```sh
fastapi dev wikirag/rag/main.py
```

Or 

```sh
fastapi run wikirag/rag/main.py
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
