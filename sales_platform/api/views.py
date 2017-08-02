import datetime
import os
import random
import math
import time
import json
import requests
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, parsers, renderers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from ..core.users.serializers import UserSerializer
from ..core.users.models import SocialNetwork, Account, UserAddress, Company, VerificationCode
from ..core.users.models import CustomUser as User

from ..core.merchandise.serializers import MerchandiseSerializer, CategorySerializer, TypeSerializer, \
    MerchPhotoSerializer, RatingSerializer, FeedbackSerializer
from ..core.merchandise.models import Merchandise, Category, Type, MerchPhoto, Marker, MarkerAddress, Rating, Feedback

from ..core.orders.serializers import CartItemSerializer, OrderSerializer, OrderItemSerializer, CreditCardSerializer, \
    PaymentCredentialSerializer
from ..core.orders.models import CartItem, Order, OrderItem, CreditCard, PaymentCredential, PayTransactions

from ..core.paypal import PayPal
from ..tasks import sent_verification_code, sent_reset_password, sent_order_information_notification

from TwitterAPI import TwitterAPI
from ..settings import CONSUMER_KEY, CONSUMER_SECRET


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser, parsers.FileUploadParser)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = self.try_get_user(pk)
        if not user:
            return Response({'detail': 'user id: %s does not exist' % pk},
                            status=status.HTTP_404_NOT_FOUND)
        if not self.check_permission(request.user, user):
            return Response({'detail': 'permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data = request.data
        if 'first_name' in data and data['first_name'] and user.first_name != data['first_name']:
            user.first_name = data['first_name']
        if 'last_name' in data and data['last_name'] and user.last_name != data['last_name']:
            user.last_name = data['last_name']
        if 'contact_number' in data and user.contact_number != data['contact_number']:
            user.contact_number = data['contact_number']
        if 'role' in data:  # and data['role'] and user.role != data['role']:
            user.role = data['role']
        if 'gender' in data:  # and data['gender'] and user.gender != data['gender']:
            user.gender = data['gender']
        if 'email' in data and data['email'] and user.email != data['email']:
            user.email = data['email']
        if 'user_address' in data:
            list_address = data['user_address']
            for address in list_address:
                country = address['country']
                country_code = address['country_code']
                city = address['city']
                street = address['street']
                post_code = address['post_code']
                if address['id'] == 0:
                    if not country or (not city and not street and not post_code and country_code):
                        continue
                    UserAddress.objects.create(
                        user=user,
                        country=country,
                        city=city,
                        street=street,
                        post_code=post_code,
                        country_code=country_code
                    )
                else:
                    try:
                        user_address = UserAddress.objects.get(pk=address['id'])
                        user_address.country = country
                        user_address.country_code = country_code
                        user_address.city = city
                        user_address.street = street
                        user_address.post_code = post_code
                        user_address.save()
                    except:
                        continue
        if 'company' in data:
            list_company = data['company']
            for company in list_company:
                name = company['name']
                industry = company['industry']
                country = company['country']
                country_code = company['country_code']
                city = company['city']
                post_code = company['post_code']
                contact_number = company['contact_number']
                fax_number = company['fax_number']
                enquiry_email = company['enquiry_email']
                if company['id'] == 0:
                    if not name:
                        continue
                    Company.objects.create(
                        user=user, name=name, industry=industry, country=country, city=city,
                        post_code=post_code, contact_number=contact_number,
                        fax_number=fax_number, enquiry_email=enquiry_email, country_code=country_code
                    )
                else:
                    try:
                        user_company = Company.objects.get(pk=company['id'])
                        user_company.name = name
                        user_company.industry = industry
                        user_company.country = country
                        user_company.city = city
                        user_company.post_code = post_code
                        user_company.contact_number = contact_number
                        user_company.fax_number = fax_number
                        user_company.enquiry_email = enquiry_email
                        user_company.country_code = country_code
                        user_company.save()
                    except:
                        continue
        if 'birthday' in data:
            birthday = data['birthday']
            if birthday:
                try:
                    birthday_data = time.strptime(birthday, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    pass
                else:
                    user.birthday = '{0}-{1}-{2}'.format(birthday_data.tm_year, birthday_data.tm_mon, birthday_data.tm_mday)
        user.save()
        user_data = self.serializer_class(user, context={"request": request}).data
        return Response(user_data, status=status.HTTP_200_OK)

    def try_get_user(self, pk):
        try:
            user = self.queryset.get(pk=pk)
        except:
            user = None
        return user

    @staticmethod
    def check_permission(current_user, edit_user):
        if current_user == edit_user or current_user.is_staff or current_user.is_superuser:
            return True
        return False

    def update(self, request, *args, **kwargs):
        # PUT AND PATCH METHODS
        pk = kwargs.get('pk')
        user = self.try_get_user(pk=pk)

        if not user:
            return Response({'detail': 'user id: %s does not exist' % pk},
                            status=status.HTTP_404_NOT_FOUND)
        if not self.check_permission(request.user, user):
            return Response({'detail': 'permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if 'profile_photo' in request.FILES:
            profile_photo = request.FILES['profile_photo']
            if len(profile_photo):
                if user.profile_photo:
                    user.profile_photo.delete()
                user.profile_photo = profile_photo
                user.save()

        user_data = self.serializer_class(user, context={"request": request}).data
        return Response(user_data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()


class MerchandiseViewSet(viewsets.ModelViewSet):
    queryset = Merchandise.objects.all()
    serializer_class = MerchandiseSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role == 0:
            return Response({'detail': 'Only seller can create new item'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if 'name' not in request.data or 'price' not in request.data or 'type_id' not in request.data or 'category_id' not in request.data:
            return Response(
                {'detail': ['Request must include fields "name", "price", "type" and "category".']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if float(request.data['price']) < 0.01:
            return Response({'detail': 'Invalid price value'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            type_obj = Type.objects.get(id=request.data['type_id'])
        except:
            return Response(
                {'detail': 'Type %s does not exist!' % request.data['type_id']}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category_obj = Category.objects.get(id=request.data['category_id'])
        except:
            return Response(
                {'detail': 'Category %s does not exist!' % request.data['category_obj']},
                status=status.HTTP_400_BAD_REQUEST
            )

        merchandise = Merchandise.objects.create(
            name=request.data['name'],
            price=request.data['price'],
            seller=user,
            seller_email=user.email,
            type=type_obj,
            category=category_obj
        )

        if 'description' in request.data:
            merchandise.description = request.data['description']

        if 'merchandise' in request.data:
            merchandise.merchandise = request.data['merchandise']

        if 'count' in request.data:
            if int(request.data['count']) < 0:
                return Response({'detail': 'Invalid count value'}, status=status.HTTP_400_BAD_REQUEST)
            merchandise.count = request.data['count']

        if 'list_markers' in request.data:
            list_markers = request.data['list_markers']
            for marker in list_markers:
                marker_address = marker['address']
                if not marker['lat'] or not marker['lon'] or not marker_address['country'] \
                        or not marker_address['city']:
                    continue
                new_marker = Marker.objects.create(
                    lat=marker['lat'],
                    lon=marker['lon'],
                    merch=merchandise
                )
                MarkerAddress.objects.create(
                    country=marker_address['country'],
                    country_code=marker_address['country_code'],
                    city=marker_address['city'],
                    street=marker_address['street'],
                    marker=new_marker
                )

        if 'video_url' in request.data:
            if request.data['video_url']:
                merchandise.video_url = request.data['video_url']

        merchandise.save()
        return Response(self.serializer_class(merchandise).data, status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        try:
            merch = Merchandise.objects.get(pk=kwargs.get('pk'))
        except:
            return Response({'detail': 'merchandise id: %s does not exist' % kwargs.get('pk')},
                            status=status.HTTP_404_NOT_FOUND)
        if merch.seller.id != request.user.id:
            if not request.user.is_superuser:
                return Response({'detail': 'permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data = request.data
        for key in data:
            try:
                if key == 'id' or key == 'photo' or key == 'preview_photo' or key == 'type_id' \
                        or key == 'category_id' or key == 'list_markers' or key == 'seller':
                    continue
                if key == 'name' and not data['name']:
                    return Response({'detail': 'field name can`t be empty'}, status=status.HTTP_400_BAD_REQUEST)
                if key == 'price' and not data['price']:
                    if float(data['price']) < 0.01:
                        return Response({'detail': 'Invalid price value'}, status=status.HTTP_400_BAD_REQUEST)
                if key == 'count' and not data['count']:
                    if int(request.data['count']) < 0:
                        return Response({'detail': 'Invalid count value'}, status=status.HTTP_400_BAD_REQUEST)
                if data[key] != merch.__getattribute__(key):
                    setattr(merch, key, data[key])
            except:
                return Response({'detail': 'Unexpected attribute %s' % key},
                                status=status.HTTP_400_BAD_REQUEST)

        if 'type_id' in request.data:
            if data['type_id'] and merch.type_id != data['type_id']:
                try:
                    merch.type = Type.objects.get(pk=data['type_id'])
                except:
                    return Response({'detail': 'Invalid type value'}, status=status.HTTP_400_BAD_REQUEST)
        if 'category_id' in request.data:
            if data['category_id'] and merch.category.id != data['category_id']:
                try:
                    merch.category = Category.objects.get(pk=data['category_id'])
                except:
                    return Response({'detail': 'Invalid category value'}, status=status.HTTP_400_BAD_REQUEST)

        for marker in Marker.objects.filter(merch=merch):
            marker.delete()

        if 'list_markers' in data:
            list_markers = data['list_markers']
            for marker in list_markers:
                lat = marker['lat']
                lon = marker['lon']
                address = marker['address']
                country = address['country']
                country_code = address['country_code']
                city = address['city']
                street = address['street']
                # if marker['id'] == 0:
                if not lat or not lon or not country or not city:
                    continue
                marker = Marker.objects.create(
                    lat=lat,
                    lon=lon,
                    merch=merch
                )
                MarkerAddress.objects.create(
                    country=country,
                    city=city,
                    street=street,
                    country_code=country_code,
                    marker=marker
                )
        merch.save()
        merch_data = self.serializer_class(merch, context={"request": request}).data
        return Response(merch_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # PUT AND PATCH METHODS
        pk = kwargs.get('pk')
        try:
            merchandise = self.queryset.get(pk=pk)
        except:
            return Response({'detail': 'merchandise id: %s does not exist' % pk},
                            status=status.HTTP_404_NOT_FOUND)
        if request.user.id != merchandise.seller.id:
            return Response({'detail': 'permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if 'preview_photo' in request.data:
            preview_photo = self.request.FILES['preview_photo']
            if len(preview_photo):
                if merchandise.preview_photo:
                    merchandise.preview_photo.delete()
                merchandise.preview_photo = preview_photo
                merchandise.save()

        merch_data = self.serializer_class(merchandise, context={"request": request}).data
        return Response(merch_data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def post(self, request, *args, **kwargs):
        try:
            category = Category.objects.get(pk=kwargs.get('pk'))
        except:
            return Response({'detail': 'category id: %s does not exist' % kwargs.get('pk')},
                            status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_superuser:
            return Response({'detail': 'permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        category_data = self.serializer_class(category).data
        return Response(category_data, status=status.HTTP_200_OK)


class TypeViewSet(viewsets.ModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def list(self, request, *args, **kwargs):
        if not request.user:
            return Response({'detail': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        cart_items = self.queryset.filter(user=request.user)
        cart_items_data = self.serializer_class(cart_items, context={"request": request}, many=True).data
        return Response(cart_items_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if not request.user:
            return Response({'detail': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'merch' not in request.data or 'count' not in request.data:
            return Response({'detail': ['Request must include fields "merch" and "count"']},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            merch_obj = Merchandise.objects.get(pk=request.data['merch']['id'])
        except:
            return Response({'detail': 'Merch with id %s does not exist' % request.data['merch']['id']},
                            status=status.HTTP_400_BAD_REQUEST)
        if int(request.data['count']) < 1 or int(request.data['count'] > merch_obj.count):
            return Response({'detail': 'Invalid count value'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.get(
                merch_id=merch_obj.id,
                seller_id=merch_obj.seller,
                user_id=request.user.id,
            )
            new_count = item.count + request.data['count']
            if new_count > merch_obj.count:
                return Response({'detail': 'Invalid count value'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                item.count = new_count
        except:
            item = CartItem.objects.create(
                user=request.user,
                seller=merch_obj.seller,
                merch=merch_obj,
                count=request.data['count']
            )
        item.save()
        return Response(self.serializer_class(item, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        if not request.user:
            return Response({'detail': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        pk = kwargs.get('pk')
        try:
            item = self.queryset.get(pk=pk)
        except:
            return Response({'detail': 'Item with id %s does not exist' % pk}, status=status.HTTP_400_BAD_REQUEST)
        if item.user != request.user:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if 'count' not in request.data:
            return Response({'detail': 'Request must include field "count"'})
        if int(request.data['count']) < 1:
            return Response({'detail': 'Invalid count value'}, status=status.HTTP_400_BAD_REQUEST)
        item.count = request.data['count']
        item.save()
        return Response(self.serializer_class(item, context={"request": request}).data, status=status.HTTP_200_OK)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def list(self, request, *args, **kwargs):
        if not request.user:
            return Response({'detail': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        order_list = self.queryset.filter(user=request.user)
        order_list_data = self.serializer_class(order_list, context={"request": request}, many=True).data
        return Response(order_list_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if not request.user:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        try:
            order_obj = self.queryset.get(pk=kwargs.get('pk'))
            if not (order_obj.seller.id == user.id or order_obj.user.id == user.id):
                return Response({'detail': 'Permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except:
            return Response({'detail': 'Order with id %s does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        if 'status' in request.data:
            status_ = int(request.data['status'])
            if order_obj.user.id == user.id:  # buyer
                if order_obj.status == 2 and status_ == 3:
                    order_obj.status = status_
                    order_obj.save()
                    sent_order_information_notification.delay(order_obj.id)
                else:
                    return Response(
                        {
                            'detail': 'Cant change status. Permissions denied.'
                        },
                        status=status.HTTP_406_NOT_ACCEPTABLE
                    )
            elif order_obj.seller.id == user.id:  # seller
                if order_obj.status == 1 and status_ == 2:
                    order_obj.status = status_
                    order_obj.save()
                    sent_order_information_notification.delay(order_obj.id)
                else:
                    return Response(
                        {
                            'detail': 'Cant change status. Permissions denied.'
                        },
                        status=status.HTTP_406_NOT_ACCEPTABLE
                    )
        order_data = self.serializer_class(order_obj, context={"request": request}, many=False).data
        return Response(order_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        order_data = request.data
        try:
            if 'seller_id' not in order_data:
                raise Exception
            seller = User.objects.get(pk=order_data['seller_id'])
            if seller.role != 1:
                raise Exception
        except:
            return Response({'detail': 'Invalid seller value'}, status=status.HTTP_400_BAD_REQUEST)
        list_items = order_data['order_items']
        if not self.validate_order_items(list_items):
            return Response(
                {
                    'detail': self.generate_conflict_log(list_items)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not self.validate_order_data(list_items, seller):
            return Response(
                {'detail': 'seller_id is not owner for some order items!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_order_obj = Order.objects.create(
            user=request.user,
            seller=seller,
            seller_email=seller.email,
            status=0,
            create_order_date=timezone.now()
        )
        full_price = 0
        for item in list_items:
            count = item['count']
            if count <= 0:
                continue
            merchandise = Merchandise.objects.get(pk=item['merch_id'])
            new_name = os.path.join(merchandise.preview_photo.path).split('/')[-1]
            OrderItem.objects.create(
                merch=merchandise,
                order=new_order_obj,
                count=count,
                price=merchandise.price,
                name=merchandise.name,
                preview_photo=File(file=open(merchandise.preview_photo.path, 'rb'), name=new_name)
            )
            full_price += merchandise.price * count
            merchandise.count -= count
            merchandise.save()
            cart_item = CartItem.objects.get(merch=merchandise, user=request.user)
            cart_item.delete()
        new_order_obj.full_price = full_price
        new_order_obj.save()

        order_data = self.serializer_class(new_order_obj, context={"request": request}, many=False).data
        return Response(order_data, status=status.HTTP_201_CREATED)

    def validate_order_items(self, list_items):
        for item in list_items:
            if not self.check_availability(item['merch_id'], item['count']):
                return False
        return True

    @staticmethod
    def validate_order_data(list_items, seller):
        for item in list_items:
            merch = Merchandise.objects.get(pk=item['merch_id'])
            if merch.seller_id != seller.id:
                return False
        return True

    @staticmethod
    def check_availability(merchandise_id, count):
        try:
            merch = Merchandise.objects.get(pk=merchandise_id)
            return count <= merch.count
        except:
            return False

    @staticmethod
    def generate_conflict_log(list_items):
        response_list = list()
        for item in list_items:
            item_data = {}
            try:
                merch = Merchandise.objects.get(pk=item['merch_id'])
                item_data['merch_id'] = merch.id
                item_data['merch_name'] = merch.name
                item_data['in_stock'] = merch.count
            except:
                item_data['merch_id'] = 0
                item_data['merch_name'] = 0
                item_data['in_stock'] = 0
            item_data['count_to_cart'] = item['count']
            response_list.append(item_data)
        return Response({'merch_items': response_list}, status=status.HTTP_409_CONFLICT)

    def destroy(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(pk=kwargs.get('pk'))
        except ObjectDoesNotExist:
            return Response({'detail': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if not (order.seller.id == request.user.id or order.user.id == request.user.id):
            return Response({'detail': 'Permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if order.seller == request.user:
            return Response(
                {
                    'detail': 'You cant delete order'
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        if order.user == request.user:
            if order.status > 0:
                return Response(
                    {
                        'detail': 'Not Acceptable'
                    },
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
            order_items = OrderItem.objects.filter(order_id=order.id)
            for order_item in order_items:
                merch = Merchandise.objects.get(pk=order_item.merch_id)
                merch.count += order_item.count
                merch.save()
            order.delete()
            return Response({}, status=status.HTTP_200_OK)


class CreditCardViewSet(viewsets.ModelViewSet):
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer

    def list(self, request, *args, **kwargs):
        credit_cards = self.queryset.filter(owner_id=request.user.id)
        json_data = self.serializer_class(credit_cards, context={"request": request}, many=True).data
        return Response(json_data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            credit_card = self.queryset.get(pk=pk)
        except:
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if credit_card.owner_id != request.user.id:
            return Response({'detail': 'Permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        json_data = self.serializer_class(credit_card, context={"request": request}).data
        return Response(json_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if request.user.role != 1:
            return Response({'detail': 'permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if 'card_network' not in request.data or 'card_number' not in request.data\
                or 'cvv_code' not in request.data or 'expiration_date' not in request.data:
            return Response(
                {
                    'detail': [
                        'Request must include fields "card_network", "card_number", "cvv_code" and "expiration_data".'
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        owner = request.user
        card_network = request.data['card_network']
        card_number = request.data['card_number']
        cvv_code = request.data['cvv_code']
        expiration_date = request.data['expiration_date']

        if not card_network or not card_number or not cvv_code or not expiration_date:
            return Response(
                {
                    'detail': [
                        'Fields "card_network", "card_number", "cvv_code", and "expiration_date"'
                        ' cant be empty.'
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(cvv_code) != 3:
            return Response({'detail': 'Invalid cvv_code'}, status=status.HTTP_200_OK)
        credit_card = CreditCard.objects.create(
            owner=owner,
            card_network=card_network,
            card_number=card_number,
            cvv_code=cvv_code,
            expiration_date=expiration_date,
            email=owner.email,
        )
        json_data = self.serializer_class(credit_card, context={"request": request}).data
        return Response(json_data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            credit_card = self.queryset.get(pk=pk)
        except:
            return Response(
                {
                    'detail': 'Credit card with id {0} does not exist.'.format(pk)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if credit_card.owner_id != request.user.id:
            return Response({'detail': 'Permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        credit_card.delete()
        return Response({'detail': 'OK'}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return self.update_credit_card(request.user, request.data, kwargs.get('pk'))

    def update(self, request, pk=None, *args, **kwargs):
        return self.update_credit_card(request.user, request.data, pk)

    def update_credit_card(self, user, data, pk):
        try:
            credit_card = self.queryset.get(pk=pk)
        except:
            return Response(
                {'detail': 'Not Found'},
                status=status.HTTP_404_NOT_FOUND
            )
        if credit_card.owner != user:
            return Response(
                {'detail': 'Permissions denied'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        for key in data:
            if not data[key] or key == 'owner':
                continue
            if key == 'cvv_code':
                if len(data['cvv_code']) != 3:
                    continue
            try:
                if data[key] != credit_card.__getattribute__(key):
                    setattr(credit_card, key, data[key])
            except:
                return Response({'detail': 'Unexpected attribute %s' % key},
                                status=status.HTTP_400_BAD_REQUEST)
        credit_card.save()
        json_data = self.serializer_class(credit_card).data
        return Response(json_data, status=status.HTTP_200_OK)


class PaymentCredentialsViewSet(viewsets.ModelViewSet):
    queryset = PaymentCredential.objects.all()
    serializer_class = PaymentCredentialSerializer

    def list(self, request, *args, **kwargs):
        payment_credentials = self.queryset.filter(owner_id=request.user.id)
        json_data = self.serializer_class(payment_credentials, many=True).data
        return Response(json_data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            payment_credential = self.queryset.get(pk=pk)
        except:
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if payment_credential.owner_id != request.user.id:
            return Response({'detail': 'Permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        json_data = self.serializer_class(payment_credential).data
        return Response(json_data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            payment_credential = self.queryset.get(pk=pk)
        except:
            return Response(
                {
                    'detail': 'Payment Credentials with id {0} does not exist.'.format(pk)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if payment_credential.owner_id != request.user.id:
            return Response({'detail': 'Permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        payment_credential.delete()
        return Response({'detail': 'OK'}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        return self.create_or_update(request.user, request.data)

    def post(self, request, *args, **kwargs):
        return self.create_or_update(request.user, request.data)

    def update(self, request, pk=None, *args, **kwargs):
        return self.create_or_update(request.user, request.data)

    def create_or_update(self, user, data):
        if user.role != 1:
            return Response({'detail': 'permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if 'payment_email' not in data:
            return Response(
                {
                    'detail': [
                        'Request must include field "payment_email".'
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        paypal_account_info = PayPal().paypal_account_information(data['payment_email'])
        if 'error' in paypal_account_info:
            return Response({'detail': paypal_account_info['error'][0]['message']}, status=status.HTTP_409_CONFLICT)
        if paypal_account_info['accountStatus'] == 'UNVERIFIED':
            return Response({'detail': 'PayPal account status is UNVERIFIED'}, status=status.HTTP_409_CONFLICT)
        if paypal_account_info['userInfo']['accountType'] == 'PERSONAL':
            return Response({'detail': 'PayPal account type is PERSONAL'}, status=status.HTTP_409_CONFLICT)
        try:
            payment_credetial = self.queryset.get(owner_id=user.id)
        except:
            payment_credetial = self.queryset.create(
                owner=user,
            )
        payment_credetial.payment_email = data['payment_email']
        payment_credetial.save()
        json_data = self.serializer_class(payment_credetial).data
        return Response(json_data, status=status.HTTP_201_CREATED)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            merch = Merchandise.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(
                {
                    'detail': 'Merchandise does not exist'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            # rating = self.queryset.filter(merch=merch)
            # rating_data = self.serializer_class(rating, context={'request': request}, many=True).data
        try:
            rating = self.queryset.get(user=request.user, merch_id=merch.id)
            rating_data = self.serializer_class(rating, context={'request': request}).data
            return Response(rating_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {
                    'merch_id': 0,
                    'stars': 0
                },
                status=status.HTTP_200_OK
            )

    def create(self, request, *args, **kwargs):
        if 'merch_id' not in request.data or 'stars' not in request.data:
            return Response(
                {
                    'detail': [
                        'Request must include fields "merch_id" and "stars".'
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        stars = int(request.data['stars'])
        if not stars:
            return Response(
                {
                    'detail': 'Rating stars is empty'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if stars < 0 or stars > 5:
            return Response(
                {
                    'detail': 'Invalid rating stars.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            merch = Merchandise.objects.get(pk=request.data['merch_id'])
        except ObjectDoesNotExist:
            return Response(
                {
                    'detail': 'Invalid item id'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        order_list = Order.objects.filter(user=user)
        for order in order_list:
            order_items = OrderItem.objects.filter(order_id=order.id)
            for item in order_items:
                if item.merch_id == merch.id:
                    if order.status != 3:
                        return Response(
                            {
                                'detail': 'Order not confirmed'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    try:
                        rating = self.queryset.get(merch=merch, user=user)
                        old_count_stars = rating.stars
                        rating.stars = stars
                        rating.created_date = timezone.now()
                        rating.save()
                        if not merch.rating_count_votes and not merch.average_rating:
                            merch.average_rating = rating.stars
                            merch.rating_count_votes = 1
                        else:
                            rating_count_votes = int(merch.rating_count_votes)
                            average_rating = float(merch.average_rating)
                            new_average = (average_rating * rating_count_votes - old_count_stars + stars) / rating_count_votes
                            merch.average_rating = new_average
                    except ObjectDoesNotExist:
                        rating = self.queryset.create(
                            user=request.user,
                            merch=merch,
                            stars=stars
                        )
                        if not merch.rating_count_votes and not merch.average_rating:
                            merch.average_rating = rating.stars
                            merch.rating_count_votes = 1
                        else:
                            rating_count_votes = int(merch.rating_count_votes)
                            average_rating = float(merch.average_rating)
                            new_average = (average_rating * rating_count_votes + stars) / (rating_count_votes + 1)
                            merch.rating_count_votes += 1
                            merch.average_rating = new_average
                    merch.save()
                    return Response(
                        {
                            'merch_id': rating.merch.id,
                            'stars': rating.stars
                        },
                        status=status.HTTP_200_OK)
        return Response(
            {
                'detail': 'Error, not acceptable'
            },
            status=status.HTTP_406_NOT_ACCEPTABLE
        )

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            merch = Merchandise.objects.get(pk=pk)
            rating = self.queryset.get(user=request.user, merch=merch)
            average_rating = merch.average_rating
            rating_count_votes = merch.rating_count_votes
            if rating_count_votes - 1 < 1:
                merch.rating_count_votes = 0
                merch.average_rating = 0
            else:
                new_rating = (average_rating * rating_count_votes - rating.stars) / (rating_count_votes - 1)
                merch.average_rating = new_rating
                merch.rating_count_votes -= 1
            merch.save()
            rating.delete()
            return Response(
                {
                    'merch_id': 0,
                    'stars': 0
                },
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    'detail': 'Object does not exist'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        if 'merch_id' not in request.data or 'text' not in request.data:
            return Response(
                {
                    'detail': [
                        'Request must include fields "merch_id" and "text".'
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        text = request.data['text']
        if not text:
            return Response(
                {
                    'detail': 'Feedback text is empty'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(text) > 1000:
            return Response(
                {
                    'detail': 'Invalid feedback text length. Max length 1000.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            merch = Merchandise.objects.get(pk=request.data['merch_id'])
        except ObjectDoesNotExist:
            return Response(
                {
                    'detail': 'Invalid item id'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        order_list = Order.objects.filter(user=user)
        for order in order_list:
            order_items = OrderItem.objects.filter(order_id=order.id)
            for item in order_items:
                if item.merch_id == merch.id:
                    if order.status != 3:
                        return Response(
                            {
                                'detail': 'Order not confirmed'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    try:
                        feedback = self.queryset.get(merch=merch, user=user)
                        feedback.text = text
                        # feedback.created_date = timezone.now()
                        feedback.username = user.get_full_name()
                        if not feedback.user_profile_photo:
                            if user.profile_photo:
                                new_name = os.path.join(user.profile_photo.path).split('/')[-1]
                                feedback.user_profile_photo = File(file=open(user.profile_photo.path, 'rb'),
                                                                   name=new_name)
                        feedback.save()
                    except ObjectDoesNotExist:
                        feedback = self.queryset.create(
                            user=request.user,
                            merch=merch,
                            text=text,
                            username=user.get_full_name()
                        )
                        if request.user.profile_photo:
                            new_name = os.path.join(user.profile_photo.path).split('/')[-1]
                            feedback.user_profile_photo = File(file=open(user.profile_photo.path, 'rb'), name=new_name)
                            feedback.save()
                        # print()
                    return Response(
                            self.serializer_class(feedback, context={"request": request}).data,
                            status=status.HTTP_200_OK
                    )
        return Response(
            {
                'detail': 'You cant leave feedback if you not if you have not ordered item'
            },
            status=status.HTTP_406_NOT_ACCEPTABLE
        )

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            merch = Merchandise.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(
                {
                    'detail': 'Merchandise does not exist'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            # feedbacks = self.queryset.filter(merch_id=merch.id)
            # data = self.serializer_class(feedbacks, context={'request': request}, many=True).data
        try:
            feedback = self.queryset.get(merch_id=merch.id, user=request.user)
            data = self.serializer_class(feedback, context={'request': request}).data
            return Response(data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {
                    'merch_id': 0,
                    'text': '',
                    'username': '',
                    'user_profile_photo': ''
                },
                status=status.HTTP_200_OK
            )

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            merch = Merchandise.objects.get(pk=pk)
            feedback = self.queryset.get(user=request.user, merch=merch)
            feedback.delete()
            return Response(
                {
                    'merch_id': 0,
                    'text': '',
                    'username': '',
                    'user_profile_photo': ''
                },
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    'detail': 'Object does not exist'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        if not pk:
            return Response({}, status=status.HTTP_200_OK)
        PayPal().check_parallel_payment_status(pk)
        return Response(
            {
                'order_id': 0,
                'redirect_url': ''
            },
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        if not request.data['order_id']:
            return Response({'detail': 'order_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        pk = request.data['order_id']
        try:
            order = Order.objects.get(pk=pk)
        except:
            return Response(
                {
                    'detail': 'Order with id {0} does not exist'.format(pk)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.status != 0:
            return Response(
                {
                    'detail': 'Order status {0}'.format(order.status)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user != order.user:
            return Response(
                {
                    'detail': 'Buyer(in order) and current user dont match!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            transaction = PayTransactions.objects.get(order_id=order.id)
            if not transaction.pay_key:
                transaction.delete()
                raise ObjectDoesNotExist

            PayPal().check_parallel_payment_status(transaction.pay_key)
            transaction = PayTransactions.objects.get(order_id=order.id)
            if transaction.transaction_status == 'ERROR' or transaction.transaction_status == 'EXPIRED':
                transaction.delete()
                raise ObjectDoesNotExist

            if transaction.transaction_status == 'COMPLETED' or \
                    transaction.transaction_status == 'PROCESSING' or transaction.transaction_status == 'PENDING':
                return Response(
                    {
                        'detail': 'Order was payed'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if transaction.transaction_status == 'CREATED':
                return Response(
                    {
                        'order_id': request.data['order_id'],
                        'redirect_url': 'https://www.sandbox.paypal.com/webapps/adaptivepayment/flow/pay?paykey=' +
                                        transaction.pay_key + '&expType=mini'
                    },
                    status=status.HTTP_200_OK
                )
        except ObjectDoesNotExist:
            return Response(
                {
                    'order_id': request.data['order_id'],
                    'redirect_url': PayPal().create_parallel_payment(
                        order=order
                    )
                },
                status=status.HTTP_201_CREATED
            )
        except:
            return Response({'detail': 'failed'}, status=status.HTTP_400_BAD_REQUEST)


class VerificationCodeViewSet(viewsets.ViewSet):
    queryset = VerificationCode.objects.all()

    def create(self, request, pk=None):
        if 'verification_code' not in request.data:
            return Response(
                {
                    'detail': [
                        'Request must include field "verification_code".'
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        try:
            verification_code = self.queryset.get(user=user)
        except:
            return Response(
                {
                    'detail': 'failed'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if verification_code.attempt_count_left == 0:
            user.is_active = False
            user.save()
            return Response(
                {
                    'detail': 'Attempt count left is 0. Unable to verify user.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if verification_code.code == request.data['verification_code']:
            user.active = True
            user.save()
            verification_code.delete()
            return Response(
                {
                    "success": "User verified."
                },
                status=status.HTTP_200_OK
            )
        verification_code.attempt_count_left -= 1
        verification_code.save()
        if verification_code.attempt_count_left == 0:
            user.is_active = False
            user.save()
            return Response(
                {
                    'detail': 'Attempt count left is 0. Unable to verify user.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        verification_code_by_email(user)

        return Response(
            {
                "detail": "Attempt count left {0}. New verification code sent in email".format(
                    verification_code.attempt_count_left
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class TokenAuth(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        if 'username' not in request.data or 'password' not in request.data:
            return Response(
                {
                    'detail': ['Fields "username" and "passsword" is required!']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        username = request.data['username']
        password = request.data['password']

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    return Response(
                        {
                            'detail': 'User account is disabled.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                try:
                    user = User.objects.get(username=username)
                    user.failed_log += 1
                    if user.failed_log > 5:
                        user.active = False
                        verification_code_by_email(user)
                    user.save()
                finally:
                    return Response(
                        {
                            'Unable to log in with provided credentials.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response(
                {
                    'detail': 'Fields "username" and "password" cant be empty'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': user.id})


class SNAuth(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request, *args, **kwargs):
        if 'access_token' not in request.data or 'email' not in request.data or 'social_network' not in request.data:
            return Response(
                {
                    'detail': [
                        'Fields "social_network", "access_token", "email" is required.'
                    ]
                },
                status.HTTP_400_BAD_REQUEST
            )

        social_network = int(request.data['social_network'])
        email = request.data['email']
        access_token = request.data['access_token']
        if 'token_secret' in request.data:
            token_secret = request.data['token_secret']
        else:
            token_secret = None

        if not access_token or not email or not social_network:
            return Response(
                {
                    'detail': [
                        'Invalid value in field "access_token"/"social_id"/"email".'
                    ]
                },
                status.HTTP_400_BAD_REQUEST
            )
        if social_network < 0 or social_network > 3:
            return Response(
                {
                    'detail': 'Social type is not supported'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Try found id in SN
            social_account = self.get_social_account_user(social_network, access_token, token_secret)
            if social_network == 1:
                if not social_account or email not in [email_['value'] for email_ in social_account['emails']]:
                    return Response(
                        {
                            'detail': 'Invalid access to social network.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                sn_obj = SocialNetwork.objects.get(google=social_account['id'])
            elif social_network == 2:
                if not social_account or email != social_account['email']:
                    return Response(
                        {
                            'detail': 'Invalid access to social network.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                sn_obj = SocialNetwork.objects.get(facebook=social_account['id'])
            elif social_network == 3:
                if not social_account or email != social_account['email']:
                    return Response(
                        {
                            'detail': 'Invalid access to social network.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                sn_obj = SocialNetwork.objects.get(twitter=social_account['id'])

            try:
                # Try found account in Account
                account_obj = Account.objects.get(sn=sn_obj, email=email)
            except ObjectDoesNotExist:
                # Object Does Not Exist in Account Table with current email
                another_account = Account.objects.get(sn=sn_obj)
                account_obj = Account.objects.create(sn=sn_obj, user=another_account.user, email=email)

            user = User.objects.get(pk=account_obj.user.id)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': user.id}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            # Object Does Not Exist in SocialNetwork Table or in User Table
            try:
                # Try found Account with current email
                account_obj = Account.objects.get(email=email)
                sn_obj = SocialNetwork.objects.get(pk=account_obj.sn.id)
                if social_network == 1:
                    sn_obj.google = social_account['id']
                elif social_network == 2:
                    sn_obj.facebook = social_account['id']
                elif social_network == 3:
                    sn_obj.twitter = social_account['id']

                sn_obj.save()
                user = User.objects.get(id=account_obj.user.id)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'user': user.id}, status=status.HTTP_200_OK)
            except Exception as e:
                # This New User
                username = email
                try:
                    # Try create New User
                    user = User.objects.create_user(username=username, password=generate_random_sequence(20), email=email)
                    sn_obj = SocialNetwork.create_one_social(social_media_type=social_network,
                                                             social_media_id=social_account['id'])
                    Account.objects.create(user=user, sn=sn_obj, email=email)
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({'token': token.key, 'user': user.id}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({'detail': 'Failed. ' + e.__str__()[:100]},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'detail': 'Failed. ' + e.__str__()[:100]},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_social_account_user(socail_network, access_token, token_secret=None):
        if socail_network == 1:
            url = 'https://www.googleapis.com/plus/v1/people/me?access_token=' + access_token
        elif socail_network == 2:
            url = "https://graph.facebook.com/v2.8/me/?fields=name,email,first_name,last_name&access_token=" + access_token
        else:
            if not token_secret:
                return None

            api = TwitterAPI(
                CONSUMER_KEY,
                CONSUMER_SECRET,
                access_token,
                token_secret
            )
            try:
                content = api.request('account/verify_credentials', {'include_email': 'true'})
                return json.loads(content.text)
            except:
                return None
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/39.0.2171.95 Safari/537.36'
                   }

        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            content = json.loads(r.text)
            return content
        else:
            return None


class Registration(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request, *args, **kwargs):
        if 'username' not in request.data or 'password' not in request.data:
            return Response({'detail': ['Request must include fields "username", "password" and "email".']},
                            status=status.HTTP_400_BAD_REQUEST)

        username = email = request.data['username']
        password = request.data['password']

        if not username:
            return Response({'detail': 'username must be set'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'detail': 'password must be set'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User.objects.get(username=username)
            return Response({'detail': 'user with username %s is already exist' % username},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.active = False
            user.save()
            verification_code_by_email(user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': user.id}, status=status.HTTP_201_CREATED)


class ResetPass(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        if 'email' not in request.data:
            return Response(
                {
                    'detail': 'Request must include field "email"'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = self.queryset.get(email=request.data['email'])
            new_password = generate_random_sequence(10)
            user.set_password(new_password)
            user.save()
            sent_reset_password.delay(user.email, new_password)
            return Response(
                {
                    # 'detail': 'You password was reset. Check your email'
                    'email': ''
                },
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    'detail': 'User with email {0} does not exist'.format(request.data['email'])
                },
                status=status.HTTP_400_BAD_REQUEST
            )


token_auth = TokenAuth.as_view()
sn_auth = SNAuth.as_view()
registration = Registration.as_view()
reset_password = ResetPass.as_view()


# for rout seller/<seller_id>/merchandise/
@api_view(['GET'])
def seller_merchandise(request, *args, **kwargs):
    seller_id = kwargs.get('seller_id')
    try:
        seller = User.objects.get(pk=seller_id)
    except:
        return Response({'detail': 'user with id %s does not exist' % seller_id}, status=status.HTTP_400_BAD_REQUEST)
    if seller.role == 0:
        return Response({'detail': 'user with id %s isn`t seller' % seller_id}, status=status.HTTP_400_BAD_REQUEST)
    merchandises = Merchandise.objects.filter(seller=seller)
    merchandises_data = MerchandiseSerializer(merchandises, context={"request": request}, many=True).data
    return Response(merchandises_data, status=status.HTTP_200_OK)


# for rout seller/<seller_id>/order/
@api_view(['GET'])
def seller_orders(request, *args, **kwargs):
    seller_id = kwargs.get('seller_id')
    try:
        seller = User.objects.get(pk=seller_id)
    except:
        return Response({'detail': 'user with id %s does not exist' % seller_id})
    if seller.role == 0 or seller != request.user:
        return Response({'detail': 'Permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    orders = Order.objects.filter(seller=seller)
    orders_data = OrderSerializer(orders, context={"request": request}, many=True).data
    return Response(orders_data, status=status.HTTP_200_OK)


# for rout merchandise/<merch_id>/picture/
@api_view(['POST'])
def merchandise_photo_add(request, *args, **kwargs):
    id_merch = kwargs.get('merch_id')
    try:
        merchandise = Merchandise.objects.get(pk=id_merch)
    except:
        return Response(
            {'detail': 'merchandise id %s does not exist' % id_merch},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = request.user
    if user.id != merchandise.seller.id or user.role != 1:
        return Response({'detail': 'Permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if 'photo' in request.data:
        photo = request.FILES['photo']
        if len(photo):
            merch_photo = MerchPhoto.objects.create(
                merchandise=merchandise,
                photo_source_min=photo,
                photo_source_max=photo,
            )
            merch_photo.save()
            data = MerchPhotoSerializer(merch_photo, context={"request": request}).data
            return Response(data=data, status=status.HTTP_201_CREATED)
    return Response({}, status=status.HTTP_200_OK)


# for rout merchandise/<merch_id/picture/<id_picture>/
@api_view(['DELETE'])
def merchandise_photo_delete(request, *args, **kwargs):
    id_merch = kwargs.get('merch_id')
    try:
        merchandise = Merchandise.objects.get(pk=id_merch)
    except:
        return Response(
            {'detail': 'merchandise id %s does not exist' % id_merch},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = request.user
    if user.id != merchandise.seller.id or user.role != 1:
        return Response({'detail': 'Permissions denied'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    picture_id = kwargs.get('id_picture')
    try:
        photo = MerchPhoto.objects.get(pk=picture_id)
        photo.delete()
        return Response({}, status=status.HTTP_200_OK)
    except:
        return Response({'detail': 'Picture id %s does not exist'%picture_id}, status=status.HTTP_400_BAD_REQUEST)


# for rout payment/approve
@api_view(['GET', 'POST'])
def paypal_payment_approve(request, *args, **kwargs):
    payment_id = request.query_params.get('paymentId')
    payer_id = request.query_params.get('PayerID')
    if not payer_id or not payment_id:
        return Response({'detail': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
    json_response = PayPal().execute_payment(payment_id=payment_id, payer_id=payer_id)
    if 'state' in json_response:
        if json_response['state'] == 'approved':
            return Response(
                {
                    'payment status': 'approved'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'payment status': json_response['state']
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
    return Response(
        {
            'detail': 'payment already done'
        },
        status=status.HTTP_410_GONE
    )


# for rout payment/redirect
@api_view(['GET'])
def paypal_payment_redirect(request, *args, **kwargs):
    return Response({})


# for rout payment/cancel
@api_view(['GET', 'POST'])
def paypal_payment_cancel(request, *args, **kwargs):
    return Response({'detail': 'your payment was canceled'}, status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
def change_password(request, *args, **kwargs):
    if 'old_password' not in request.data or 'new_password' not in request.data:
        return Response(
            {
                'detail': [
                    'Request must include fields "old_password" and "new_password".'
                ]
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    old_pass = request.data['old_password']
    new_pass = request.data['new_password']
    if not old_pass or not new_pass:
        return Response(
            {
                'detail': [
                    'Fields "old_password" and "new_password" can`t be empty.'
                ]
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    user = authenticate(username=request.user.username, password=old_pass)
    if not user:
        return Response(
            {
                'detail': 'Old password invalid'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    user.set_password(new_pass)
    user.save()
    return Response(
        {
            'old_password': '',
            'new_password': ''
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def merchandise_feedbacks(request, *args, **kwargs):
    pk = kwargs.get('merch_id')
    try:
        merch = Merchandise.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response(
            {
                'detail': 'Merchandise does not exist'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        feedbacks = Feedback.objects.filter(merch_id=merch.id)
        data = FeedbackSerializer(feedbacks, context={'request': request}, many=True).data
        return Response(data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(
            [],
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
def merchandise_search(request):
    query = request.query_params.get('query', None)
    min_price = request.query_params.get('min_price', None)
    max_price = request.query_params.get('max_price', None)
    category_id = request.query_params.get('category')
    type_id = request.query_params.get('type')
    lat = request.query_params.get('lat', None)
    lon = request.query_params.get('lon', None)
    radius = request.query_params.get('radius', None)

    queryset = Merchandise.objects.all()
    if query:
        queryset = queryset.filter(name__icontains=query)
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if type_id:
        queryset = queryset.filter(type_id=type_id)

    if lat and lon and radius:
        try:
            new_query_set = list()
            for item in queryset:
                item_markers = Marker.objects.filter(merch=item)
                for marker in item_markers:
                    if distanse(float(lat.replace(',', '.')), float(lon.replace(',', '.')), marker.lat, marker.lon) <= float(radius.replace(',', '.')):
                        new_query_set.append(item)
                        break
            queryset = new_query_set
        except Exception as e:
            print(e)
            pass
    data = MerchandiseSerializer(queryset, many=True, context={'request':request}).data
    return Response(data)


@api_view(['DELETE'])
def company_delete(request, *args, **kwargs):
    try:
        company = Company.objects.get(id=kwargs.get('company_id'))
        company.delete_company(request.user)
        return Response()
    except ObjectDoesNotExist:
        return Response(
            {
                'detail': 'object does not exist'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except:
        return Response(
            {'detail': 'Permissions denied!'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
def address_delete(request, *args, **kwargs):
    try:
        address = UserAddress.objects.get(id=kwargs.get('address_id'))
        address.delete_address(request.user)
        return Response()
    except ObjectDoesNotExist:
        return Response(
            {
                'detail': 'object does not exist'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except:
        return Response(
            {'detail': 'Permissions denied!'},
            status=status.HTTP_400_BAD_REQUEST
        )


def generate_random_sequence(sequence_range):
    char_set = '123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM123456789'
    char_list = list(char_set)
    random.shuffle(char_list)
    result = ''.join([random.choice(char_list) for i in range(sequence_range)])
    return result


def verification_code_by_email(user):
    try:
        verification_code = VerificationCode.objects.get(user=user)
        verification_code.code = generate_random_sequence(6)
        verification_code.status = 0
        verification_code.save()
    except ObjectDoesNotExist:
        verification_code = VerificationCode.objects.create(
            user=user,
            code=generate_random_sequence(6),
            status=0
        )
        verification_code.save()
    sent_verification_code.delay(user.email, verification_code.id)


def distanse(lat1, long1, lat2, long2):
    rad = 6372795

    lat1 = lat1 * math.pi / 180.
    lat2 = lat2 * math.pi / 180.
    long1 = long1 * math.pi / 180.
    long2 = long2 * math.pi / 180.

    cl1 = math.cos(lat1)
    cl2 = math.cos(lat2)
    sl1 = math.sin(lat1)
    sl2 = math.sin(lat2)
    delta = long2 - long1
    cdelta = math.cos(delta)
    sdelta = math.sin(delta)

    y = math.sqrt(math.pow(cl2 * sdelta, 2) + math.pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
    x = sl1 * sl2 + cl1 * cl2 * cdelta
    ad = math.atan2(y, x)
    return ad * rad

