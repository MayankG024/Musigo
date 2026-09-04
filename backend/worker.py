import os
import json
import asyncio
from rq import Queue
from redis import Redis

from rag_system.vector_store import vector_store
from api.core.config import settings


def _ensure_env_defaults():
    # Default Redis URL if not provided
    os.environ.setdefault("REDIS_URL", settings.REDIS_URL)


async def process_embedding(song_id: str, song_data_json: str):
    """Async processor to add a song to the vector store."""
    song_data = json.loads(song_data_json)
    await vector_store.add_song(song_id=song_id, song_data=song_data)


def enqueue_embedding(song_id: str, song_data: dict):
    """Enqueue an embedding job for RQ."""
    _ensure_env_defaults()
    redis = Redis.from_url(os.environ.get("REDIS_URL", settings.REDIS_URL))
    q = Queue("embeddings", connection=redis)
    # Serialize and run via asyncio in worker
    return q.enqueue(run_async, song_id, json.dumps(song_data))


def run_async(song_id: str, song_data_json: str):
    asyncio.run(process_embedding(song_id, song_data_json))


if __name__ == "__main__":
    _ensure_env_defaults()
    from rq import Worker
    conn = Redis.from_url(os.environ.get("REDIS_URL", settings.REDIS_URL))
    w = Worker(["embeddings"], connection=conn)
    w.work()