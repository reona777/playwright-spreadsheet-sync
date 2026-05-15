"""scraper モジュールのユニットテスト"""
import pytest

from scraper import Product, get_dummy_products


def test_get_dummy_products_returns_list():
    products = get_dummy_products()
    assert isinstance(products, list)
    assert len(products) > 0


def test_dummy_products_have_required_fields():
    products = get_dummy_products()
    for p in products:
        assert p.product_id != ""
        assert p.name != ""
        assert p.category != ""
        assert p.price > 0
        assert p.stock >= 0
        assert p.url.startswith("https://")


def test_dummy_products_stock_status():
    products = get_dummy_products()
    out_of_stock = [p for p in products if p.stock == 0]
    in_stock = [p for p in products if p.stock > 0]
    assert len(out_of_stock) >= 1
    assert len(in_stock) >= 1


def test_product_dataclass_fields():
    p = Product(
        product_id="TEST001",
        name="テスト商品",
        category="テスト",
        price=1000,
        stock=5,
        url="https://example.com/TEST001",
    )
    assert p.product_id == "TEST001"
    assert p.price == 1000
    assert p.stock == 5


def test_dummy_products_unique_ids():
    products = get_dummy_products()
    ids = [p.product_id for p in products]
    assert len(ids) == len(set(ids)), "商品IDが重複しています"
