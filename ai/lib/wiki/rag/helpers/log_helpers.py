import json

import aiofiles
from haystack import Document


def strip_embeddings_from_dict(data: dict):
    """
    Strips embeddings from a dictionary.

    Embeddings are not useful information to log, and can be very large.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key in ["embedding", "embeddings"]:
                data[key] = []
            else:
                strip_embeddings_from_dict(value)
    elif isinstance(data, list):
        for item in data:
            strip_embeddings_from_dict(item)
    return data


def custom_serializer(obj):
    if isinstance(obj, Document):
        return strip_embeddings_from_dict(obj.to_dict())
    try:
        # Try to use the default serializer
        return json.JSONEncoder().default(obj)
    except TypeError:
        # If the object is not serializable, return a custom dictionary
        return {"type_of_obj": str(type(obj)), "raw_string": str(obj)}


async def log_dict_as_json(log_filename, data):
    """
    Logs a dictionary as a JSON string asynchronously.
    """
    strip_embeddings_from_dict(data)

    async with aiofiles.open(log_filename, "w") as file:
        await file.write(json.dumps(data, default=custom_serializer, indent=4))
