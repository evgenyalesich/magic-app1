# tests/services/test_order_crud.py

import pytest
from backend.services.crud import order_crud, user_crud, product_crud, category_crud
from backend.schemas.user import UserCreate
from backend.schemas.category import CategoryCreate
from backend.schemas.product import ProductCreate
from backend.schemas.order import OrderCreate


@pytest.mark.asyncio
async def test_order_crud_full_cycle(async_session_fixture):
    """
    OrderCreate у вас ожидает:
      - user_id: int
      - product_id: int
      - quantity: int
      - price: float

    Поэтому внутри теста:
     1) Сначала создаём “User”.
     2) Затем “Category” → “Product”.
     3) Наконец, “Order”, ссылаясь на user.id и product.id.
    """

    # 1) создаём пользователя (telegram_id — целое число)
    user_in = UserCreate(username="bob", telegram_id=222333)
    user = await user_crud.create(async_session_fixture, user_in)
    assert user.id is not None

    # 2) создаём категорию и продукт (нужно из-за внешнего ключа category_id у Product)
    cat_in = CategoryCreate(name="OrderCategory")
    category = await category_crud.create(async_session_fixture, cat_in)
    assert category.id is not None

    prod_in = ProductCreate(title="OrderProduct", price=20.0, category_id=category.id)
    product = await product_crud.create(async_session_fixture, prod_in)
    assert product.id is not None

    # 3) создаём заказ через Pydantic OrderCreate
    order_in = OrderCreate(
        user_id=user.id, product_id=product.id, quantity=2, price=20.0
    )
    order = await order_crud.create(async_session_fixture, order_in)
    assert order.id is not None
    assert order.user_id == user.id
    assert order.product_id == product.id
    assert order.quantity == 2

    # 4) проверяем, что get_multi() вернёт наш заказ
    all_orders = await order_crud.get_multi(async_session_fixture)
    assert any(o.id == order.id for o in all_orders)

    # 5) получаем заказ по его ID и проверяем поля
    fetched = await order_crud.get(async_session_fixture, order.id)
    assert fetched is not None
    assert fetched.quantity == 2

    # 6) обновляем какое-либо поле (например, quantity)
    updated = await order_crud.update(async_session_fixture, fetched, {"quantity": 3})
    assert updated.quantity == 3

    # 7) удаляем заказ
    removed = await order_crud.remove(async_session_fixture, updated)
    assert removed.id == order.id

    # 8) get(id) после удаления снова вернёт None
    assert await order_crud.get(async_session_fixture, order.id) is None
