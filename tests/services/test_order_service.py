import pytest
from backend.services import crud


@pytest.mark.asyncio
async def test_get_nonexistent_user(async_session_fixture):
    user = await crud.user_crud.get(async_session_fixture, id=-1)
    assert user is None


@pytest.mark.asyncio
async def test_admin_helpers_return_zero(async_session_fixture):
    assert await crud.count_users(async_session_fixture) == 0
    assert await crud.count_orders(async_session_fixture) == 0
    assert await crud.calculate_total_revenue(async_session_fixture) == 0.0
    assert await crud.count_unread_messages(async_session_fixture) == 0


@pytest.mark.asyncio
async def test_admin_helpers_non_negative(async_session_fixture):
    """функции count_* возвращают неотрицательные числа / float."""
    cu = await crud.count_users(async_session_fixture)
    co = await crud.count_orders(async_session_fixture)
    cr = await crud.calculate_total_revenue(async_session_fixture)
    cm = await crud.count_unread_messages(async_session_fixture)
    assert isinstance(cu, int) and cu >= 0
    assert isinstance(co, int) and co >= 0
    assert isinstance(cr, float) and cr >= 0.0
    assert isinstance(cm, int) and cm >= 0
