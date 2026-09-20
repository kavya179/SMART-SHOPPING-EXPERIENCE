"""
WSGI config for Joyory SmartMatch project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartmatch.settings')
application = get_wsgi_application()
