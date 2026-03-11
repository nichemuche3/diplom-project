from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderCreateSerializer
from apps.products.models import Price
from apps.common.email_utils import send_order_confirmation_email

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    # Добавление товара в корзину
    price_id = request.data.get('price_id')
    quantity = request.data.get('quantity', 1)
    
    try:
        price = Price.objects.get(id=price_id, shop__is_active=True)
    except Price.DoesNotExist:
        return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        price=price,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request):
   # Удаление товара из корзины
    item_id = request.data.get('item_id')
    
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
        return Response({'status': 'removed'})
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({'error': 'Товар не найден в корзине'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request):
   # Обновление количества товара в корзине
    item_id = request.data.get('item_id')
    quantity = request.data.get('quantity')
    
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        return Response({'status': 'updated'})
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
class OrderCreateView(generics.CreateAPIView):
  # Создание заказа из корзины
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        cart = Cart.objects.get(user=self.request.user)
        if not cart.items.exists():
            raise serializers.ValidationError("Корзина пуста")
        
        order = serializer.save(user=self.request.user)
        
        # Перенос товаров из корзины в заказ
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                price=cart_item.price,
                quantity=cart_item.quantity
            )
        
        # Очистка корзины
        cart.items.all().delete()
        
        send_order_confirmation_email(order)
        
        return order

class OrderListView(generics.ListAPIView):
    # Список заказов пользователя
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    # Детали заказа 
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_order_status(request, pk):
    # Обновление статуса заказа (для поставщиков)
    try:
        order = Order.objects.get(pk=pk)
        # Проверка, что пользователь - поставщик этого товара
        if request.user.user_type != 'supplier':
            return Response({'error': 'Нет прав'}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({'status': order.status})
        return Response({'error': 'Неверный статус'}, status=status.HTTP_400_BAD_REQUEST)
    except Order.DoesNotExist:
        return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)