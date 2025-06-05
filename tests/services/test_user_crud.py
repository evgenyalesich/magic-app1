# tests/services/test_user_crud.py

import pytest
from backend.services.crud import user_crud
from backend.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_user_crud_create_get_update_remove(async_session_fixture):
    """
    UserCreate у вас ожидает:
      - telegram_id: int
      - username: str
    Поэтому передаём telegram_id как целое, а не как строку.
    """

    # 1) Создаём пользователя
    user_in = UserCreate(username="alice", telegram_id=123456)
    user = await user_crud.create(async_session_fixture, user_in)
    assert user.id is not None
    assert user.username == "alice"
    assert user.telegram_id == 123456

    # 2) Получаем пользователя по его ID
    fetched = await user_crud.get(async_session_fixture, user.id)
    assert fetched is not None
    assert fetched.username == "alice"
    assert fetched.telegram_id == 123456

    # 3) Обновляем username (оставляем telegram_id без изменений)
    updated = await user_crud.update(
        async_session_fixture, fetched, {"username": "alice_new"}
    )
    assert updated.id == user.id
    assert updated.username == "alice_new"
    assert updated.telegram_id == 123456

    # 4) Удаляем пользователя
    removed = await user_crud.remove(async_session_fixture, updated)
    assert removed.id == user.id

    # 5) Теперь get(id) должен вернуть None, потому что мы его удалили
    none_user = await user_crud.get(async_session_fixture, user.id)
    assert none_user is None
