from django.conf.urls import url
from rest_framework import routers
from .views import seller_merchandise, seller_orders, merchandise_photo_add, merchandise_photo_delete, merchandise_feedbacks
from .views import token_auth, sn_auth, registration
from .views import UsersViewSet, MerchandiseViewSet, CategoryViewSet, TypeViewSet, CartItemViewSet, \
    OrderViewSet, OrderItemViewSet, CreditCardViewSet, PaymentCredentialsViewSet, PaymentViewSet, \
    VerificationCodeViewSet, RatingViewSet, FeedbackViewSet
from .views import paypal_payment_approve, paypal_payment_cancel, paypal_payment_redirect, \
    reset_password, change_password
from .views import merchandise_search, company_delete, address_delete


router = routers.DefaultRouter()
router.register(r'user', UsersViewSet, base_name='api_user')
router.register(r'category', CategoryViewSet, base_name='api_category')
router.register(r'type', TypeViewSet, base_name='api_type')
router.register(r'merchandise', MerchandiseViewSet, base_name='api_merchandise')
router.register(r'cartitem', CartItemViewSet, base_name='api_cart_item')
router.register(r'order', OrderViewSet, base_name='api_order')
router.register(r'orderitem', OrderItemViewSet, base_name='api_order_item')
router.register(r'creditcard', CreditCardViewSet, base_name='api_credit_card')
router.register(r'paymentcredential', PaymentCredentialsViewSet, base_name='api_payment_credetial')
router.register(r'payment', PaymentViewSet, base_name='api_payment')
router.register(r'verificationcode', VerificationCodeViewSet, base_name='api_verification_code')
router.register(r'rating', RatingViewSet, base_name='api_merchandise_rating')
router.register(r'feedback', FeedbackViewSet, base_name='api_feedback')

urlpatterns = [
    url(r'token-auth/', token_auth),
    url(r'sn-auth/', sn_auth),
    url(r'registration/', registration),
    url(r'resetpassword/', reset_password),
    url(r'seller/(?P<seller_id>[0-9]+)/merchandise/', seller_merchandise),
    url(r'seller/(?P<seller_id>[0-9]+)/order/', seller_orders),
    url(r'payment/approve', paypal_payment_approve),
    url(r'payment/cancel', paypal_payment_cancel),
    url(r'payment/redirect', paypal_payment_redirect),
    url(r'merchandise/(?P<merch_id>[0-9]+)/picture/(?P<id_picture>[0-9]+)/', merchandise_photo_delete),
    url(r'merchandise/(?P<merch_id>[0-9]+)/picture/', merchandise_photo_add),
    url(r'merchandise/(?P<merch_id>[0-9]+)/feedback/', merchandise_feedbacks),
    url(r'password', change_password),
    url(r'search/merchandise', merchandise_search),
    url(r'company/(?P<company_id>[0-9]+)/', company_delete),
    url(r'address/(?P<address_id>[0-9]+)/', address_delete)
]

urlpatterns += router.urls
