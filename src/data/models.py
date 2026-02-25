import logging
from datetime import datetime
from mongoengine import (
    connect, Document, StringField, IntField, ListField, DateTimeField,
)
from src.config import MONGO_URI

logger = logging.getLogger(__name__)

connect(host=MONGO_URI)


class ScrapedData(Document):
    """Stores a single scraped link (story or post) for a target username."""

    STORY = 1
    POST = 2

    username = StringField(required=True)
    link = StringField(required=True, unique=True)
    content_type = IntField(required=True, choices=[STORY, POST])
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "scraped_data",
        "indexes": ["username", "link"],
    }

    def to_dict(self):
        return {
            "username": self.username,
            "link": self.link,
            "content_type": self.content_type,
        }


class LastLink(Document):
    """Tracks the last scraped story URL per username to resume from where we left off."""

    username = StringField(required=True, unique=True)
    last_story_link = StringField(required=True)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "last_links", "indexes": ["username"]}


class SessionCookies(Document):
    """Persists browser session cookies per Instagram account to avoid repeated logins."""

    acc_username = StringField(required=True, unique=True)
    cookies = ListField()
    saved_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "session_cookies", "indexes": ["acc_username"]}


# --- Repository helpers ---

def save_scraped_link(username: str, link: str, content_type: int) -> bool:
    """Saves a scraped link. Returns False if it already exists."""
    if ScrapedData.objects(link=link).first():
        logger.debug("Already in DB, skipping: %s", link)
        return False
    ScrapedData(username=username, link=link, content_type=content_type).save()
    logger.info("Saved [%s] %s", "story" if content_type == ScrapedData.STORY else "post", link)
    return True


def upsert_last_link(username: str, last_link: str):
    """Creates or updates the last story link for a username."""
    LastLink.objects(username=username).update_one(
        set__last_story_link=last_link,
        set__updated_at=datetime.utcnow(),
        upsert=True,
    )


def save_session_cookies(acc_username: str, cookies: list):
    """Creates or replaces session cookies for an account."""
    SessionCookies.objects(acc_username=acc_username).update_one(
        set__cookies=cookies,
        set__saved_at=datetime.utcnow(),
        upsert=True,
    )
