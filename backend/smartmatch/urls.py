"""
Root URL configuration for Joyory SmartMatch.
"""

from django.contrib import admin
from django.urls import path, include

from products.views import recommend_products, faq_query

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/products/', include('products.urls')),
    path('api/recommendations/', recommend_products, name='api-recommendations'),
    path('api/faq/', faq_query, name='api-faq'),
]
