import pytest
from backend.services import crud
from backend.schemas.category import CategoryCreate


@pytest.mark.asyncio
async def test_category_crud_create_get_update_remove(async_session_fixture):
    # 1) Создаём категорию
    data = CategoryCreate(name="TestCat")
    category = await crud.category_crud.create(async_session_fixture, data)
    assert category.id is not None
    assert category.name == "TestCat"

    # 2) Получаем по ID
    fetched = await crud.category_crud.get(async_session_fixture, category.id)
    assert fetched is not None
    assert fetched.name == "TestCat"

    # 3) Обновляем имя
    updated = await crud.category_crud.update(
        async_session_fixture, fetched, {"name": "NewCat"}
    )
    assert updated.name == "NewCat"

    # 4) Удаляем категорию
    removed = await crud.category_crud.remove(async_session_fixture, updated)
    assert removed.id == category.id

    # 5) Повторный get для удалённого объекта должен быть None
    no_cat = await crud.category_crud.get(async_session_fixture, category.id)
    assert no_cat is None
