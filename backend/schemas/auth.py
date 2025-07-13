# backend/schemas/auth.py

from pydantic import BaseModel, Field



class UserAuth(BaseModel):
    """Схема для объекта 'user' внутри initData."""
    id: int = Field(..., description="Уникальный идентификатор пользователя Telegram")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str | None = Field(None, description="Фамилия пользователя")
    username: str | None = Field(None, description="Юзернейм пользователя в Telegram")



class InitData(BaseModel):

    user: str = Field(..., description="Данные пользователя в формате JSON-строки")
    auth_date: int = Field(..., description="Время аутентификации в Unix-формате")
    hash: str = Field(..., description="Хэш для проверки подлинности данных")




class Token(BaseModel):
    """Схема для JWT токена доступа."""
    access_token: str
    token_type: str = "bearer"
