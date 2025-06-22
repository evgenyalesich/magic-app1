# backend/tests/test_products.py
import pytest

@pytest.mark.asyncio
async def test_products_flow(client):
    # ───── 0. Сначала создаём категорию ───────────────────────────
    cat_payload = {"name": "Расклады"}
    r = await client.post("/api/categories/", json=cat_payload)
    assert r.status_code == 201
    category_id = r.json()["id"]

    # ───── 1. CREATE product ──────────────────────────────────────
    prod_payload = {
        "title": "Кельтский крест",
        "price": 1500,
        "description": "Классический большой расклад",
        "image": "https://example.com/celtic.jpg",
        "category_id": category_id,            # ← добавили
    }
    r = await client.post("/api/products/", json=prod_payload)
    assert r.status_code == 201
    product = r.json()
    prod_id = product["id"]

    # ───── 2. LIST ────────────────────────────────────────────────
    r = await client.get("/api/products/")
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()]
    assert prod_id in ids

    # ───── 3. DELETE ─────────────────────────────────────────────
    r = await client.delete(f"/api/products/{prod_id}")
    assert r.status_code in (204, 200)

    # ───── 4. Проверяем, что больше не существует ───────────────
    r = await client.get(f"/api/products/{prod_id}")
    assert r.status_code == 404
