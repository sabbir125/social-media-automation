from mongoengine import *
from datetime import datetime
from src.config import DB_URI

connect(host=DB_URI)


class Data(Document):
    username = StringField(required=True)
    link = StringField(required=True)
    type = IntField(required=True)  # 1 = story, 2 = post
    createdAt = DateTimeField(default=datetime.utcnow)
    updatedAt = DateTimeField()

    def to_json(self):
        return {"username": self.username, "link": self.link, "type": self.type}


class LastLink(Document):
    username = StringField(required=True)
    lastStory_link = StringField(required=True)


class Cookies(Document):
    acc_username = StringField(required=True)
    cookies = ListField()


def save_scraped_data(username, link, _type):
    Data(username=username, link=link, type=_type).save()


def save_last_link(username, last_link):
    LastLink(username=username, lastStory_link=last_link).save()


def save_cookies(acc_username, cookies):
    Cookies(acc_username=acc_username, cookies=cookies).save()
