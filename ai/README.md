

-----------------

### Tests

Run the following in the terminal from the root ```ai/``` directory:

```sh
python -m unittest discover -s tests -t .
```

-----------------

### Tips

- Run ```docker compose down -v``` when switching between different datasets (v100 and v3000). As the volume name is same (because a common docker-compose.yml is used), it first needs to be removed before plugging in a different device file path to the volume.