from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from flask import current_app
from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
import certifi


_client: MongoClient | None = None


def _get_collection() -> Collection:
    """Return the `posts` collection, creating the MongoClient once per process."""
    global _client
    if _client is None:
        # Use certifi CA bundle to avoid local CA mismatch issues
        _client = MongoClient(
            current_app.config["MONGODB_URI"],
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=20000,
        )
    db = _client[current_app.config["MONGODB_DB"]]
    return db["posts"]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_all_posts() -> list[dict]:
    """Return all posts sorted newest-first."""
    col = _get_collection()
    return list(col.find({}).sort("created_at", DESCENDING))


def get_post_by_id(post_id: str) -> dict | None:
    """Return a single post document or None if not found / invalid id."""
    col = _get_collection()
    try:
        oid = ObjectId(post_id)
    except Exception:
        return None
    return col.find_one({"_id": oid})


def create_post(
    *,
    type: str,
    item_name: str,
    description: str,
    location: str,
    contact: str,
    image_url: str | None = None,
) -> str:
    """Insert a new post and return the inserted document id as a string."""
    col = _get_collection()
    doc = {
        "type": type,
        "item_name": item_name,
        "description": description,
        "location": location,
        "contact": contact,
        "image_url": image_url,
        "created_at": datetime.now(timezone.utc),
    }
    result = col.insert_one(doc)
    return str(result.inserted_id)
