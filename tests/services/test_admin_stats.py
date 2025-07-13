import pytest
from backend.services.crud import (
    count_users,
    count_orders,
    calculate_total_revenue,
    count_unread_messages,
)


@pytest.mark.asyncio
async def test_admin_helpers_return_zero(async_session_fixture):
    # Пустая БД, всё должно быть 0
    assert await count_users(async_session_fixture) == 0
    assert await count_orders(async_session_fixture) == 0
    assert await calculate_total_revenue(async_session_fixture) == 0.0
    assert await count_unread_messages(async_session_fixture) == 0
