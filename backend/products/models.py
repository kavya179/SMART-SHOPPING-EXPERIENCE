from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):
    """
    Comprehensive product model for beauty and personal-care items.
    All data is sample/demo data — not official Joyory inventory.
    """

    # ── Category choices ─────────────────────────────────────────
    CATEGORY_CHOICES = [
        ('skincare', 'Skincare'),
        ('haircare', 'Haircare'),
        ('makeup', 'Makeup'),
        ('fragrance', 'Fragrance'),
        ('bodycare', 'Body Care'),
        ('nailcare', 'Nail Care'),
        ('tools', 'Tools & Accessories'),
    ]

    # ── Skin-type / intended-use tags ────────────────────────────
    SKIN_TYPE_CHOICES = [
        ('all', 'All Skin Types'),
        ('oily', 'Oily'),
        ('dry', 'Dry'),
        ('combination', 'Combination'),
        ('sensitive', 'Sensitive'),
        ('normal', 'Normal'),
    ]

    # ── Availability status ──────────────────────────────────────
    AVAILABILITY_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]

    # ── Core fields ──────────────────────────────────────────────
    name = models.CharField(
        max_length=250,
        help_text='Product display name',
    )
    brand = models.CharField(
        max_length=120,
        help_text='Brand or manufacturer name',
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        db_index=True,
        help_text='Primary product category',
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text='Short marketing description',
    )

    # ── Pricing ──────────────────────────────────────────────────
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Price in INR (₹)',
    )
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text='Discount percentage (0-100)',
    )

    # ── Rating ───────────────────────────────────────────────────
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Average rating (0.00 – 5.00)',
    )
    review_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of customer reviews',
    )

    # ── Image ────────────────────────────────────────────────────
    image_url = models.URLField(
        blank=True,
        default='',
        help_text='URL to product image (external or placeholder)',
    )

    # ── Tags ─────────────────────────────────────────────────────
    skin_type = models.CharField(
        max_length=50,
        choices=SKIN_TYPE_CHOICES,
        default='all',
        help_text='Intended skin type',
    )
    concern_tags = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text='Comma-separated concern tags, e.g. "acne,dark spots,hydration"',
    )

    # ── Ingredient & usage information ───────────────────────────
    key_ingredients = models.TextField(
        blank=True,
        default='',
        help_text='Key active ingredients (comma-separated or free text)',
    )
    full_ingredients = models.TextField(
        blank=True,
        default='',
        help_text='Complete INCI ingredient list',
    )
    usage_instructions = models.TextField(
        blank=True,
        default='',
        help_text='How to use this product',
    )
    caution_info = models.TextField(
        blank=True,
        default='',
        help_text='Warnings, allergens, or contraindications',
    )

    # ── Availability ─────────────────────────────────────────────
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='in_stock',
        db_index=True,
        help_text='Current stock status',
    )

    # ── Metadata ─────────────────────────────────────────────────
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.name} — {self.brand}"

    @property
    def discounted_price(self):
        """Return the price after discount (if any)."""
        if self.discount_percent > 0:
            factor = Decimal(1) - Decimal(self.discount_percent) / Decimal(100)
            return round(self.price * factor, 2)
        return self.price

    @property
    def concern_list(self):
        """Return concern_tags as a Python list."""
        if self.concern_tags:
            return [tag.strip() for tag in self.concern_tags.split(',') if tag.strip()]
        return []
