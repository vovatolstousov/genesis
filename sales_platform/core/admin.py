from django.contrib import admin
from django.contrib.auth.models import Group
from .users.models import CustomUser, UserAddress, SocialNetwork, Account, Company, VerificationCode
from .merchandise.models import Merchandise, Feedback, Rating, Tag, MerchTag, \
    Type, Category, Marker, MarkerAddress, MerchPhoto
from .orders.models import Order, OrderItem, CartItem, CreditCard, PayTransactions, PaymentCredential
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                'fields': (
                    'contact_number',
                    'profile_photo',
                    'role',
                    'failed_log',
                    'gender',
                    'online',
                    'birthday',
                    'active'
                )
            }
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)

admin.site.register(UserAddress)
admin.site.register(SocialNetwork)
admin.site.register(Account)
admin.site.register(Company)
admin.site.register(VerificationCode)

admin.site.register(Merchandise)
admin.site.register(Feedback)
admin.site.register(Rating)
admin.site.register(Tag)
admin.site.register(Type)
admin.site.register(Category)
admin.site.register(Marker)
admin.site.register(MarkerAddress)
admin.site.register(MerchPhoto)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(CreditCard)
admin.site.register(PayTransactions)
admin.site.register(PaymentCredential)
