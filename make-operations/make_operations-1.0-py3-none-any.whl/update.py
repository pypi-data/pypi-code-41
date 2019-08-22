from fastapi import APIRouter
from models.users import users_table, User

router = APIRouter()


@router.put("/put_user/{user_id}")
def update_user(user_id: int, name: str, password: str, age: int):
    new_user = User(name=name, password=password, age=age)
    i = 1

    for user in users_table:
        if i == user_id:
            user = new_user
            return user
        i = i + 1
    return {"message": "not found"}

