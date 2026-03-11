from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, ContactSerializer
from .models import Contact
from apps.common.email_utils import send_verification_email
from django.shortcuts import get_object_or_404

User = get_user_model()

# Регистрация
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    def perform_create(self, serializer):
        user = serializer.save()
        # Отправка email с подтверждением
        send_verification_email(user)
        return user

# Профиль пользователя
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

# Контакты (адреса доставки)
class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)
    
class VerifyEmailView(generics.GenericAPIView):
    permission_classes = []  # Разрешаем всем
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.is_verified = True
        user.save()
        return Response({'message': 'Email успешно подтвержден'})