



-----------------

### Databases

To start Redis, Weaviate, Elasticsearch, Neo4j in Docker, run the following in the terminal from the root ```ai/``` directory:

```sh
docker compose -f docker-compose.databases.yml up -d
```

***Tip***
- Run ```docker compose down -v``` when switching between different datasets (v100 and v3000). As the volume name is same (because a common docker-compose.yml is used), the volume first needs to be removed before plugging in a different device file path to it.

-----------------

### Tests

Run the following in the terminal from the root ```ai/``` directory:

```sh
python -m unittest discover -s tests -t .
```

Or run with ```- v``` for verbose output:

```sh
python -m unittest discover -s tests -t . -v
```