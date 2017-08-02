from rest_framework import serializers
from .models import Merchandise, Type, Category, Feedback, Tag, MerchTag, Marker, MarkerAddress, MerchPhoto, Rating


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'user_id', 'created_date', 'text', 'username', 'user_profile_photo')


class MarkerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkerAddress
        fields = ('country', 'country_code', 'city', 'street')


class MarkerSerializer(serializers.ModelSerializer):
    # address = MarkerAddressSerializer(source='markeraddress_set', many=True)
    address = MarkerAddressSerializer(many=False, read_only=True, source='merchandise_marker_address')

    class Meta:
        model = Marker
        fields = ('id', 'lat', 'lon',  'address', )


class MerchPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchPhoto
        fields = ('id', 'photo_source_min', 'photo_source_max')


class MerchandiseSerializer(serializers.ModelSerializer):
    # feedbacks = FeedbackSerializer(source='feedback_set', many=True)
    list_markers = MarkerSerializer(source='marker_set', many=True)
    photo = MerchPhotoSerializer(source='merchphoto_set', many=True, read_only=True)

    class Meta:
        model = Merchandise
        fields = ('id', 'name', 'description', 'merchandise', 'price', 'count',
                  'category_id', 'type_id', 'photo', 'preview_photo', 'seller', 'seller_email', 'list_markers', 'video_url',
                  'average_rating')


class TypeMerchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchandise
        fields = ('id', 'name', 'price', 'preview_photo', 'type_id')


class TypeSerializer(serializers.ModelSerializer):
    merchs = TypeMerchSerializer(source='merchandise_set', many=True)

    class Meta:
        model = Type
        fields = ('id', 'name', 'category_id', 'merchs')


class CategotyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ('id', 'name')


class CategorySerializer(serializers.ModelSerializer):
    types = CategotyTypeSerializer(source='type_set', many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'types', 'icon', 'image')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


class MerchTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchTag
        fields = ('id', 'merch_id', 'tag_id')


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('id', 'stars', 'merch_id')
