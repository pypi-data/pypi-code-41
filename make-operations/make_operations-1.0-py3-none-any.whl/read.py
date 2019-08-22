from fastapi import APIRouter
from models.users import users_table

router = APIRouter()


@router.get("/get_user/{user_id}")
def read_user(user_id: int):
    i = 1

    for user in users_table:
        if i == user_id:
            return user
        i = i + 1
    return {"message": "not found"}


@router.get("/get_user/")
def read_user():
    return users_table
