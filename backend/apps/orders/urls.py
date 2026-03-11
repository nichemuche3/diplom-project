from django.urls import path
from . import views

urlpatterns = [
    # Корзина
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.add_to_cart, name='cart_add'),
    path('cart/remove/', views.remove_from_cart, name='cart_remove'),
    path('cart/update/', views.update_cart_item, name='cart_update'),
    
    # Заказы
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/status/', views.update_order_status, name='order_status'),
]