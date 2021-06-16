from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string

from apps.cart.cart import Cart

from .models import Order, OrderItem


def checkout(request, first_name, last_name, email, address, phone, district, sector, cell, village, delivery_address, delivery_cost, amount):

    try:
        order = Order.objects.create(first_name=first_name, last_name=last_name, email=email, address=address, phone=phone, district=district, sector=sector, cell=cell, village=village, delivery_address=delivery_address, delivery_cost=delivery_cost, paid_amount=amount)
    except Exception as e:
        raise e
    total_quantity = 0
    subtotal_amount = 0
    for item in Cart(request):
        total_quantity += item['quantity']
        subtotal_amount += item['product'].price * item['quantity']
        OrderItem.objects.create(
            order=order, product=item['product'], vendor=item['product'].vendor, price=item['product'].price, quantity=item['quantity'])

        order.vendors.add(item['product'].vendor)
    order.total_quantity = total_quantity
    order.subtotal_amount = subtotal_amount

    return order

def notify_vendor(order):
    connection = get_connection() # uses SMTP server specified in settings.py
    connection.open()

    from_email = settings.DEFAULT_EMAIL_FROM

    for vendor in order.vendors.all():
        to_email = vendor.email
        
        subject = 'New order'
        text_content = 'You have a new order!'
        html_content = render_to_string(
            'order/email_notify_vendor.html', {'order': order, 'vendor': vendor})
        print("================= vendor")
        print(html_content)

        msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to_email], connection=connection)
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

    connection.close()


def notify_customer(order):
    print("==== notify_customer")
    connection = get_connection() # uses SMTP server specified in settings.py
    connection.open()
    print("opened")
    from_email = settings.DEFAULT_EMAIL_FROM
    to_email = order.email
    subject = 'Order confirmation'
    text_content = 'Thank you for the order!'
    html_content = render_to_string(
        'order/email_notify_customer.html', {'order': order})
    print("html_content = ", html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email], connection=connection)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    connection.close()    