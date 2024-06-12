import logging

from fastapi import APIRouter, HTTPException, Request, status

from socialmediaapi.database import database, users_table
from socialmediaapi.models.users import UserIn
from socialmediaapi.security import (
    authenticate_user,
    create_access_token,
    create_confirmation_token,
    get_password_hash,
    get_subject_for_token_type,
    get_user,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn, request: Request):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists.",
        )
    query = users_table.insert().values(
        email=user.email,
        password=get_password_hash(user.password),
        confirmed=user.confirmed,
    )
    logger.debug(query)
    await database.execute(query)
    return {
        "detail": "User created. Please confirm your email",
        "confirmation_url": request.url_for(
            "confirm_email", token=create_confirmation_token(user.email)
        ),
    }


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    logger.debug("Confirming email")
    email = get_subject_for_token_type(token, "confirmation")
    query = (
        users_table.update().where(users_table.c.email == email).values(confirmed=True)
    )
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User confirmed"}
