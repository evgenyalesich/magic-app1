import pytest
from backend.services import crud
from backend.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_user_crud_create_get_update_remove(async_session_fixture):
    #  Создаём пользователя
    data = UserCreate(username="testuser", telegram_id="tg_123")
    user = await crud.user_crud.create(async_session_fixture, data)
    assert user.id is not None
    assert user.username == "testuser"
    assert user.telegram_id == "tg_123"

    # Получаем ID
    fetched = await crud.user_crud.get(async_session_fixture, user.id)
    assert fetched is not None
    assert fetched.username == "testuser"
    assert fetched.telegram_id == "tg_123"

    #  Обновляем username
    updated = await crud.user_crud.update(
        async_session_fixture, fetched, {"username": "new_name"}
    )
    assert updated.username == "new_name"
    assert updated.telegram_id == "tg_123"

    #  Удаляем пользователя
    removed = await crud.user_crud.remove(async_session_fixture, updated)
    assert removed.id == user.id

    # Повторный get для удалённого пользователя  None
    no_user = await crud.user_crud.get(async_session_fixture, user.id)
    assert no_user is None
