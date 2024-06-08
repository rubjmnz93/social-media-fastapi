import logging

from fastapi import APIRouter, HTTPException, status

from socialmediaapi.database import database, users_table
from socialmediaapi.models.users import UserIn
from socialmediaapi.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists.",
        )
    query = users_table.insert().values(
        email=user.email, password=get_password_hash(user.password)
    )
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User created."}


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}
