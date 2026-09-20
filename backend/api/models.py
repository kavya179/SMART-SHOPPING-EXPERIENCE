from django.db import models


class Product(models.Model):
    """
    A beauty / personal-care product.
    This is the core model for Phase 1 — just enough to prove the
    Django ORM + SQLite + DRF pipeline works end-to-end.
    """

    CATEGORY_CHOICES = [
        ('skincare', 'Skincare'),
        ('haircare', 'Haircare'),
        ('makeup', 'Makeup'),
        ('fragrance', 'Fragrance'),
        ('bodycare', 'Body Care'),
    ]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    image_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} by {self.brand}"
