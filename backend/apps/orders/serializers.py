from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from apps.products.serializers import PriceSerializer

class CartItemSerializer(serializers.ModelSerializer):
    price_details = PriceSerializer(source='price', read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'price_details', 'quantity', 'total_price']
    
    def get_total_price(self, obj):
        return obj.price.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at', 'updated_at']
    
    def get_total_price(self, obj):
        return sum(item.price.price * item.quantity for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='price.product.name', read_only=True)
    price_per_item = serializers.DecimalField(source='price.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'price_per_item', 'quantity', 'total_price']
    
    def get_total_price(self, obj):
        return obj.price.price * obj.quantity

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'items', 'total_price', 'contact', 'contact_details']
    
    def get_total_price(self, obj):
        return sum(item.price.price * item.quantity for item in obj.items.all())
    
    def get_contact_details(self, obj):
        if obj.contact:
            return {
                'city': obj.contact.city,
                'street': obj.contact.street,
                'house': obj.contact.house,
                'apartment': obj.contact.apartment,
                'phone': obj.contact.phone
            }
        return None

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['contact']