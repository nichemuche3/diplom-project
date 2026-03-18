# test_fixes.py
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
from io import StringIO
import yaml
from apps.accounts.models import User
from apps.shops.models import Shop
from apps.products.models import Product, Category, Price, ProductParameter
from apps.orders.models import Order, OrderItem, Cart
from apps.common.email_utils import send_invoice_to_admin, send_order_status_notification


def print_header(text):
    """Печать заголовка"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)


def print_result(success, message):
    """Печать результата"""
    if success:
        print(f"  ✅ {message}")
    else:
        print(f"  ❌ {message}")


def test_import():
    """Тест 1: Импорт товаров из YAML"""
    print_header("ТЕСТ 1: ИМПОРТ ТОВАРОВ ИЗ YAML")
    
    # Создаем тестовый YAML
    test_yaml = """
shop: "Тестовый магазин для импорта"
categories:
  - id: 999
    name: "Тестовая категория"
  - id: 998
    name: "Еще категория"

goods:
  - id: 9999
    name: "Тестовый товар из YAML 1"
    category: 999
    price: 999.99
    quantity: 10
    description: "Этот товар создан тестом импорта"
    parameters:
      цвет: "красный"
      размер: "M"
      
  - id: 9998
    name: "Тестовый товар из YAML 2"
    category: 998
    price: 1499.99
    quantity: 5
    description: "Второй тестовый товар"
    parameters:
      цвет: "синий"
      вес: "1.5 кг"
"""
    
  
    yaml_path = 'test_import.yaml'
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(test_yaml)
    
    print(f"   Создан тестовый YAML файл: {yaml_path}")
    
   
    user = User.objects.first()
    if not user:
        print_result(False, "Нет пользователей в БД. Создайте хотя бы одного:")
        print("   python manage.py createsuperuser")
        return
    
   
    shop, created = Shop.objects.get_or_create(
        name="Тестовый магазин для импорта",
        defaults={'user': user}
    )
    print(f"   Используется магазин: {shop.name} (ID: {shop.id})")
    
   
    products_before = Product.objects.count()
    categories_before = Category.objects.count()
    prices_before = Price.objects.count()
    params_before = ProductParameter.objects.count()
    
    
    out = StringIO()
    try:
        print(f"   Запуск импорта из файла: {yaml_path}")
        call_command('import_products', yaml_path, f'--shop_id={shop.id}', stdout=out)
        result = out.getvalue()
        print(result)
    except Exception as e:
        print_result(False, f"Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
       
        if os.path.exists(yaml_path):
            os.remove(yaml_path)
        return
    
    
    products_after = Product.objects.count()
    categories_after = Category.objects.count()
    prices_after = Price.objects.count()
    params_after = ProductParameter.objects.count()
    

    new_product = Product.objects.filter(name="Тестовый товар из YAML 1").first()
    new_category = Category.objects.filter(id=999).first()
    
    print_result(products_after > products_before, f"Создано товаров: {products_after - products_before}")
    print_result(categories_after > categories_before, f"Создано категорий: {categories_after - categories_before}")
    print_result(prices_after > prices_before, f"Создано цен: {prices_after - prices_before}")
    print_result(params_after > params_before, f"Создано параметров: {params_after - params_before}")
    
    print_result(new_category is not None, "Категория 'Тестовая категория' создана")
    print_result(new_product is not None, "Товар 'Тестовый товар из YAML 1' создан")
    
    if new_product:
        prices = Price.objects.filter(product=new_product)
        print_result(prices.exists(), f"Цена создана: {prices.first().price if prices.exists() else 'нет'}")
        
        params = new_product.parameters.all()
        print_result(params.exists(), f"Параметры созданы: {params.count()}")
    
 
    if os.path.exists(yaml_path):
        os.remove(yaml_path)
        print(f"   Временный файл удален")


def test_invoice():
    """Тест 2: Отправка накладной на email администратора"""
    print_header("ТЕСТ 2: ОТПРАВКА НАКЛАДНОЙ")
    

    old_backend = settings.EMAIL_BACKEND
    
    
    settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    print("   Используется console.EmailBackend - письма будут в консоли")
    
    
    order = Order.objects.first()
    
    if not order:
        print_result(False, "Нет заказов для теста. Сначала создайте заказ.")
      
        settings.EMAIL_BACKEND = old_backend
        return
    
    print(f"   Используется заказ #{order.id}")
    
    try:
        # Отправляем накладную
        print("   Отправка накладной...")
        sent_count = send_invoice_to_admin(order)
        print_result(sent_count > 0, f"Отправлено накладных: {sent_count}")
        print("   ✅ Проверьте консоль Django - там должны быть письма с накладными")
    except Exception as e:
        print_result(False, f"Ошибка отправки: {e}")
        import traceback
        traceback.print_exc()
    finally:
        settings.EMAIL_BACKEND = old_backend


def test_status_permissions():
    """Тест 3: Проверка прав при изменении статуса"""
    print_header("ТЕСТ 3: ПРОВЕРКА ПРАВ НА ИЗМЕНЕНИЕ СТАТУСА")
    
    supplier1, created1 = User.objects.get_or_create(
        username='test_supplier1',
        defaults={
            'email': 'supplier1@test.com',
            'user_type': 'supplier'
        }
    )
    if created1:
        supplier1.set_password('password123')
        supplier1.save()
        print(f"   Создан поставщик 1: {supplier1.username}")
    else:
        print(f"   Найден поставщик 1: {supplier1.username}")
    
   
    supplier2, created2 = User.objects.get_or_create(
        username='test_supplier2',
        defaults={
            'email': 'supplier2@test.com',
            'user_type': 'supplier'
        }
    )
    if created2:
        supplier2.set_password('password123')
        supplier2.save()
        print(f"   Создан поставщик 2: {supplier2.username}")
    else:
        print(f"   Найден поставщик 2: {supplier2.username}")
    
   
    shop1, _ = Shop.objects.get_or_create(
        user=supplier1,
        defaults={'name': 'Магазин поставщика 1'}
    )
    shop2, _ = Shop.objects.get_or_create(
        user=supplier2,
        defaults={'name': 'Магазин поставщика 2'}
    )
    
    print_result(True, f"Поставщик 1: {supplier1.username}, магазин: {shop1.name} (ID: {shop1.id})")
    print_result(True, f"Поставщик 2: {supplier2.username}, магазин: {shop2.name} (ID: {shop2.id})")

    category, _ = Category.objects.get_or_create(name="Тестовая категория для прав")
    product, _ = Product.objects.get_or_create(
        name="Тестовый товар для проверки прав",
        defaults={'category': category, 'description': "Для теста прав поставщиков"}
    )
    

    price1, _ = Price.objects.get_or_create(
        product=product,
        shop=shop1,
        defaults={'price': 1000, 'quantity': 10}
    )
    
    # Создаем заказ (нужен покупатель)
    buyer, _ = User.objects.get_or_create(
        username='test_buyer',
        defaults={
            'email': 'buyer@test.com',
            'user_type': 'buyer'
        }
    )
    
    order = Order.objects.create(
        user=buyer,
        status='new'
    )
    
    OrderItem.objects.create(
        order=order,
        price=price1,
        quantity=1
    )
    
    print_result(True, f"Создан тестовый заказ #{order.id} с товаром от поставщика 1")
    
    # Тест 3.1: Проверка прав через прямой доступ (имитация)
    print("\n   Тест 3.1: Проверка наличия товаров поставщика в заказе:")
    
    
    items_supplier1 = order.items.filter(price__shop=shop1)
    items_supplier2 = order.items.filter(price__shop=shop2)
    
    print_result(items_supplier1.exists(), f"У поставщика 1 есть товары в заказе: {items_supplier1.count()}")
    print_result(not items_supplier2.exists(), f"У поставщика 2 нет товаров в заказе: {items_supplier2.count()}")
    
    # Тест 3.2: Симуляция API проверки прав
    print("\n   Тест 3.2: Симуляция проверки прав в API:")
    
    def can_change_status(user, order):
        """Симуляция проверки прав как в API"""
        if user.user_type != 'supplier':
            return False, "Только поставщики могут изменять статус"
        
        try:
            shop = user.shop
        except:
            return False, "У вас нет магазина"
        
        if not order.items.filter(price__shop=shop).exists():
            return False, "В этом заказе нет ваших товаров"
        
        return True, "OK"
    
    # Проверка для поставщика 1
    can1, msg1 = can_change_status(supplier1, order)
    print_result(can1, f"Поставщик 1: {msg1}")
    
    # Проверка для поставщика 2
    can2, msg2 = can_change_status(supplier2, order)
    print_result(not can2, f"Поставщик 2: {msg2} (ожидаемо)")
    
    if can1 and not can2:
        print_result(True, " Проверка прав работает правильно!")
    else:
        print_result(False, "Проблема с проверкой прав!")


def test_all():
    """Запуск всех тестов"""
    print(" ПРОВЕРКА ВСЕХ ДОРАБОТОК")
    
    if User.objects.count() == 0:
        print("\n В БД нет пользователей. Создайте хотя бы одного:")
        return
    
   
    test_import()
    test_invoice()
    test_status_permissions()
    
    print("\n" + "="*60)
    print(" ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)
    print("\nПроверьте результаты выше.")


if __name__ == "__main__":
    test_all()