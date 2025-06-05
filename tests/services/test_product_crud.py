import pytest
from backend.services import crud
from backend.services.crud import CategoryCreate
from backend.schemas.product import ProductCreate


@pytest.mark.asyncio
async def test_product_crud_create_get_update_remove(async_session_fixture):
    # 1) Сначала нужна категория
    cat_data = CategoryCreate(name="ProdCat")
    category = await crud.category_crud.create(async_session_fixture, cat_data)

    # 2) Создаём продукт в этой категории
    prod_data = ProductCreate(name="TestProd", price=50.0, category_id=category.id)
    product = await crud.product_crud.create(async_session_fixture, prod_data)
    assert product.id is not None
    assert product.name == "TestProd"
    assert product.price == 50.0
    assert product.category_id == category.id

    # 3) Получаем продукт по ID
    fetched = await crud.product_crud.get(async_session_fixture, product.id)
    assert fetched is not None
    assert fetched.name == "TestProd"
    assert fetched.price == 50.0

    # 4) Обновляем цену
    updated = await crud.product_crud.update(
        async_session_fixture, fetched, {"price": 75.0}
    )
    assert updated.price == 75.0

    # 5) Удаляем продукт
    removed = await crud.product_crud.remove(async_session_fixture, updated)
    assert removed.id == product.id

    # 6) Повторный get должен вернуть None
    no_prod = await crud.product_crud.get(async_session_fixture, product.id)
    assert no_prod is None
