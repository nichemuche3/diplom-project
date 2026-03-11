from django.urls import path
from . import views

urlpatterns = [
    path('shops/', views.ShopListView.as_view(), name='shop_list'),
    path('shops/<int:pk>/', views.ShopDetailView.as_view(), name='shop_detail'),
]