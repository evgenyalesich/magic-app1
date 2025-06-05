# tests/services/test_message_crud.py
import pytest
from backend.services.crud import message_crud
from backend.schemas.message import MessageCreate


@pytest.mark.asyncio
async def test_message_crud_create_get_update_remove(async_session_fixture):
    # 1) Создаём сообщение (например, без привязки к юзеру)
    msg_in = MessageCreate(user_id=None, content="Hello!", is_read=False)
    message = await message_crud.create(async_session_fixture, msg_in)
    assert message.id is not None
    assert message.content == "Hello!"
    assert not message.is_read

    # 2) Получаем по ID
    fetched = await message_crud.get(async_session_fixture, message.id)
    assert fetched is not None
    assert fetched.content == "Hello!"

    # 3) Обновляем поле is_read
    updated = await message_crud.update(
        async_session_fixture, fetched, {"is_read": True}
    )
    assert updated.is_read

    # 4) Удаляем сообщение
    removed = await message_crud.remove(async_session_fixture, updated)
    assert removed.id == message.id

    # 5) После удаления get возвращает None
    none_msg = await message_crud.get(async_session_fixture, message.id)
    assert none_msg is None
