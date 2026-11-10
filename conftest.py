import pytest
from app import app as flask_app, db as flask_db, Category as FlaskCategory, Product as FlaskProduct
from shop.models import Category as DjangoCategory, Product as DjangoProduct, ProductDetail as DjangoProductDetail

# ----------------- FLASK FIXTURES -----------------
@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })
    with flask_app.app_context():
        flask_db.create_all()
        yield flask_app
        flask_db.session.remove()
        flask_db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def flask_category(app):
    cat = FlaskCategory(name="Тестова Категорія Flask", slug="test-flask")
    flask_db.session.add(cat)
    flask_db.session.commit()
    return cat

# ----------------- DJANGO FIXTURES -----------------
@pytest.fixture
def django_category(db):
    return DjangoCategory.objects.create(name="Тестова Категорія Django", slug="test-django")

@pytest.fixture
def django_product(db, django_category):
    prod = DjangoProduct.objects.create(
        name="Тестовий Ноутбук",
        price=25000.00,
        category=django_category
    )
    DjangoProductDetail.objects.create(
        product=prod,
        warranty_months=24,
        manufacturer_country="Україна"
    )
    return prod