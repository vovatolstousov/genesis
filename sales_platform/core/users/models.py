from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from datetime import datetime, timedelta
from django.utils import timezone
from os import path
from ..helpers import resize_photo

ROLES = (
    (0, 'buyer'),
    (1, 'seller'),
)

GENDERS = (
    (0, 'male'),
    (1, 'female'),
    (2, 'different')
)

# class CustomUserManager(UserManager):
#     pass


class CustomUser(AbstractUser):
    contact_number = models.TextField(max_length=15, blank=True)
    profile_photo = models.ImageField("profile_photo", upload_to=path.join('photo', 'profile_photo'),
                                      null=True, blank=True,)
    role = models.IntegerField(choices=ROLES, default=0)
    failed_log = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    gender = models.IntegerField(choices=GENDERS, default=2)
    online = models.BooleanField(default=False)
    birthday = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.last_activity = timezone.now()
        super(CustomUser, self).save(*args, **kwargs)
        if self.profile_photo:
            resize_photo(self, max_thumbnail_size=640, filename=self.profile_photo.path,
                         width=self.profile_photo.width, height=self.profile_photo.height,)

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        app_label = 'sales_platform'
        swappable = 'AUTH_USER_MODEL'
        verbose_name_plural = 'CustomUsers'


class UserAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    country = models.TextField(max_length=60, default='Singapore')
    country_code = models.CharField(max_length=5, blank=True)
    city = models.TextField(max_length=60, blank=True)
    street = models.TextField(max_length=60, blank=True)
    post_code = models.TextField(max_length=10, blank=True)

    def __str__(self):
        return '{0} address: {1}, {2}'.format(self.user, self.country, self.city)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'UserAddress'

    def delete_address(self, user):
        if user == self.user:
            super(UserAddress, self).delete()
        else:
            raise Exception('Permission denied!')


class SocialNetwork(models.Model):
    # google = models.BigIntegerField(blank=True, null=True)
    # facebook = models.BigIntegerField(blank=True, null=True)
    # twitter = models.BigIntegerField(blank=True, null=True)
    # instagram = models.BigIntegerField(blank=True, null=True)

    google = models.TextField(blank=True, null=True)
    facebook = models.TextField(blank=True, null=True)
    twitter = models.TextField(blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'SocialNetworks'

    def __str__(self):
        return 'sn id {0}'.format(self.id)

    def __unicode__(self):
        return 'sn id {0}'.format(self.id)

    @classmethod
    def create_one_social(cls, social_media_type, social_media_id):
        social_network = cls()

        if social_media_type == 1:
            social_network = cls(google=social_media_id)
        elif social_media_type == 2:
            social_network = cls(facebook=social_media_id)
        elif social_media_type == 3:
            social_network = cls(twitter=social_media_id)
        elif social_media_type == 4:
            social_network = cls(instagram=social_media_id)
        else:
            return None

        social_network.save()
        return social_network


class Account(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sn = models.ForeignKey(SocialNetwork, null=True)
    email = models.EmailField(default="")

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return "email: {0} for user id {1} with sn id {2}".format(self.email, self.user_id, self.sn_id)

    def __unicode__(self):
        return "email: {0} for user id {1} with sn id {2}".format(self.email, self.user_id, self.sn_id)


class Company(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.TextField(max_length=100, default="")
    industry = models.TextField(max_length=50, blank=True)
    country = models.TextField(max_length=60, blank=True)
    country_code = models.CharField(max_length=5, blank=True)
    city = models.TextField(max_length=60, blank=True)
    post_code = models.TextField(max_length=10, blank=True)
    contact_number = models.TextField(max_length=20, blank=True)
    fax_number = models.TextField(max_length=30, blank=True)
    enquiry_email = models.TextField(max_length=100, blank=True)

    class Meta:
        app_label = 'sales_platform'
        verbose_name_plural = 'Company'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def delete_company(self, user):
        if user == self.user:
            super(Company, self).delete()
        else:
            raise Exception('Permission denied!')


class VerificationCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, default="")
    status = models.IntegerField(choices=((0, 'awaiting'), (1, 'sent'), (2, 'error')), default=0)
    attempt_count_left = models.IntegerField(default=5)
    create_date = models.DateTimeField(default=timezone.now())

    class Meta:
        app_label = 'sales_platform'

    def __str__(self):
        return 'Code status {2}: {0} for user {1}. Attempt left {3}'.format(
            self.code, self.user, self.status, self.attempt_count_left
        )
