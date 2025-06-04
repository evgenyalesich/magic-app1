import pytest
from backend.services import crud


@pytest.mark.asyncio
async def test_get_nonexistent_user(async_session_fixture):
    user = await crud.user_crud.get(async_session_fixture, id=-1)
    assert user is None
