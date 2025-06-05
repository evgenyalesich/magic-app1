# tests/services/test_product_crud.py

import pytest
from backend.services.crud import product_crud, category_crud
from backend.schemas.category import CategoryCreate
from backend.schemas.product import ProductCreate


@pytest.mark.asyncio
async def test_product_crud_create_get_update_remove(async_session_fixture):
    """
    ProductCreate у вас ожидает:
      - title: str
      - price: float
      - category_id: int
    Чтобы обойти внешние ключи, внутри теста сначала создаём “Category”,
    а затем уже создаём “Product” с этой category_id.
    """

    # 1) Сначала создаём запись в таблице categories (через category_crud)
    cat_in = CategoryCreate(name="TestCategory")
    category = await category_crud.create(async_session_fixture, cat_in)
    assert category.id is not None
    assert category.name == "TestCategory"

    # 2) Теперь создаём “Product” c обязательными полями title, price и category_id
    prod_in = ProductCreate(title="TestProduct", price=99.99, category_id=category.id)
    product = await product_crud.create(async_session_fixture, prod_in)
    assert product.id is not None
    assert product.title == "TestProduct"
    assert product.price == 99.99
    assert product.category_id == category.id

    # 3) Получаем продукт по ID
    fetched = await product_crud.get(async_session_fixture, product.id)
    assert fetched is not None
    assert fetched.title == "TestProduct"
    assert fetched.price == 99.99

    # 4) Обновляем некоторые поля (например, price и title)
    updated = await product_crud.update(
        async_session_fixture, fetched, {"price": 150.0, "title": "UpdatedProduct"}
    )
    assert updated.id == product.id
    assert updated.price == 150.0
    assert updated.title == "UpdatedProduct"

    # 5) Удаляем продукт
    removed = await product_crud.remove(async_session_fixture, updated)
    assert removed.id == product.id

    # 6) get(id) после удаления вернёт None
    none_prod = await product_crud.get(async_session_fixture, product.id)
    assert none_prod is None
