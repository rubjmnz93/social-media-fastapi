import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from socialmediaapi.database import comments_table, database, post_table
from socialmediaapi.models.post import (
    Comment,
    CommentInt,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)
from socialmediaapi.models.users import User
from socialmediaapi.security import get_current_user
from socialmediaapi.utils import log

router = APIRouter()

logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


@router.get("/post", response_model=list[UserPost])
@log(logger)
async def get_all_posts():
    logger.info("get_all_posts()")
    query = post_table.select()

    logger.debug(query)

    return await database.fetch_all(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info("Creating post")

    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentInt, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.debug("Creating a comment.")
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(
            status_code=404, detail=f"Post with id {comment.post_id} not found"
        )

    data = {**comment.model_dump(), "user_id": current_user.id}
    query = comments_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comment", response_model=list[Comment])
@log(logger)
async def get_comments_on_post(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {post_id} not found")

    query = comments_table.select().where(comments_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
@log(logger)
async def get_post_with_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id={post_id} not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
