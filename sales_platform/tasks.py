from __future__ import absolute_import, unicode_literals
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
from .celery import app
from .core.orders.models import Order, OrderItem
from .core.users.models import CustomUser as User
from .core.users.models import VerificationCode
from .core.merchandise.models import Merchandise
from .core.orders.models import PayTransactions
from .settings import EMAIL_HOST_USER


@app.task
def test(arg):
    print(arg)


@app.task
def sent_verification_code(recipient_email, verification_code_id):
    verification_code = VerificationCode.objects.get(pk=verification_code_id)
    subject = 'VERIFICATION CODE'
    mail_message = "YOUR VERIFICATION CODE: " + verification_code.code
    try:
        send_mail(
            subject,
            mail_message,
            EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=True,
        )
        verification_code.status = 1
    except BadHeaderError:
        verification_code.status = 2
    verification_code.save()


@app.task
def sent_reset_password(recipient_email, new_password):
    subject = 'RESET PASSWORD'
    mail_message = 'You password: ' + new_password
    try:
        send_mail(
            subject,
            mail_message,
            EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=True
        )
    except BadHeaderError:
        pass


@app.task
def sent_order_information_notification(order_id):
    order = Order.objects.get(pk=order_id)
    if order.status == 1:  # processing
        subject = 'ORDER ID{0} IN GENESIS APP'.format(order.id)
        mail_message = 'Order id{0} change status to "processing".'. format(order.id)
        try:
            send_mail(
                subject,
                mail_message,
                EMAIL_HOST_USER,
                [order.user.email],
                fail_silently=True
            )
        except BadHeaderError:
            pass

        subject = 'ORDER ID{0} IN GENESIS APP'.format(order.id)
        mail_message = 'You have new order in genesis app! Order id {0}'.format(order.id)
        try:
            send_mail(
                subject,
                mail_message,
                EMAIL_HOST_USER,
                [order.seller_email],
                fail_silently=True
            )
        except BadHeaderError:
            pass
    if order.status == 2:  # sent
        subject = 'ORDER ID{0} IN GENESIS APP'.format(order.id)
        mail_message = 'Order id{0} change status to "sent".'.format(order.id)
        try:
            send_mail(
                subject,
                mail_message,
                EMAIL_HOST_USER,
                [order.user.email],
                fail_silently=True
            )
        except BadHeaderError:
            pass
    if order.status == 3:  # confirmed
        subject = 'ORDER ID{0} IN GENESIS APP'.format(order.id)
        mail_message = 'Order id {0} confirmed'.format(order.id)
        try:
            send_mail(
                subject,
                mail_message,
                EMAIL_HOST_USER,
                [order.seller_email],
                fail_silently=True
            )
        except BadHeaderError:
            pass


@app.task
def overdue_orders():
    from .core.paypal import PayPal
    query_set = Order.objects.filter(status=0)
    for order in query_set:
        if order.create_order_date < timezone.now() - timezone.timedelta(minutes=15):
            try:
                transaction = PayTransactions.objects.get()
                PayPal().check_parallel_payment_status(pay_key=transaction.pay_key)
                transaction = PayTransactions.object.get(order_id=order.id)
                if transaction.transaction_status == 'ERROR' or transaction.transaction_status == 'EXPIRED':
                    transaction.delete()
                    raise Exception
            except:
                order_items = OrderItem.objects.filter(order_id=order.id)
                for order_item in order_items:
                    merch = Merchandise.objects.get(pk=order_item.merch_id)
                    merch.count += order_item.count
                    merch.save()
                order.delete()


@app.task
def user_online_status_trigger():
    query_set = User.objects.all()
    for user in query_set:
        if user.last_activity < timezone.now() - timezone.timedelta(minutes=10):
            if user.online:
                user.online = False
                user.save()
        else:
            if user.online is False:
                user.online = True
                user.save()


@app.task
def delete_expired_unverificated_user():
    queryset = User.objects.filter(active=False)
    for user in queryset:
        if user.date_joined < timezone.datetime.now() - timezone.timedelta(days=2):
            user.is_active = False
            user.save()
