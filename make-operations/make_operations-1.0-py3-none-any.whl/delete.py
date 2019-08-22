from fastapi import APIRouter
from models.users import users_table

router = APIRouter()


@router.delete("/delete_user/{user_id}")
def delete_user(user_id: int):

    i = 1

    for user in users_table:
        if i == user_id:
            users_table.remove(user)
            return users_table
        i = i + 1

    return {"message": "not found"}
