from pydantic import BaseModel


class User(BaseModel):
    name: str
    password: str
    age: int

users_table = []
