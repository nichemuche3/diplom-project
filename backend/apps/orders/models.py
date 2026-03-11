from django.db import models
from apps.accounts.models import User, Contact
from apps.products.models import Price

class Cart(models.Model):
   # Корзина пользователя
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

class CartItem(models.Model):
   # Товар в корзине
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    price = models.ForeignKey(Price, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    
    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'

class Order(models.Model):
    # Заказ
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.date()}"

class OrderItem(models.Model):
   # Товар в заказе 
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    price = models.ForeignKey(Price, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    
    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'