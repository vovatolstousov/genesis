import os
from django.db import models
from ..users.models import CustomUser
from django.utils import timezone
from ..helpers import resize_photo
from os import path

MERCH = (
    (0, 'product'),
    (1, 'service')
)


class Category(models.Model):
    name = models.TextField(default="default")
    icon = models.ImageField("category_icon", null=True, blank=True,
                             upload_to=path.join('photo', 'merchandise', 'category', 'icons'),)
    image = models.ImageField("category_image", null=True, blank=True, upload_to=path.join('photo', 'merchandise',
                                                                                           'category', 'images'))

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        if self.icon:
            resize_photo(self, max_thumbnail_size=100, filename=self.icon.path,
                         width=self.icon.width, height=self.icon.height)
        if self.image:
            resize_photo(self, max_thumbnail_size=300, filename=self.image.path,
                         width=self.image.width, height=self.image.height)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Type(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.TextField(default="default")

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Types'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Merchandise(models.Model):
    name = models.TextField(default='Item')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    seller_email = models.EmailField(blank=True, null=True)
    preview_photo = models.ImageField("merch_preview_photo", null=True, blank=True,
                                      upload_to=path.join('photo', 'merchandise', 'preview_photo'),
                                      max_length=500)
    description = models.TextField(blank=True)
    merchandise = models.IntegerField(choices=MERCH, default=0)
    price = models.FloatField(default=1)
    count = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    average_rating = models.FloatField(blank=True, null=True)
    rating_count_votes = models.PositiveIntegerField(blank=True, default=0)
    created_date = models.DateTimeField(auto_created=True)
    video_url = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_date = timezone.now()
        super(Merchandise, self).save(*args, **kwargs)
        if self.preview_photo:
            resize_photo(self, max_thumbnail_size=200, filename=self.preview_photo.path,
                         width=self.preview_photo.width, height=self.preview_photo.height)
        # return super(Merchandise, self).save(*args, **kwargs)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Merchandises'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Feedback(models.Model):
    merch = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)
    text = models.TextField(max_length=1000, blank=False)
    user_profile_photo = models.ImageField(
        "feedbacks_user_photo", null=True, blank=True, max_length=500,
        upload_to=path.join('photo', 'merchandise', 'feedback', 'user_profile_photo')
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_date = timezone.now()
        return super(Feedback, self).save(*args, **kwargs)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        return 'Feedback id {1} by username {2} on merch {3} with text: {0}... '.format(
            self.text[:10], self.pk, self.username, self.merch
        )

    def __unicode__(self):
        return self.text

    def delete(self, using=None, keep_parents=False):
        if self.user_profile_photo:
            os.remove(self.user_profile_photo.path)
        return super(Feedback, self).delete(using, keep_parents)


class Tag(models.Model):
    name = models.TextField(default='')

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class MerchTag(models.Model):
    merch = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        app_label = 'sales_platform'

    def __str__(self):
        return 'Merch %s, Tag %s' % self.merch, self.tag


class Marker(models.Model):
    merch = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    lat = models.FloatField(default=0)
    lon = models.FloatField(default=0)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Markers'

    def __str__(self):
        return 'id {0}. Lat.:{1}, Lon.:{2}'.format(self.pk, self.lat, self.lon)


class MarkerAddress(models.Model):
    marker = models.OneToOneField(Marker, on_delete=models.CASCADE, related_name='merchandise_marker_address')
    country = models.TextField(default='Singapore')
    country_code = models.CharField(max_length=5, blank=True)
    city = models.TextField(null=True)
    street = models.TextField(blank=True)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'MarkerAddress'

    def __str__(self):
        return 'id {0}, {1}, {2}, {3}'.format(self.pk, self.country, self.city, self.street)


class MerchPhoto(models.Model):
    merchandise = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    photo_source_min = models.ImageField("merch_photo_source_min", null=True, blank=True,
                                         upload_to=path.join('photo', 'merchandise', 'merchandise_photo', 'min'),)
    photo_source_max = models.ImageField("merch_photo_source_max", null=True, blank=True,
                                         upload_to=path.join('photo', 'merchandise', 'merchandise_photo', 'max'),)

    def save(self, *args, **kwargs):
        super(MerchPhoto, self).save(*args, **kwargs)
        if self.photo_source_min:
            resize_photo(self, max_thumbnail_size=200, filename=self.photo_source_min.path,
                         width=self.photo_source_min.width, height=self.photo_source_min.height)
        if self.photo_source_max:
            resize_photo(self, max_thumbnail_size=800, filename=self.photo_source_max.path,
                         width=self.photo_source_max.width, height=self.photo_source_max.height)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Photo'

    def __str__(self):
        return 'Photo id {0}, merchandise {1}, name file: {2}'.format(self.id, self.merchandise.name, self.photo_source_max)


class Rating(models.Model):
    user = models.ForeignKey(CustomUser, null=True)
    merch = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0)
    created_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_date = timezone.now()
        return super(Rating, self).save(*args, **kwargs)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Ratings'

    def __str__(self):
        return 'Rating id {0} user {1}, merchandise {2}, stars count {3}'.format(self.pk, self.user, self.merch, self.stars)