from django.contrib import admin
from .models import Shop

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'user__username')