from django.contrib import admin
from .models import Category, Product, ProductParameter, Price

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    inlines = [ProductParameterInline]

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'shop', 'price', 'quantity', 'updated_at')
    list_filter = ('shop',)
    search_fields = ('product__name',)