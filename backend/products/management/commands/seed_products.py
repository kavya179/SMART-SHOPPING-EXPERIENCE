"""
Management command to seed the database with sample beauty products.
All data is fictional sample data for demonstration purposes only.
This is NOT official Joyory inventory.

Usage:
    python manage.py seed_products
    python manage.py seed_products --clear   # clears existing products first
"""

from django.core.management.base import BaseCommand
from products.models import Product


SAMPLE_PRODUCTS = [
    # ── Skincare ─────────────────────────────────────────────────
    {
        'name': 'Radiance Vitamin C Serum',
        'brand': 'GlowEssentials',
        'category': 'skincare',
        'description': 'A brightening serum with 15% Vitamin C and Hyaluronic Acid that visibly reduces dark spots and boosts radiance.',
        'price': 899.00,
        'discount_percent': 15,
        'rating': 4.60,
        'review_count': 342,
        'image_url': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'all',
        'concern_tags': 'dark spots,dullness,uneven tone,brightening',
        'key_ingredients': 'Vitamin C (Ascorbic Acid), Hyaluronic Acid, Vitamin E, Ferulic Acid',
        'full_ingredients': 'Water, Ascorbic Acid, Propanediol, Hyaluronic Acid, Tocopherol, Ferulic Acid, Panthenol, Glycerin, Phenoxyethanol',
        'usage_instructions': 'Apply 3-4 drops to clean, damp skin every morning before moisturizer. Follow with SPF.',
        'caution_info': 'For external use only. Avoid direct sun exposure without SPF. Patch test before first use.',
        'availability': 'in_stock',
        'is_bestseller': True,
        'is_new_arrival': False,
    },
    {
        'name': 'Ultra Hydration Moisturizer',
        'brand': 'AquaSoft',
        'category': 'skincare',
        'description': 'Deep-hydrating gel cream with ceramides and squalane. Locks in 48-hour moisture without greasiness.',
        'price': 649.00,
        'discount_percent': 0,
        'rating': 4.40,
        'review_count': 218,
        'image_url': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'dry',
        'concern_tags': 'hydration,dryness,barrier repair',
        'key_ingredients': 'Ceramides, Squalane, Hyaluronic Acid, Shea Butter',
        'full_ingredients': 'Water, Squalane, Glycerin, Cetearyl Alcohol, Ceramide NP, Ceramide AP, Ceramide EOP, Butyrospermum Parkii Butter, Sodium Hyaluronate, Phenoxyethanol',
        'usage_instructions': 'Apply generously to face and neck morning and night after serum.',
        'caution_info': 'Discontinue use if irritation occurs.',
        'availability': 'in_stock',
        'is_bestseller': True,
        'is_new_arrival': False,
    },
    {
        'name': 'Clear Skin Niacinamide Gel',
        'brand': 'DermaClear',
        'category': 'skincare',
        'description': 'Oil-free gel with 10% Niacinamide and Zinc PCA to minimize pores and control excess oil.',
        'price': 475.00,
        'discount_percent': 10,
        'rating': 4.30,
        'review_count': 189,
        'image_url': 'https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'oily',
        'concern_tags': 'acne,oiliness,large pores,blemishes',
        'key_ingredients': 'Niacinamide 10%, Zinc PCA, Aloe Vera, Green Tea Extract',
        'full_ingredients': 'Water, Niacinamide, Zinc PCA, Aloe Barbadensis Leaf Juice, Camellia Sinensis Leaf Extract, Carbomer, Phenoxyethanol',
        'usage_instructions': 'Apply a thin layer on clean skin. Can be used morning and night.',
        'caution_info': 'Do not combine with pure Vitamin C in the same routine.',
        'availability': 'in_stock',
        'is_bestseller': False,
        'is_new_arrival': True,
    },
    {
        'name': 'Soothing Aloe Vera Gel',
        'brand': 'NatureCalm',
        'category': 'skincare',
        'description': 'Multi-purpose 99% pure aloe vera gel for soothing sunburns, redness, and irritation.',
        'price': 299.00,
        'discount_percent': 0,
        'rating': 4.10,
        'review_count': 467,
        'image_url': 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'sensitive',
        'concern_tags': 'redness,sunburn,irritation,soothing',
        'key_ingredients': 'Aloe Vera 99%, Vitamin E, Chamomile Extract',
        'full_ingredients': 'Aloe Barbadensis Leaf Juice, Glycerin, Tocopherol, Chamomilla Recutita Extract, Carbomer, Phenoxyethanol',
        'usage_instructions': 'Apply liberally to affected areas as needed. Can be refrigerated for a cooling effect.',
        'caution_info': 'Avoid contact with eyes. For external use only.',
        'availability': 'in_stock',
        'is_bestseller': False,
        'is_new_arrival': False,
    },

    # ── Haircare ─────────────────────────────────────────────────
    {
        'name': 'Keratin Smooth Shampoo',
        'brand': 'SilkStrand',
        'category': 'haircare',
        'description': 'Sulfate-free shampoo enriched with keratin protein and argan oil for frizz-free, silky hair.',
        'price': 550.00,
        'discount_percent': 20,
        'rating': 4.50,
        'review_count': 305,
        'image_url': 'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'all',
        'concern_tags': 'frizz,dryness,damage,smoothing',
        'key_ingredients': 'Keratin Protein, Argan Oil, Coconut Oil, Biotin',
        'full_ingredients': 'Water, Cocamidopropyl Betaine, Sodium Cocoyl Isethionate, Hydrolyzed Keratin, Argania Spinosa Kernel Oil, Cocos Nucifera Oil, Biotin, Glycerin, Phenoxyethanol',
        'usage_instructions': 'Massage into wet hair, lather, and rinse. Follow with conditioner for best results.',
        'caution_info': 'Avoid contact with eyes. Rinse immediately if contact occurs.',
        'availability': 'in_stock',
        'is_bestseller': True,
        'is_new_arrival': False,
    },
    {
        'name': 'Anti-Hairfall Conditioner',
        'brand': 'SilkStrand',
        'category': 'haircare',
        'description': 'Strengthening conditioner with biotin and caffeine to reduce breakage and add volume.',
        'price': 499.00,
        'discount_percent': 0,
        'rating': 4.20,
        'review_count': 176,
        'image_url': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'all',
        'concern_tags': 'hairfall,thinning,breakage,volume',
        'key_ingredients': 'Biotin, Caffeine, Castor Oil, Vitamin B5',
        'full_ingredients': 'Water, Cetearyl Alcohol, Behentrimonium Chloride, Biotin, Caffeine, Ricinus Communis Seed Oil, Panthenol, Glycerin, Phenoxyethanol',
        'usage_instructions': 'Apply to damp hair after shampooing. Leave on 2-3 minutes, then rinse thoroughly.',
        'caution_info': 'For external use only.',
        'availability': 'in_stock',
        'is_bestseller': False,
        'is_new_arrival': True,
    },

    # ── Makeup ───────────────────────────────────────────────────
    {
        'name': 'Velvet Matte Lipstick — Rose Berry',
        'brand': 'ColorPop Studio',
        'category': 'makeup',
        'description': 'Long-lasting matte lipstick with a velvety finish. Enriched with jojoba oil to keep lips hydrated.',
        'price': 399.00,
        'discount_percent': 0,
        'rating': 4.70,
        'review_count': 521,
        'image_url': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'all',
        'concern_tags': 'long-lasting,matte finish,hydrating',
        'key_ingredients': 'Jojoba Oil, Vitamin E, Candelilla Wax',
        'full_ingredients': 'Isododecane, Dimethicone, Trimethylsiloxysilicate, Simmondsia Chinensis Seed Oil, Tocopherol, Candelilla Cera, CI 15850, CI 77891',
        'usage_instructions': 'Apply directly to lips. For precision, use with a lip liner.',
        'caution_info': 'Keep out of reach of children. Do not use on broken or irritated skin.',
        'availability': 'in_stock',
        'is_bestseller': True,
        'is_new_arrival': False,
    },
    {
        'name': 'Flawless Foundation SPF 25 — Natural Beige',
        'brand': 'ColorPop Studio',
        'category': 'makeup',
        'description': 'Medium-to-full coverage liquid foundation with SPF 25. Blends seamlessly for a natural, flawless look.',
        'price': 750.00,
        'discount_percent': 10,
        'rating': 4.30,
        'review_count': 284,
        'image_url': 'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'combination',
        'concern_tags': 'coverage,sun protection,even tone',
        'key_ingredients': 'SPF 25 Filters, Hyaluronic Acid, Niacinamide',
        'full_ingredients': 'Water, Cyclopentasiloxane, Titanium Dioxide, Ethylhexyl Methoxycinnamate, Niacinamide, Sodium Hyaluronate, Iron Oxides, Glycerin, Phenoxyethanol',
        'usage_instructions': 'Shake well. Apply with fingers, brush, or sponge. Build coverage as desired.',
        'caution_info': 'Reapply every 2-3 hours if relying on SPF protection alone.',
        'availability': 'in_stock',
        'is_bestseller': False,
        'is_new_arrival': True,
    },

    # ── Fragrance ────────────────────────────────────────────────
    {
        'name': 'Midnight Bloom Eau de Parfum',
        'brand': 'Aura Luxe',
        'category': 'fragrance',
        'description': 'An enchanting floral-oriental fragrance with notes of jasmine, vanilla, and sandalwood.',
        'price': 1299.00,
        'discount_percent': 5,
        'rating': 4.80,
        'review_count': 156,
        'image_url': 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'all',
        'concern_tags': 'long-lasting,evening wear,floral,oriental',
        'key_ingredients': 'Jasmine Absolute, Vanilla Bean, Sandalwood Oil, Musk',
        'full_ingredients': 'Alcohol Denat., Parfum (Fragrance), Aqua, Jasminum Grandiflorum Flower Extract, Vanilla Planifolia Fruit Extract, Santalum Album Oil, Linalool, Coumarin',
        'usage_instructions': 'Spray on pulse points — wrists, neck, behind ears. Do not rub.',
        'caution_info': 'Flammable. Avoid spraying near eyes. Keep away from open flames.',
        'availability': 'in_stock',
        'is_bestseller': False,
        'is_new_arrival': True,
    },

    # ── Body Care ────────────────────────────────────────────────
    {
        'name': 'Cocoa Butter Body Lotion',
        'brand': 'BodyBliss',
        'category': 'bodycare',
        'description': 'Rich, non-greasy body lotion with cocoa butter and coconut oil for all-day nourishment.',
        'price': 425.00,
        'discount_percent': 0,
        'rating': 4.40,
        'review_count': 390,
        'image_url': 'https://images.unsplash.com/photo-1556228722-d0b5d1589b23?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'dry',
        'concern_tags': 'dryness,nourishment,softness,winter care',
        'key_ingredients': 'Cocoa Butter, Coconut Oil, Shea Butter, Vitamin E',
        'full_ingredients': 'Water, Theobroma Cacao Seed Butter, Cocos Nucifera Oil, Butyrospermum Parkii Butter, Glycerin, Tocopherol, Cetearyl Alcohol, Phenoxyethanol, Parfum',
        'usage_instructions': 'Apply generously all over body after shower while skin is still slightly damp.',
        'caution_info': 'For external use only. Discontinue if rash or irritation develops.',
        'availability': 'in_stock',
        'is_bestseller': False,
        'is_new_arrival': False,
    },
    {
        'name': 'Charcoal Detox Body Scrub',
        'brand': 'PureGrit',
        'category': 'bodycare',
        'description': 'Exfoliating body scrub with activated charcoal and walnut shell to remove dead skin and impurities.',
        'price': 375.00,
        'discount_percent': 15,
        'rating': 4.10,
        'review_count': 142,
        'image_url': 'https://images.unsplash.com/photo-1567928815104-b7980ee5032e?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'normal',
        'concern_tags': 'exfoliation,detox,deep cleansing,blackheads',
        'key_ingredients': 'Activated Charcoal, Walnut Shell Powder, Tea Tree Oil, Aloe Vera',
        'full_ingredients': 'Water, Juglans Regia Shell Powder, Charcoal Powder, Glycerin, Melaleuca Alternifolia Leaf Oil, Aloe Barbadensis Leaf Juice, Cetearyl Alcohol, Phenoxyethanol',
        'usage_instructions': 'Massage onto wet skin in circular motions. Rinse thoroughly. Use 2-3 times per week.',
        'caution_info': 'Not suitable for very sensitive or broken skin. Avoid face area.',
        'availability': 'low_stock',
        'is_bestseller': False,
        'is_new_arrival': False,
    },

    # ── Nail Care ────────────────────────────────────────────────
    {
        'name': 'Gel Effect Nail Polish — Cherry Red',
        'brand': 'NailGlam',
        'category': 'nailcare',
        'description': 'High-shine gel-effect nail polish with a chip-resistant formula. No UV lamp required.',
        'price': 199.00,
        'discount_percent': 0,
        'rating': 4.00,
        'review_count': 88,
        'image_url': 'https://images.unsplash.com/photo-1632345031435-8727f6897d53?auto=format&fit=crop&w=600&q=80',
        'skin_type': 'all',
        'concern_tags': 'long-lasting,chip-resistant,glossy',
        'key_ingredients': 'Biotin, Calcium, Keratin',
        'full_ingredients': 'Butyl Acetate, Ethyl Acetate, Nitrocellulose, Adipic Acid/Neopentyl Glycol/Trimellitic Anhydride Copolymer, Isopropyl Alcohol, Biotin, Calcium Pantothenate',
        'usage_instructions': 'Apply base coat. Apply 2 thin coats of color. Finish with top coat for maximum shine.',
        'caution_info': 'Keep away from heat. Use in well-ventilated area. Keep out of reach of children.',
        'availability': 'in_stock',
        'is_bestseller': False,
        'is_new_arrival': False,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with sample beauty products (demo data only, not official Joyory inventory).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing products before seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Product.objects.count()
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing product(s).'))

        created = 0
        skipped = 0
        for data in SAMPLE_PRODUCTS:
            obj, was_created = Product.objects.get_or_create(
                name=data['name'],
                brand=data['brand'],
                defaults=data,
            )
            if was_created:
                created += 1
            else:
                # Update existing products with new image_url
                for key, value in data.items():
                    setattr(obj, key, value)
                obj.save()
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeding complete: {created} updated/created.'
        ))
