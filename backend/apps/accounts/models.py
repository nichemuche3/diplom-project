from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
   # Расширенная модель пользователя
    USER_TYPE_CHOICES = (
        ('buyer', 'Покупатель'),
        ('supplier', 'Поставщик'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    company = models.CharField(max_length=100, verbose_name='Компания', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Contact(models.Model):
    #  Контакты пользователя
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=20, verbose_name='Дом')
    apartment = models.CharField(max_length=20, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    
    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
    
    def __str__(self):
        return f"{self.city}, {self.street} {self.house}"