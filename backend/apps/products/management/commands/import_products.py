import os
import yaml
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import Category, Product, ProductParameter, Price
from apps.shops.models import Shop

class Command(BaseCommand):
    help = 'Импорт товаров'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к YAML файлу')
        parser.add_argument('--shop_id', type=int, help='ID магазина (если не указан, будет создан)')

    def handle(self, *args, **options):
        file_path = options['file_path']
        shop_id = options.get('shop_id')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                self.stdout.write(self.style.ERROR(f'Ошибка парсинга YAML: {e}'))
                return

        # Получаем или создаем магазин
        if shop_id:
            try:
                shop = Shop.objects.get(id=shop_id)
            except Shop.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Магазин с ID {shop_id} не найден'))
                return
        else:
            shop_name = data.get('shop', 'Магазин')
            shop, created = Shop.objects.get_or_create(
                name=shop_name,
                defaults={'user_id': 1}  
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан магазин: {shop.name}'))

        try:
            with transaction.atomic():
                self.import_categories(data.get('categories', []))
                self.import_goods(data.get('goods', []), shop)
            
            self.stdout.write(self.style.SUCCESS(f'Импорт из {file_path} успешно завершен'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка импорта: {e}'))

    def import_categories(self, categories_data):
        """Импорт категорий"""
        for cat_data in categories_data:
            category, created = Category.objects.update_or_create(
                id=cat_data.get('id'),
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(f'  Создана категория: {category.name}')
            else:
                self.stdout.write(f'  Обновлена категория: {category.name}')

    def import_goods(self, goods_data, shop):
        """Импорт товаров"""
        for item in goods_data:
            product, created = Product.objects.update_or_create(
                name=item['name'],
                category_id=item['category'],
                defaults={'description': item.get('description', '')}
            )

            price, price_created = Price.objects.update_or_create(
                product=product,
                shop=shop,
                defaults={
                    'price': item['price'],
                    'quantity': item['quantity']
                }
            )

            if 'parameters' in item:
                for param_name, param_value in item['parameters'].items():
                    ProductParameter.objects.update_or_create(
                        product=product,
                        name=param_name,
                        defaults={'value': str(param_value)}
                    )

            action = 'Создан' if created else 'Обновлен'
            self.stdout.write(f'  {action} товар: {product.name} (цена: {item["price"]})')