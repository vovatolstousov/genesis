from rest_framework import serializers
from .models import UserAddress, CustomUser, Company, Account, SocialNetwork


class SocialNetworksSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialNetwork


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id',
                  'email',
                  'user_id',
                  'sn_id')
        depth = 1


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ('id', 'country', 'country_code', 'city', 'street', 'post_code')


class UserSerializer(serializers.ModelSerializer):
    user_address = UserAddressSerializer(source='useraddress_set', many=True, read_only=True)
    company = CompanySerializer(source='company_set', many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'password', 'username', 'first_name', 'last_name', 'contact_number', 'role', 'gender',
                  'user_address', 'email', 'profile_photo', 'company', 'online', 'last_activity', 'birthday', 'active')
        extra_kwargs = {'password': {'write_only': True}}

        depth = 2
