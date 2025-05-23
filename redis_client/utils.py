from typing import Any
from pydantic import BaseModel

from redis_client import redis_client as client
from schema import ZRangeItem


async def hgetall(name: str, return_model: BaseModel | None) -> BaseModel | dict | None:
    try:
        item_dict = await client.hgetall(name=name)

        if not item_dict or len(item_dict) == 0:
            return None

        item_dict = {k.decode(): v.decode() for k, v in item_dict.items()}

        model = return_model or dict

        return model(**item_dict)

    except Exception as e:
        print(f"error occured at func: HGETALL: {e}")


async def hset(name: str, data: dict = None) -> None:
    try:
        if not data:
            raise ValueError("Data must not be None")
        if not isinstance(data, dict):
            raise ValueError("Data must be a mapping")

        await client.hset(name=name, mapping={**data})
    except Exception as e:
        print(f"error occured at func: HSET: {e}")


def get_zrange_item(item: Any):
    if isinstance(item, tuple):
        key, score = item
        return ZRangeItem(key=key.decode(), score=score)
    else:
        key = item.decode()
        return ZRangeItem(key=key, score=None)
