import os
from os import path
from django.db import models
from django.utils import timezone
from ..users.models import CustomUser
from ..merchandise.models import Merchandise

ORDER_STATUS = (
    (0, 'unpaid'),
    (1, 'processing'),
    (2, 'sent'),
    (3, 'confirmed'),
)

CREDIT_CARD_CHOICES = (
    (0, 'Visa'),
    (1, 'MasterCard'),
    (2, 'American Express'),
    (3, 'Discover'),
)


class Order(models.Model):
    user = models.ForeignKey(CustomUser, related_name='buyer_order')
    seller = models.ForeignKey(CustomUser, related_name='seller_order')
    seller_email = models.EmailField(default="")
    status = models.IntegerField(choices=ORDER_STATUS, default=0)
    create_order_date = models.DateTimeField(default=timezone.now)
    full_price = models.FloatField(default=0)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return 'Order %s' % self.id


class OrderItem(models.Model):
    merch = models.ForeignKey(Merchandise, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=250, null=True)
    price = models.FloatField(default=0)
    preview_photo = models.ImageField('orderitem_photo', null=True, blank=True,
                                      upload_to=path.join('photo', 'order_items'),
                                      max_length=500)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'OrderItems'

    def __str__(self):
        return 'Merchandise {0}, count {1} in Order# {2}'.format(self.merch_id, self.count, self.order_id)

    def delete(self, using=None, keep_parents=False):
        if self.preview_photo:
            os.remove(self.preview_photo.path)
        return super(OrderItem, self).delete(using, keep_parents)


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, related_name='user_cart', on_delete=models.CASCADE)
    seller = models.ForeignKey(CustomUser, related_name='seller_cart', null=True)
    merch = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'CartItem'

    def __str__(self):
        return 'Cart id: {0}, user: {1}, seller: {2}, merch id: {3}, count {4}'\
            .format(self.id, self.user, self.seller, self.merch, self.count)


class CreditCard(models.Model):
    owner = models.ForeignKey(CustomUser, related_name='seller_credit_cart', on_delete=models.CASCADE)
    card_network = models.IntegerField(choices=CREDIT_CARD_CHOICES, default=0)
    card_number = models.BigIntegerField(null=True)
    cvv_code = models.PositiveSmallIntegerField(null=True)
    expiration_date = models.DateField(null=True)
    email = models.EmailField(blank=True)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'CreditCards'

    def __str__(self):
        return 'CreditCard id {0};  for user {1} id {2}'.format(self.id, self.owner, self.owner.id)


class PayTransactions(models.Model):
    payer = models.ForeignKey(CustomUser, related_name='payer', null=True)
    payer_transaction_email = models.TextField(blank=True)
    recipient = models.ForeignKey(CustomUser, related_name='recipient', null=True)
    recipient_transactions_email = models.TextField(blank=True)
    tax_recipient = models.TextField(max_length=250, default="")
    amount = models.FloatField(default=0)
    amount_recipient = models.FloatField(default=0)
    amount_genesis_tax = models.FloatField(default=0)
    tax_percent = models.FloatField(default=0)
    transaction_status = models.TextField(blank=True)
    pay_key = models.TextField(max_length=250, default="")
    timestamp = models.DateTimeField(null=True)
    order = models.OneToOneField(Order, null=True)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'PayTransactions'

    def __str__(self):
        return 'Pay status {4}, payKey {0}, amount: {3}, payer: {1}, recipient:{2}'.format(
            self.pay_key, self.payer, self.recipient, self.amount, self.transaction_status
        )


class PaymentCredential(models.Model):
    owner = models.ForeignKey(CustomUser, related_name='owner_payment_credentials', on_delete=models.CASCADE)
    payment_email = models.EmailField(null=True)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'PaymentCredentials'

    def __str__(self):
        return 'Payment Credentials for user {0}, id credentials {1}'.format(self.owner, self.pk)
