import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

try:
    send_mail(
        'Тестовое письмо',
        'почта работает!',
        settings.DEFAULT_FROM_EMAIL,
        ['email@gmail.com'],  
        fail_silently=False,
    )
    print("✅ Письмо отправлено!")
except Exception as e:
    print(f"❌ Ошибка: {e}")