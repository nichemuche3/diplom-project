from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_verification_email(user):
    """Отправка email для подтверждения регистрации"""
    subject = 'Подтверждение регистрации'
    
    context = {
        'username': user.username,
        'user_id': user.id,
        'site_url': 'http://127.0.0.1:8000', 
    }
    
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
    """Отправка подтверждения заказа покупателю"""
    subject = f'Заказ #{order.id} подтвержден'
    
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


def send_invoice_to_admin(order):
    """
    Отправка накладной на email администратора магазина.
    Для каждого магазина в заказе отправляется отдельная накладная.
    """
    shops_items = {}
    
    for item in order.items.all():
        shop = item.price.shop
        if shop not in shops_items:
            shops_items[shop] = []
        
        shops_items[shop].append({
            'product_name': item.price.product.name,
            'quantity': item.quantity,
            'price': item.price.price,
            'total': item.quantity * item.price.price,
        })
    
    sent_count = 0
    for shop, items in shops_items.items():
        admin_email = shop.user.email
        
        subject = f'Накладная для заказа #{order.id} - {shop.name}'
        
        context = {
            'order_id': order.id,
            'shop_name': shop.name,
            'items': items,
            'total_price': sum(item['total'] for item in items),
            'customer': order.user,
            'contact': order.contact,
            'created_at': order.created_at,
            'site_url': 'http://127.0.0.1:8000',
        }
        
        html_message = render_to_string('emails/invoice.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            html_message=html_message,
            fail_silently=False,
        )
        sent_count += 1
    
    return sent_count


def send_order_status_notification(order, shop=None):
    """
    Отправка уведомления покупателю об изменении статуса заказа.
    Если указан shop - уведомление только о товарах этого магазина.
    """
    subject = f'Статус заказа #{order.id} изменен'
    
    if shop:
        items = []
        for item in order.items.filter(price__shop=shop):
            items.append({
                'product_name': item.price.product.name,
                'quantity': item.quantity,
                'price': item.price.price,
                'total': item.quantity * item.price.price,
            })
        shop_name = shop.name
    else:
        # Все товары
        items = []
        for item in order.items.all():
            items.append({
                'product_name': item.price.product.name,
                'quantity': item.quantity,
                'price': item.price.price,
                'total': item.quantity * item.price.price,
                'shop': item.price.shop.name,
            })
        shop_name = "Все магазины"
    
    context = {
        'order_id': order.id,
        'shop_name': shop_name,
        'items': items,
        'total_price': sum(item['total'] for item in items),
        'new_status': order.get_status_display(),
        'customer': order.user,
        'site_url': 'http://127.0.0.1:8000',
    }
    
    html_message = render_to_string('emails/order_status_changed.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_test_email(recipient_email):
    subject = 'Тестовое письмо'
    message = 'Если вы это видите, то почта работает правильно!'
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )