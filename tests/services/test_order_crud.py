import pytest
from backend.services import crud
from backend.schemas.category import CategoryCreate
from backend.schemas.product import ProductCreate


@pytest.mark.asyncio
async def test_order_crud_full_cycle(async_session_fixture):
    # 1) Создаём категорию и продукт
    cat = await crud.category_crud.create(
        async_session_fixture, CategoryCreate(name="CatForOrder")
    )
    prod = await crud.product_crud.create(
        async_session_fixture,
        ProductCreate(name="OrderProd", price=100.0, category_id=cat.id),
    )

    # 2) Создаём заказ (достаточно передать user_id=None, product_id, quantity и price;
    #    можно положить user_id как 0 или любой другой, если в модели nullable)
    order_data = {
        "user_id": None,
        "product_id": prod.id,
        "quantity": 2,
        "price": 100.0,
    }
    order = await crud.order_crud.create(async_session_fixture, order_data)
    assert order.id is not None
    assert order.product_id == prod.id
    assert order.quantity == 2

    # 3) Получаем все заказы (get_multi) и проверяем, что созданный заказ в списке
    orders = await crud.order_crud.get_multi(async_session_fixture)
    assert any(o.id == order.id for o in orders)

    # 4) Обновляем количество
    fetched = await crud.order_crud.get(async_session_fixture, order.id)
    updated = await crud.order_crud.update(
        async_session_fixture, fetched, {"quantity": 3}
    )
    assert updated.quantity == 3

    # 5) Удаляем заказ
    removed = await crud.order_crud.remove(async_session_fixture, updated)
    assert removed.id == order.id

    # 6) Убедимся, что get возвращает None
    no_order = await crud.order_crud.get(async_session_fixture, order.id)
    assert no_order is None
