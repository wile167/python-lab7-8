from unittest.mock import patch, MagicMock
import pytest
from shop.models import Product as DjangoProduct, Category as DjangoCategory
from app import db as flask_db, Product as FlaskProduct

# =====================================================================
# ЗАВДАННЯ 5: PyTest — ТЕСТИ МОДЕЛЕЙ, ФІКСТУРИ ТА ПАРАМЕТРИЗАЦІЯ
# =====================================================================

# 1. Перевірка створення об'єкта та рядкового представлення (__str__) в Django
@pytest.mark.django_db
def test_django_model_str(django_product):
    assert str(django_product) == "Тестовий Ноутбук (25000.0 грн)"

# 2. Перевірка каскадного видалення (CASCADE) в Django (OneToOneField)
@pytest.mark.django_db
def test_django_cascade_delete(django_product):
    product_id = django_product.id
    django_product.delete()
    assert DjangoProduct.objects.filter(id=product_id).count() == 0

# 3. Параметризований тест: перевірка створення товарів з різними цінами та статусами в Django
@pytest.mark.django_db
@pytest.mark.parametrize("price, status, expected_in_stock", [
    (100.00, 'published', True),
    (5000.50, 'draft', True),
    (0.00, 'archived', True),
])
def test_django_product_parametrization(django_category, price, status, expected_in_stock):
    prod = DjangoProduct.objects.create(
        name="Параметризований товар",
        price=price,
        status=status,
        category=django_category
    )
    assert prod.price == price
    assert prod.status == status
    assert prod.in_stock == expected_in_stock

# 4. Перевірка створення об'єкта у Flask-SQLAlchemy
def test_flask_product_creation(app, flask_category):
    prod = FlaskProduct(name="Flask Планшет", price=12000.0, category_id=flask_category.id)
    flask_db.session.add(prod)
    flask_db.session.commit()
    assert prod.id is not None
    assert prod.category.name == "Тестова Категорія Flask"

# 5. Перевірка значення за замовчуванням (rating) у Flask
def test_flask_product_default_rating(app, flask_category):
    prod = FlaskProduct(name="Flask Монітор", price=8000.0, category_id=flask_category.id)
    flask_db.session.add(prod)
    flask_db.session.commit()
    assert prod.rating == 5.0

# 6. Перевірка застереження унікальності імені категорії в Django
@pytest.mark.django_db
def test_django_category_unique_constraint(django_category):
    with pytest.raises(Exception):
        DjangoCategory.objects.create(name="Тестова Категорія Django", slug="test-django-2")


# =====================================================================
# ЗАВДАННЯ 6: ІНТЕГРАЦІЙНЕ ТЕСТУВАННЯ VIEWS І МАРШРУТІВ
# =====================================================================

# 1. Django: Перевірка головної сторінки (HTTP 200)
@pytest.mark.django_db
def test_django_index_view(client):
    response = client.get('/')
    assert response.status_code == 200

# 2. Django: Перевірка сторінки 404 для неіснуючого маршруту
@pytest.mark.django_db
def test_django_404_view(client):
    response = client.get('/non-existent-page/')
    assert response.status_code == 404

# 3. Flask: Позитивний тест GET-запиту каталогу (HTTP 200)
def test_flask_catalog_route(client):
    response = client.get('/catalog')
    assert response.status_code == 200

# 4. Flask: Негативний / Межовий тест POST-запиту форми зворотного зв'язку
def test_flask_contact_post_invalid(client):
    response = client.post('/contact', data={}, follow_redirects=True)
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    assert "This field is required" in html_content or "Обов" in html_content


# =====================================================================
# ЗАВДАННЯ 7: МОК-ТЕСТУВАННЯ ТА АНАЛІЗ ПОКРИТТЯ КОДУ
# =====================================================================

# 1. Мок зовнішньої залежності (підміна відправки електронної пошти / flash-повідомлення)
@patch('app.flash')
def test_mock_external_service_email_flash(mock_flash, client):
    valid_data = {
        'name': 'Глєб Костенков',
        'email': 'gleb@example.com',
        'category': 'tech',
        'message': 'Це тестове повідомлення з більше ніж трьох слів.'
    }
    response = client.post('/contact', data=valid_data, follow_redirects=True)
    assert response.status_code == 200
    # Перевіряємо, що зовнішня функція flash була викликана з очікуваними аргументами
    mock_flash.assert_called_once_with("Ваше повідомлення успішно надіслано!", "success")

# 2. Мок внутрішньої залежності (підміна виклику datetime у роуті index)
@patch('app.datetime')
def test_mock_internal_dependency_datetime(mock_datetime, client):
    # Створюємо мок-об'єкт для повернення фіксованого року
    mock_now = MagicMock()
    mock_now.year = 2026
    mock_datetime.now.return_value = mock_now

    response = client.get('/')
    assert response.status_code == 200
    # Перевірка, що метод datetime.now викликався для генерації контексту
    mock_datetime.now.assert_called_once()