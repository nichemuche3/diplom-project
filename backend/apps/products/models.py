from django.db import models
from apps.shops.models import Shop

class Category(models.Model):
    # Категория товаров
    name = models.CharField(max_length=100, verbose_name='Название')
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name

class Product(models.Model):
   # Товар
    name = models.CharField(max_length=200, verbose_name='Название')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(verbose_name='Описание', blank=True)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
    
    def __str__(self):
        return self.name

class ProductParameter(models.Model):
   # Характеристики товара
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='parameters')
    name = models.CharField(max_length=100, verbose_name='Название')
    value = models.CharField(max_length=100, verbose_name='Значение')
    
    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
    
    def __str__(self):
        return f"{self.name}: {self.value}"

class Price(models.Model):
   # Цена товара в конкретном магазине
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(verbose_name='Количество на складе')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'
        unique_together = ('product', 'shop')
    
    def __str__(self):
        return f"{self.product.name} - {self.price} руб."