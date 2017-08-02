from rest_framework import serializers
from .models import CartItem, Order, OrderItem, CreditCard, PaymentCredential
from ..merchandise.models import Merchandise
from ..users.models import CustomUser


class CartItemMerchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchandise
        fields = ('id', 'name', 'price', 'preview_photo')


class CartItemSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email')


class CartItemSerializer(serializers.ModelSerializer):
    merch = CartItemMerchSerializer()
    seller = CartItemSellerSerializer()

    class Meta:
        model = CartItem
        fields = ('id', 'user_id', 'seller', 'merch', 'count')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'merch_id', 'count', 'price', 'name', 'preview_photo')


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user_id', 'seller_id', 'seller_email', 'status', 'create_order_date', 'order_items', 'full_price')


class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = ('id', 'owner_id', 'card_network', 'card_number', 'cvv_code', 'expiration_date', 'email')


class PaymentCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCredential
        fields = ('id', 'payment_email')
