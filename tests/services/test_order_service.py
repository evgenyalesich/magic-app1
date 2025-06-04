import asyncio
from backend.core.database import async_session
from backend.services import crud


def test_get_nonexistent_user():
    async def run_test():
        async with async_session() as session:
            user = await crud.user_crud.get(session, id=-1)
            assert user is None

    asyncio.run(run_test())


def test_admin_helpers_return_zero():
    async def run_test():
        async with async_session() as session:
            assert await crud.count_users(session) == 0
            assert await crud.count_orders(session) == 0
            assert await crud.calculate_total_revenue(session) == 0.0
            assert await crud.count_unread_messages(session) == 0

    asyncio.run(run_test())
