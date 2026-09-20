from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product-list'),
    path('categories/', views.category_list, name='category-list'),
    path('recommend/', views.recommend_products, name='product-recommend'),
    path('faq/', views.faq_query, name='product-faq'),
    path('<int:pk>/', views.product_detail, name='product-detail'),
]
