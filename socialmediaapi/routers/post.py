from fastapi import APIRouter

from socialmediaapi.models.post import UserPost, UserPostIn

router = APIRouter()


post_table = {}


@router.get("/post", response_model=list[UserPost])
async def root():
    return list(post_table.values())


@router.post("/post", response_model=UserPost)
async def create_post(post: UserPostIn):
    data = post.model_dump()
    last_record_id = len(post_table)
    new_post = {**data, "id": last_record_id}
    post_table[last_record_id] = new_post
    return new_post
