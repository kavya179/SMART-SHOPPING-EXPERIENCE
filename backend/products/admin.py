from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for managing products in Django admin."""

    list_display = (
        'name',
        'brand',
        'category',
        'price',
        'discount_percent',
        'rating',
        'skin_type',
        'availability',
        'is_bestseller',
        'is_new_arrival',
    )
    list_filter = (
        'category',
        'skin_type',
        'availability',
        'is_bestseller',
        'is_new_arrival',
    )
    search_fields = ('name', 'brand', 'description', 'key_ingredients')
    list_editable = ('price', 'discount_percent', 'availability', 'is_bestseller', 'is_new_arrival')
    list_per_page = 25

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'brand', 'category', 'description', 'image_url'),
        }),
        ('Pricing & Rating', {
            'fields': ('price', 'discount_percent', 'rating', 'review_count'),
        }),
        ('Tags & Classification', {
            'fields': ('skin_type', 'concern_tags'),
        }),
        ('Ingredients & Usage', {
            'fields': ('key_ingredients', 'full_ingredients', 'usage_instructions', 'caution_info'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('availability', 'is_bestseller', 'is_new_arrival'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
