from django.db import models
from apps.accounts.models import User

class Shop(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    url = models.URLField(verbose_name='Сайт', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Прием заказов')
    
    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
    
    def __str__(self):
        return self.name