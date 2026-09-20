from django.test import TestCase
from rest_framework.test import APIClient
from decimal import Decimal
from .models import Product


class ProductModelTest(TestCase):
    """Tests for the Product model."""

    def setUp(self):
        self.product = Product.objects.create(
            name='Hydrating Face Cream',
            brand='SampleBrand',
            category='skincare',
            description='A lightweight moisturizer.',
            price=Decimal('499.00'),
            discount_percent=10,
            rating=Decimal('4.50'),
            review_count=120,
            skin_type='dry',
            concern_tags='hydration,dryness,anti-aging',
            key_ingredients='Hyaluronic Acid, Vitamin E',
            availability='in_stock',
        )

    def test_str_representation(self):
        self.assertEqual(str(self.product), 'Hydrating Face Cream — SampleBrand')

    def test_discounted_price(self):
        self.assertEqual(self.product.discounted_price, Decimal('449.10'))

    def test_concern_list(self):
        self.assertEqual(
            self.product.concern_list,
            ['hydration', 'dryness', 'anti-aging'],
        )

    def test_discounted_price_no_discount(self):
        self.product.discount_percent = 0
        self.assertEqual(self.product.discounted_price, Decimal('499.00'))


class ProductAPITest(TestCase):
    """Tests for the product API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.p1 = Product.objects.create(
            name='Glow Serum',
            brand='GlowCo',
            category='skincare',
            price=Decimal('799.00'),
            rating=Decimal('4.20'),
            skin_type='oily',
            concern_tags='acne,oiliness',
            availability='in_stock',
        )
        self.p2 = Product.objects.create(
            name='Volume Shampoo',
            brand='HairLux',
            category='haircare',
            price=Decimal('350.00'),
            rating=Decimal('3.80'),
            skin_type='all',
            concern_tags='volume,thinning',
            availability='in_stock',
        )

    # ── List endpoint ────────────────────────────────────────────
    def test_product_list_returns_all(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_category(self):
        response = self.client.get('/api/products/?category=skincare')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Glow Serum')

    def test_filter_by_price_range(self):
        response = self.client.get('/api/products/?min_price=400&max_price=900')
        self.assertEqual(response.data['count'], 1)

    def test_search(self):
        response = self.client.get('/api/products/?search=shampoo')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['brand'], 'HairLux')

    def test_invalid_min_price(self):
        response = self.client.get('/api/products/?min_price=abc')
        self.assertEqual(response.status_code, 400)

    # ── Detail endpoint ──────────────────────────────────────────
    def test_product_detail(self):
        response = self.client.get(f'/api/products/{self.p1.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Glow Serum')

    def test_product_not_found(self):
        response = self.client.get('/api/products/9999/')
        self.assertEqual(response.status_code, 404)

    # ── Categories endpoint ──────────────────────────────────────
    def test_category_list(self):
        response = self.client.get('/api/products/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


class RecommendationTests(TestCase):
    """Tests for the rule-based recommendation engine and API."""

    def setUp(self):
        self.client = APIClient()
        self.serum = Product.objects.create(
            name='Radiance Vitamin C Serum',
            brand='GlowEssentials',
            category='skincare',
            description='Brightening serum with Vitamin C and Hyaluronic Acid for radiant skin.',
            price=Decimal('899.00'),
            discount_percent=15,
            rating=Decimal('4.60'),
            review_count=342,
            skin_type='all',
            concern_tags='dark spots,dullness,brightening',
            key_ingredients='Vitamin C, Hyaluronic Acid',
            availability='in_stock',
            is_bestseller=True,
        )
        self.cream = Product.objects.create(
            name='Ultra Hydration Cream',
            brand='AquaSoft',
            category='skincare',
            description='Moisturizer with ceramides for dry skin barrier repair.',
            price=Decimal('500.00'),
            discount_percent=0,
            rating=Decimal('4.40'),
            review_count=218,
            skin_type='dry',
            concern_tags='dryness,hydration,barrier repair',
            key_ingredients='Ceramides, Squalane',
            availability='in_stock',
        )
        self.shampoo = Product.objects.create(
            name='Keratin Smooth Shampoo',
            brand='SilkStrand',
            category='haircare',
            description='Sulfate-free shampoo with keratin for frizz-free hair.',
            price=Decimal('400.00'),
            discount_percent=10,
            rating=Decimal('4.50'),
            review_count=300,
            skin_type='all',
            concern_tags='frizz,dryness,smoothing',
            key_ingredients='Keratin, Argan Oil',
            availability='in_stock',
        )

    def test_exact_skincare_match(self):
        payload = {
            'category': 'skincare',
            'skin_type': 'dry',
            'concern': 'dryness',
            'budget_max': 600,
        }
        response = self.client.post('/api/products/recommend/', payload, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertFalse(data['is_alternative'])
        self.assertGreater(len(data['recommendations']), 0)
        # Top match should be the dry skin hydration cream
        top_match = data['recommendations'][0]
        self.assertEqual(top_match['product']['name'], 'Ultra Hydration Cream')
        self.assertGreater(top_match['match_percentage'], 70)
        self.assertTrue(len(top_match['reasons']) > 0)

    def test_category_adaptive_haircare_match(self):
        payload = {
            'category': 'haircare',
            'concern': 'frizz',
            'budget_max': 500,
        }
        response = self.client.post('/api/recommendations/', payload, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['recommendations'][0]['product']['name'], 'Keratin Smooth Shampoo')
        self.assertIn('Keratin', data['recommendations'][0]['product']['key_ingredients'])

    def test_ingredient_preference_boost(self):
        payload = {
            'category': 'skincare',
            'concern': 'brightening',
            'preferred_ingredients': ['vitamin c'],
        }
        response = self.client.post('/api/products/recommend/', payload, format='json')
        self.assertEqual(response.status_code, 200)
        top_product = response.data['recommendations'][0]['product']
        self.assertEqual(top_product['name'], 'Radiance Vitamin C Serum')

    def test_low_budget_returns_alternatives_with_explanation(self):
        payload = {
            'category': 'skincare',
            'concern': 'brightening',
            'budget_max': 100,  # Below all products
        }
        response = self.client.post('/api/products/recommend/', payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_alternative'])
        self.assertIn('No exact match was found', response.data['message'])
        self.assertGreater(len(response.data['recommendations']), 0)

    def test_invalid_negative_budget(self):
        payload = {
            'category': 'skincare',
            'budget_max': -50,
        }
        response = self.client.post('/api/products/recommend/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_invalid_body_type(self):
        response = self.client.post('/api/products/recommend/', ['invalid', 'list'], format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)


class FaqAssistantTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.serum = Product.objects.create(
            name='Radiance Vitamin C Serum',
            brand='GlowLab',
            category='skincare',
            description='Potent antioxidant serum.',
            price=Decimal('899.00'),
            skin_type='all',
            concern_tags='dark spots,dullness,brightening',
            key_ingredients='Vitamin C, Hyaluronic Acid',
            full_ingredients='Aqua, 15% Ethyl Ascorbic Acid, Sodium Hyaluronate, Ferulic Acid.',
            usage_instructions='Apply 3-4 drops in the morning on cleansed face before moisturizer and SPF.',
            caution_info='Perform patch test prior to first use. Slight tingling may occur. Use sunscreen during daytime.',
            availability='in_stock',
        )
        self.cream = Product.objects.create(
            name='Ultra Hydration Cream',
            brand='AquaSoft',
            category='skincare',
            description='Moisturizer with ceramides for dry skin barrier repair.',
            price=Decimal('500.00'),
            skin_type='dry',
            concern_tags='dryness,hydration,barrier repair',
            key_ingredients='Ceramides, Squalane',
            full_ingredients='Aqua, Ceramide NP, Ceramide AP, Squalane, Glycerin.',
            usage_instructions='Apply generously over face and neck twice daily, morning and night.',
            caution_info='For external use only. Discontinue if persistent irritation occurs.',
            availability='in_stock',
        )

    def test_faq_ingredient_query(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'Which products contain Vitamin C?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('Radiance Vitamin C Serum', data['answer'])
        self.assertEqual(data['intent'], 'ingredient')
        self.assertGreater(len(data['referenced_products']), 0)
        self.assertEqual(data['referenced_products'][0]['name'], 'Radiance Vitamin C Serum')
        self.assertTrue(data['is_disclaimer_applicable'])

    def test_faq_usage_query_for_product(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'How should I apply this?',
            'product_id': self.serum.id
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('Apply 3-4 drops', data['answer'])
        self.assertEqual(data['intent'], 'usage')
        self.assertEqual(len(data['referenced_products']), 1)

    def test_faq_caution_query(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'Are there any precautions or cautions for the Vitamin C serum?',
            'product_id': self.serum.id
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('patch test', data['answer'].lower())
        self.assertEqual(data['intent'], 'caution')

    def test_faq_general_shipping_policy(self):
        response = self.client.post('/api/faq/', {
            'question': 'What is your shipping policy and delivery time?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('shipping is FREE', data['answer'])
        self.assertEqual(data['intent'], 'platform_faq')

    def test_faq_unavailable_fallback_and_no_medical_guarantee(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'Can this diagnose or cure chronic eczema on my eyelids?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('not currently available in the Joyory product catalog', data['answer'])
        self.assertTrue(data['is_disclaimer_applicable'])
        self.assertIn('not a medical professional', data['disclaimer'].lower())

    def test_faq_empty_question(self):
        response = self.client.post('/api/products/faq/', {
            'question': '   '
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_faq_invalid_body_type(self):
        response = self.client.post('/api/products/faq/', 'not-a-dict', format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

