from rest_framework import generics, permissions
from .models import Shop
from .serializers import ShopSerializer, ShopDetailSerializer

class ShopListView(generics.ListAPIView):
    # Список всех магазинов
    queryset = Shop.objects.filter(is_active=True)
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]

class ShopDetailView(generics.RetrieveAPIView):
    # Детальная информация о магазине
    queryset = Shop.objects.all()
    serializer_class = ShopDetailSerializer
    permission_classes = [permissions.AllowAny]