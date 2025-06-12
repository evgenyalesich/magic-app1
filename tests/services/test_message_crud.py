# tests/services/test_message_crud.py

import pytest
from backend.services.crud import message_crud, user_crud
from backend.schemas.user import UserCreate
from backend.schemas.message import MessageCreate


@pytest.mark.asyncio
async def test_message_crud_create_get_update_remove(async_session_fixture):
    """
    MessageCreate у вас ожидает:
      - user_id: int
      - content: str
      - is_read: bool

    Поэтому сначала создаём “User”, затем записываем “Message” c user_id.
    """

    # 1) создаём временного пользователя, чтобы взять его ID
    user_in = UserCreate(username="charlie", telegram_id=444555)
    user = await user_crud.create(async_session_fixture, user_in)
    assert user.id is not None

    # 2) создаём сообщение, привязанное к user.id, с is_read=False
    msg_in = MessageCreate(user_id=user.id, content="Hello!", is_read=False)
    message = await message_crud.create(async_session_fixture, msg_in)
    assert message.id is not None
    assert message.content == "Hello!"
    assert message.is_read is False
    assert message.user_id == user.id

    # 3) получаем сообщение по ID
    fetched = await message_crud.get(async_session_fixture, message.id)
    assert fetched is not None
    assert fetched.content == "Hello!"
    assert fetched.user_id == user.id

    # 4) обновляем поле is_read → True
    updated = await message_crud.update(
        async_session_fixture, fetched, {"is_read": True}
    )
    assert updated.is_read is True

    # 5) удаляем сообщение
    removed = await message_crud.remove(async_session_fixture, updated)
    assert removed.id == message.id

    # 6) После удаления get(id) будет None
    assert await message_crud.get(async_session_fixture, message.id) is None
