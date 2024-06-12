from pydantic import BaseModel, Field


class User(BaseModel):
    id: int | None = None
    email: str
    confirmed: bool = Field(default=False)


class UserIn(User):
    password: str
