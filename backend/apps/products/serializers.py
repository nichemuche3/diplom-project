from rest_framework import serializers
from .models import Category, Product, ProductParameter, Price
from apps.shops.serializers import ShopSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductParameter
        fields = ['name', 'value']

class PriceSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    
    class Meta:
        model = Price
        fields = ['id', 'price', 'quantity', 'shop_name', 'updated_at']

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    min_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category_name', 'min_price']
    
    def get_min_price(self, obj):
        prices = obj.prices.filter(shop__is_active=True)
        if prices.exists():
            return min(p.price for p in prices)
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    parameters = ProductParameterSerializer(many=True, read_only=True)
    prices = PriceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description', 'parameters', 'prices']