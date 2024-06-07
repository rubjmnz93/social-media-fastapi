from pydantic import BaseModel, ConfigDict


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CommentInt(BaseModel):
    body: str
    post_id: int


class Comment(CommentInt):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserPostWithComments(BaseModel):
    post: UserPost
    comments: list[Comment]
