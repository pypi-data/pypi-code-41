from mongoengine import *


class Request(Document):
    method = StringField(max_length=10, required=True)
    url = URLField(required=True)
    headers = ListField(
        ListField(
            StringField(),
            max_length=2
        ),
        max_length=30, required=True
    )
    cookies = DynamicField()
    remote_addr = StringField(max_length=20, required=True)
    # json = StringField()


class Response(Document):
    status_code = IntField()
    headers = ListField(ListField(StringField(), max_length=2), max_length=30)


class Session(Document):
    id = LongField()
    request = ReferenceField(Request)
    response = ReferenceField(Response)
