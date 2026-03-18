from rest_framework import generics, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.management import call_command
from io import StringIO
import yaml
import tempfile
import os

from .models import Category, Product, Price
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer


class CategoryListView(generics.ListAPIView):
    """Список всех категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductListView(generics.ListAPIView):
    """Список всех товаров с фильтрацией и поиском"""
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']


class ProductDetailView(generics.RetrieveAPIView):
    """Детальная информация о товаре"""
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]


class ImportProductsView(APIView):
    """
    Импорт товаров из YAML файла.
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        # Проверяем, что пользователь - поставщик
        if request.user.user_type != 'supplier':
            return Response(
                {'error': 'Только поставщики могут импортировать товары'},
                status=status.HTTP_403_FORBIDDEN
            )

        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'Файл не предоставлен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем расширение файла
        if not file.name.endswith(('.yaml', '.yml')):
            return Response(
                {'error': 'Файл должен быть в формате YAML (.yaml или .yml)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Сохраняем файл временно
        with tempfile.NamedTemporaryFile(delete=False, suffix='.yaml') as tmp_file:
            for chunk in file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        try:
            # Проверяем, что файл - валидный
            with open(tmp_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)

            # Получаем или создаем магазин для пользователя
            try:
                shop = request.user.shop
            except:
                # Если у пользователя нет магазина, создаем
                from apps.shops.models import Shop
                shop, created = Shop.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'name': request.user.company or f'Магазин {request.user.username}',
                        'is_active': True
                    }
                )
                if created:
                    print(f"Создан новый магазин для пользователя {request.user.username}")

            out = StringIO()
            call_command(
                'import_products',
                tmp_path,
                f'--shop_id={shop.id}',
                stdout=out
            )

            result = out.getvalue()
            
            return Response({
                'success': True,
                'message': 'Импорт выполнен успешно',
                'details': result.split('\n'),
                'shop': {
                    'id': shop.id,
                    'name': shop.name
                }
            })

        except yaml.YAMLError as e:
            return Response(
                {'error': f'Неверный формат YAML: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Ошибка импорта: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Удаляем временный файл
            try:
                os.unlink(tmp_path)
            except:
                pass