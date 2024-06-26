import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from socialmediaapi import tasks
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
async def register(user: UserIn, background_task: BackgroundTasks, request: Request):
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
    background_task.add_task(
        tasks.send_user_registration_email,
        user.email,
        confirmation_url=request.url_for(
            "confirm_email", token=create_confirmation_token(user.email)
        ),
    )
    return {"detail": "User created"}


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username, form_data.password)
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
