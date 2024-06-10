import logging
from enum import Enum
from typing import Annotated

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException

from socialmediaapi.database import comments_table, database, likes_table, post_table
from socialmediaapi.models.post import (
    Comment,
    CommentInt,
    PostLike,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
    UserPostWithLikes,
)
from socialmediaapi.models.users import User
from socialmediaapi.security import get_current_user
from socialmediaapi.utils import log

select_post_and_likes = (
    sqlalchemy.select(
        post_table, sqlalchemy.func.count(likes_table.c.id).label("likes")
    )
    .select_from(post_table.outerjoin(likes_table))
    .group_by(post_table.c.id)
)

router = APIRouter()

logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"


@router.get("/post", response_model=list[UserPostWithLikes])
@log(logger)
async def get_all_posts(sorting: PostSorting = PostSorting.new):
    logger.info("get_all_posts()")

    if sorting == PostSorting.new:
        query = select_post_and_likes.order_by(post_table.c.id.desc())
    elif sorting == PostSorting.old:
        query = select_post_and_likes.order_by(post_table.c.id.asc())
    elif sorting == PostSorting.most_likes:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))

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
async def get_post_with_comments(post_id: int):
    logger.debug("Getting post and its comments")
    query = select_post_and_likes.where(post_table.c.id == post_id)
    logger.debug(query)
    post = await database.fetch_one(query)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {post_id} not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }


@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(
    like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.debug("Liking a post.")
    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(
            status_code=404, detail=f"Post with id {like.post_id} not found"
        )

    data = {**like.model_dump(), "user_id": current_user.id}
    query = likes_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}
