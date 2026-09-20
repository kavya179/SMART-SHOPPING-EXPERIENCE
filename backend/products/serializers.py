from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Full serializer for the Product model.
    Includes computed fields: discounted_price and concern_list.
    """
    discounted_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    concern_list = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'brand',
            'category',
            'description',
            'price',
            'discount_percent',
            'discounted_price',
            'rating',
            'review_count',
            'image_url',
            'skin_type',
            'concern_tags',
            'concern_list',
            'key_ingredients',
            'full_ingredients',
            'usage_instructions',
            'caution_info',
            'availability',
            'is_bestseller',
            'is_new_arrival',
            'created_at',
            'updated_at',
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lighter serializer for list views — omits heavy text fields
    (full_ingredients, usage_instructions, caution_info) for performance.
    """
    discounted_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'brand',
            'category',
            'description',
            'price',
            'discount_percent',
            'discounted_price',
            'rating',
            'review_count',
            'image_url',
            'skin_type',
            'concern_tags',
            'key_ingredients',
            'availability',
            'is_bestseller',
            'is_new_arrival',
        ]
