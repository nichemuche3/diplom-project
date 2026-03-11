from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_verification_email(user):
    """Отправка email для подтверждения регистрации"""
    subject = 'Подтверждение регистрации'
    
    # Контекст для шаблона
    context = {
        'username': user.username,
        'user_id': user.id,
        'site_url': 'http://127.0.0.1:8000',  # В продакшене заменить на реальный URL
    }
    
    # Генерируем HTML и текстовую версию
    html_message = render_to_string('emails/verification.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_order_confirmation_email(order):
    """Отправка подтверждения заказа"""
    subject = f'Заказ #{order.id} подтвержден'
    
    # Формируем список товаров
    items_list = []
    for item in order.items.all():
        items_list.append({
            'product_name': item.price.product.name,
            'quantity': item.quantity,
            'price': item.price.price,
            'total': item.quantity * item.price.price
        })
    
    context = {
        'order_id': order.id,
        'username': order.user.username,
        'items': items_list,
        'total_price': order.total_price,
        'contact': order.contact,
        'status': order.get_status_display(),
        'site_url': 'http://127.0.0.1:8000',
    }
    
    html_message = render_to_string('emails/order_confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=html_message,
        fail_silently=False,
    )