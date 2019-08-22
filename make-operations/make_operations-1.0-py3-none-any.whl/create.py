from fastapi import FastAPI, APIRouter
from .users import users_table, User

router = APIRouter()


@router.post("/post_user")
def add_user(name: str, password: str, age: int):
    user = User(name=name, password=password, age=age)
    users_table.append(user)
    return users_table
