import os

from dotenv import load_dotenv
from redis import asyncio as aioredis

load_dotenv()
redis_instance = aioredis.StrictRedis(
    host=str(os.environ.get("REDIS_HOST")),
    port=int(str(os.environ.get("REDIS_PORT"))),
    password=str(os.environ.get("REDIS_PASS")),
    db=0,
)
