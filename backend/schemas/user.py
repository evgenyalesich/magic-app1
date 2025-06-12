from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int
    username: str | None = None


class UserCreate(BaseModel):
    username: str
    telegram_id: int

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    id: int
    telegram_id: int
    username: str
    is_admin: bool

    class Config:
        orm_mode = True
        from_attributes = True
