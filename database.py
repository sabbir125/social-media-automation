from mongoengine import *
from datetime import datetime

DB_URI = "mongodb+srv://test:test@cluster0.nqwsp.mongodb.net/database?retryWrites=true&w=majority"
connect(host=DB_URI)


class Data(Document):
    username = StringField(required=True)
    link = StringField(required=True)
    createdAt = DateTimeField(default=datetime.utcnow)
    updatedAt = DateTimeField()
    type = IntField(required=True)

    def to_json(self):
        return {
            "username": self.username,
            "link": self.link,
            "type": self.type
        }


def model(username, link, _type):
    info = Data(username=username,
                link=link,
                type=_type
                )

    info.save()

# dele = Data.objects(username="sjkfk")
# dele.delete()

# info=Data.objects(username="Sabbizr")

#
# for i in Data.objects(username="Sabbi"):
#     print(i.to_json())


# dele.delete()

# order_by(): too sorting database

# info = Data(username="hello",
#             link="https://www.instagram.com/stories/parineetichopra/2546751603429228447/"
#             )
# info.save()


# meta = {"allow_inheritance": True}


# book = Collection.objects(name="Lord of the Rings").first()
# print(book.to_json())
