from django.utils import timezone
from re import sub
from rest_framework.authtoken.models import Token


class UserActivityLoggerMiddleware(object):
    def process_request(self, request):
        header_token = request.META.get('HTTP_AUTHORIZATION', None)
        if header_token is not None:
            try:
                token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
                user.last_activity = timezone.now()
                if not user.online:
                    user.online = True
                user.save()
            except Token.DoesNotExist:
                pass
