"""
WSGI config for sales_platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys
import site

from django.core.wsgi import get_wsgi_application

#site.addsitedir('sales_platform/core')
#site.addsitedir('sales_platform/api')
#sys.path.append('/apps/genesis/incode.sales_platform/backend/')
#sys.path.append('/apps/genesis/incode.sales_platform/backend/sales_platform/settings')

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sales_platform.settings")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sales_platform.settings")

application = get_wsgi_application()
