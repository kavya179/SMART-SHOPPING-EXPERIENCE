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

    def test_search_multi_word_and_category_synonym(self):
        # Create a bodycare product
        Product.objects.create(
            name='Cocoa Glow Nourishing Body Butter',
            brand='SilkSkin',
            category='bodycare',
            description='Rich whipped body butter with pure cocoa butter.',
            price=Decimal('499.00'),
            skin_type='all',
            concern_tags='dryness,glow',
            key_ingredients='Cocoa Butter, Shea Butter',
            full_ingredients='Aqua, Theobroma Cacao Seed Butter, Butyrospermum Parkii.',
            availability='in_stock',
        )
        # Search with space "body care" -> matches category 'bodycare'
        response = self.client.get('/api/products/?search=body%20care')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['category'], 'bodycare')

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
            discount_percent=10,
            skin_type='all',
            concern_tags='dark spots,dullness,brightening',
            key_ingredients='Vitamin C, Hyaluronic Acid',
            full_ingredients='Aqua, 15% Ethyl Ascorbic Acid, Sodium Hyaluronate, Ferulic Acid.',
            usage_instructions='Apply 3-4 drops in the morning on cleansed face before moisturizer and SPF.',
            caution_info='Perform patch test prior to first use. Slight tingling may occur. Use sunscreen during daytime.',
            availability='in_stock',
            rating=Decimal('4.80'),
            review_count=120,
        )
        self.cream = Product.objects.create(
            name='Ultra Hydration Cream',
            brand='AquaSoft',
            category='skincare',
            description='Moisturizer with ceramides for dry skin barrier repair.',
            price=Decimal('450.00'),
            discount_percent=0,
            skin_type='dry',
            concern_tags='dryness,hydration,barrier repair',
            key_ingredients='Ceramides, Squalane',
            full_ingredients='Aqua, Ceramide NP, Ceramide AP, Squalane, Glycerin.',
            usage_instructions='Apply generously over face and neck twice daily, morning and night.',
            caution_info='For external use only. Discontinue if persistent irritation occurs.',
            availability='in_stock',
            rating=Decimal('4.60'),
            review_count=85,
        )

    def test_faq_greeting_social(self):
        response = self.client.post('/api/faq/', {'question': 'Hello! How are you?'}, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['intent'], 'greeting')
        self.assertIn('Joyory SmartMatch', data['answer'])
        self.assertEqual(len(data['referenced_products']), 0)
        self.assertTrue(len(data['suggested_questions']) > 0)

    def test_faq_gratitude_and_farewell(self):
        resp_thanks = self.client.post('/api/faq/', {'question': 'Thank you so much!'}, format='json')
        self.assertEqual(resp_thanks.status_code, 200)
        self.assertEqual(resp_thanks.data['intent'], 'gratitude')

        resp_bye = self.client.post('/api/faq/', {'question': 'Goodbye, see you!'}, format='json')
        self.assertEqual(resp_bye.status_code, 200)
        self.assertEqual(resp_bye.data['intent'], 'farewell')

    def test_faq_ingredient_query(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'Which products contain Vitamin C?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('Radiance Vitamin C Serum', data['answer'])
        self.assertEqual(data['intent'], 'ingredients')
        self.assertGreater(len(data['referenced_products']), 0)
        self.assertEqual(data['referenced_products'][0]['name'], 'Radiance Vitamin C Serum')
        self.assertTrue(data['is_disclaimer_applicable'])
        self.assertIn('intent_label', data)

    def test_faq_price_and_discount_query(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'What is the price of Radiance Vitamin C Serum?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('809.1', data['answer'])
        self.assertEqual(data['context_product_id'], self.serum.id)
        self.assertEqual(len(data['referenced_products']), 1)

    def test_faq_budget_search(self):
        response = self.client.post('/api/faq/', {
            'question': 'Show me products under ₹500'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['intent'], 'budget_search')
        self.assertIn('Ultra Hydration Cream', data['answer'])
        self.assertEqual(data['referenced_products'][0]['name'], 'Ultra Hydration Cream')

    def test_faq_contextual_follow_up(self):
        # First query sets context_product_id = self.serum.id
        resp1 = self.client.post('/api/faq/', {
            'question': 'Tell me about Radiance Vitamin C Serum'
        }, format='json')
        self.assertEqual(resp1.status_code, 200)
        context_id = resp1.data.get('context_product_id')
        self.assertEqual(context_id, self.serum.id)

        # Follow-up query using pronoun "its price"
        resp2 = self.client.post('/api/faq/', {
            'question': 'What is its price?',
            'context_product_id': context_id
        }, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('Pricing & Availability for Radiance Vitamin C Serum', resp2.data['answer'])

        # Follow-up query asking "what are its ingredients?"
        resp3 = self.client.post('/api/faq/', {
            'question': 'What are its ingredients?',
            'context_product_id': context_id
        }, format='json')
        self.assertEqual(resp3.status_code, 200)
        self.assertIn('Vitamin C, Hyaluronic Acid', resp3.data['answer'])

    def test_faq_pronoun_without_context_prompts_clarification(self):
        response = self.client.post('/api/faq/', {
            'question': 'What is its price?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertFalse(data['found'])
        self.assertIn('Which product are you referring to', data['answer'])

    def test_faq_product_comparison(self):
        response = self.client.post('/api/faq/', {
            'question': 'Compare Radiance Vitamin C Serum and Ultra Hydration Cream'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['intent'], 'comparison_and_alternatives')
        self.assertIn('Formula Comparison', data['answer'])
        self.assertEqual(len(data['referenced_products']), 2)

    def test_faq_unfound_product(self):
        response = self.client.post('/api/faq/', {
            'question': 'What is the price of Loreal Revitalift Laser X3?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertFalse(data['found'])
        self.assertIn('could not be found in our verified catalog', data['answer'])

    def test_faq_usage_query_for_product(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'How should I apply this?',
            'product_id': self.serum.id
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('Apply 3-4 drops', data['answer'])
        self.assertEqual(data['intent'], 'usage_instructions')
        self.assertEqual(len(data['referenced_products']), 1)

    def test_faq_caution_query(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'Are there any precautions or cautions for the Vitamin C serum?',
            'product_id': self.serum.id
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('patch test', data['answer'].lower())
        self.assertEqual(data['intent'], 'safety_and_cautions')

    def test_faq_general_shipping_policy(self):
        response = self.client.post('/api/faq/', {
            'question': 'What is your shipping policy and delivery time?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('shipping is FREE', data['answer'])
        self.assertEqual(data['intent'], 'platform_policy')

    def test_faq_medical_query_guardrail(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'Can this diagnose or cure chronic eczema on my eyelids?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['intent'], 'medical_disclaimer_fallback')
        self.assertIn('Medical Advisory', data['answer'])
        self.assertTrue(data['is_disclaimer_applicable'])
        self.assertIn('not a medical professional', data['disclaimer'].lower())

    def test_faq_unsupported_query_fallback(self):
        response = self.client.post('/api/products/faq/', {
            'question': 'How do I change the oil in my car engine?'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['intent'], 'unavailable')
        self.assertIn('could not find specific catalog information', data['answer'])
        self.assertFalse(data['found'])

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


# ══════════════════════════════════════════════════════════════
#  PHASE 5: Review Insight Analyzer Tests
# ══════════════════════════════════════════════════════════════

class ReviewAnalyzerUnitTest(TestCase):
    """Unit tests for ReviewInsightAnalyzer service."""

    def setUp(self):
        # Create test products
        Product.objects.create(
            name='Test Serum',
            brand='TestBrand',
            category='skincare',
            price=Decimal('599.00'),
            rating=Decimal('4.80'),
            review_count=350,
            skin_type='all',
            availability='in_stock',
        )
        Product.objects.create(
            name='Test Moisturizer',
            brand='TestBrand',
            category='skincare',
            price=Decimal('399.00'),
            rating=Decimal('4.20'),
            review_count=80,
            skin_type='dry',
            availability='in_stock',
        )
        Product.objects.create(
            name='Test Lipstick',
            brand='MakeupBrand',
            category='makeup',
            price=Decimal('299.00'),
            rating=Decimal('3.80'),
            review_count=25,
            skin_type='all',
            availability='in_stock',
        )

    def test_analyzer_returns_ok(self):
        from .services.review_analyzer import ReviewInsightAnalyzer
        result = ReviewInsightAnalyzer().analyze()
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result['data_available'])

    def test_analyzer_catalog_summary(self):
        from .services.review_analyzer import ReviewInsightAnalyzer
        result = ReviewInsightAnalyzer().analyze()
        summary = result['catalog_summary']
        self.assertEqual(summary['total_products_analyzed'], 3)
        self.assertEqual(summary['total_review_count'], 455)
        self.assertGreater(summary['average_catalog_rating'], 0)

    def test_rating_distribution_sums_correctly(self):
        from .services.review_analyzer import ReviewInsightAnalyzer
        result = ReviewInsightAnalyzer().analyze()
        total = sum(band['count'] for band in result['rating_distribution'])
        self.assertEqual(total, 3)

    def test_category_breakdown_present(self):
        from .services.review_analyzer import ReviewInsightAnalyzer
        result = ReviewInsightAnalyzer().analyze()
        cats = {c['category'] for c in result['category_breakdown']}
        self.assertIn('skincare', cats)
        self.assertIn('makeup', cats)

    def test_top_products_structure(self):
        from .services.review_analyzer import ReviewInsightAnalyzer
        result = ReviewInsightAnalyzer().analyze()
        tp = result['top_products']
        self.assertIn('top_rated', tp)
        self.assertIn('most_reviewed', tp)
        self.assertIn('best_value', tp)
        self.assertGreater(len(tp['top_rated']), 0)

    def test_confidence_breakdown_present(self):
        from .services.review_analyzer import ReviewInsightAnalyzer
        result = ReviewInsightAnalyzer().analyze()
        cb = result['confidence_breakdown']
        self.assertIsInstance(cb, list)
        self.assertGreater(len(cb), 0)

    def test_data_disclaimer_present(self):
        from .services.review_analyzer import ReviewInsightAnalyzer
        result = ReviewInsightAnalyzer().analyze()
        self.assertIn('data_disclaimer', result)
        self.assertIn('review text', result['data_disclaimer'].lower())

    def test_what_is_missing_present(self):
        from .services.review_analyzer import ReviewInsightAnalyzer
        result = ReviewInsightAnalyzer().analyze()
        self.assertIn('what_is_missing', result)


class ReviewInsightsAPITest(TestCase):
    """Integration tests for the /api/products/review-insights/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        Product.objects.create(
            name='API Test Product',
            brand='TestBrand',
            category='skincare',
            price=Decimal('499.00'),
            rating=Decimal('4.50'),
            review_count=200,
            skin_type='oily',
            availability='in_stock',
        )

    def test_endpoint_returns_200(self):
        response = self.client.get('/api/products/review-insights/')
        self.assertEqual(response.status_code, 200)

    def test_endpoint_returns_ok_status(self):
        response = self.client.get('/api/products/review-insights/')
        self.assertEqual(response.data['status'], 'ok')

    def test_endpoint_has_catalog_summary(self):
        response = self.client.get('/api/products/review-insights/')
        self.assertIn('catalog_summary', response.data)

    def test_endpoint_has_rating_distribution(self):
        response = self.client.get('/api/products/review-insights/')
        self.assertIn('rating_distribution', response.data)

    def test_endpoint_has_category_breakdown(self):
        response = self.client.get('/api/products/review-insights/')
        self.assertIn('category_breakdown', response.data)

    def test_endpoint_has_top_products(self):
        response = self.client.get('/api/products/review-insights/')
        self.assertIn('top_products', response.data)

    def test_endpoint_includes_disclaimer(self):
        response = self.client.get('/api/products/review-insights/')
        self.assertIn('data_disclaimer', response.data)

    def test_endpoint_method_not_allowed_post(self):
        """Review insights is GET-only."""
        response = self.client.post('/api/products/review-insights/', {}, format='json')
        self.assertEqual(response.status_code, 405)


# ══════════════════════════════════════════════════════════════
#  PHASE 7: IngredientChecker Additional Tests
# ══════════════════════════════════════════════════════════════

class IngredientCheckerExtendedTest(TestCase):
    """Extended tests for IngredientChecker to improve coverage."""

    def test_safe_single_ingredient(self):
        from .services.ingredient_checker import IngredientChecker
        result = IngredientChecker(['Hyaluronic Acid']).check()
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['overall_safety'], 'safe')
        self.assertEqual(result['total_conflicts'], 0)

    def test_high_severity_conflict(self):
        from .services.ingredient_checker import IngredientChecker
        # Retinol + Benzoyl Peroxide is a known high-severity conflict
        result = IngredientChecker(['Retinol', 'Benzoyl Peroxide']).check()
        self.assertEqual(result['status'], 'ok')
        severities = [c['severity'] for c in result['conflicts']]
        self.assertIn('high', severities)
        self.assertEqual(result['overall_safety'], 'unsafe')

    def test_case_insensitive_matching(self):
        from .services.ingredient_checker import IngredientChecker
        result = IngredientChecker(['vitamin c', 'RETINOL']).check()
        self.assertGreater(result['total_conflicts'], 0)

    def test_empty_ingredient_list(self):
        from .services.ingredient_checker import IngredientChecker
        result = IngredientChecker([]).check()
        self.assertEqual(result['status'], 'error')

    def test_disclaimer_always_present(self):
        from .services.ingredient_checker import IngredientChecker
        result = IngredientChecker(['Niacinamide']).check()
        self.assertIn('disclaimer', result)

    def test_safe_pairs_populated(self):
        from .services.ingredient_checker import IngredientChecker
        result = IngredientChecker(['Niacinamide', 'Hyaluronic Acid', 'Ceramides']).check()
        self.assertIn('safe_pairs', result)


# ══════════════════════════════════════════════════════════════
#  PHASE 7: RoutineBuilder Additional Tests
# ══════════════════════════════════════════════════════════════

class RoutineBuilderExtendedTest(TestCase):
    """Extended tests for RoutineBuilder service."""

    def setUp(self):
        Product.objects.create(
            name='Routine Test Serum',
            brand='TestBrand',
            category='skincare',
            price=Decimal('599.00'),
            rating=Decimal('4.60'),
            review_count=200,
            skin_type='oily',
            concern_tags='acne,oiliness',
            key_ingredients='Niacinamide, Salicylic Acid',
            availability='in_stock',
        )

    def test_routine_has_morning_and_evening(self):
        from .services.routine_builder import RoutineBuilder
        result = RoutineBuilder('oily', 'acne').build()
        self.assertEqual(result['status'], 'ok')
        self.assertIn('morning_routine', result)
        self.assertIn('evening_routine', result)

    def test_routine_steps_are_ordered(self):
        from .services.routine_builder import RoutineBuilder
        result = RoutineBuilder('dry', 'hydration').build()
        steps = result['morning_routine']
        step_nums = [s['step'] for s in steps]
        self.assertEqual(step_nums, sorted(step_nums))

    def test_all_skin_types_work(self):
        from .services.routine_builder import RoutineBuilder
        for skin_type in ['oily', 'dry', 'combination', 'sensitive', 'all']:
            result = RoutineBuilder(skin_type, 'general').build()
            self.assertEqual(result['status'], 'ok', f"Failed for skin_type={skin_type}")

    def test_all_concerns_work(self):
        from .services.routine_builder import RoutineBuilder
        for concern in ['acne', 'brightening', 'hydration', 'anti-aging', 'general']:
            result = RoutineBuilder('all', concern).build()
            self.assertEqual(result['status'], 'ok', f"Failed for concern={concern}")

    def test_disclaimer_present(self):
        from .services.routine_builder import RoutineBuilder
        result = RoutineBuilder('oily', 'acne').build()
        self.assertIn('disclaimer', result)

    def test_routine_tips_present(self):
        from .services.routine_builder import RoutineBuilder
        result = RoutineBuilder('oily', 'acne').build()
        self.assertIn('routine_tips', result)

    def test_total_products_found_is_integer(self):
        from .services.routine_builder import RoutineBuilder
        result = RoutineBuilder('all', 'general').build()
        self.assertIsInstance(result['total_products_found'], int)


# ══════════════════════════════════════════════════════════════
#  PHASE 7: Ingredient Check API Endpoint Tests
# ══════════════════════════════════════════════════════════════

class IngredientCheckAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_endpoint_post_returns_200(self):
        response = self.client.post('/api/products/ingredient-check/', {
            'ingredients': ['Vitamin C', 'Niacinamide']
        }, format='json')
        self.assertEqual(response.status_code, 200)

    def test_endpoint_get_not_allowed(self):
        response = self.client.get('/api/products/ingredient-check/')
        self.assertEqual(response.status_code, 405)

    def test_endpoint_missing_ingredients_field(self):
        response = self.client.post('/api/products/ingredient-check/', {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_endpoint_empty_ingredients_list(self):
        response = self.client.post('/api/products/ingredient-check/', {
            'ingredients': []
        }, format='json')
        self.assertEqual(response.status_code, 400)


# ══════════════════════════════════════════════════════════════
#  PHASE 7: Routine Builder API Endpoint Tests
# ══════════════════════════════════════════════════════════════

class RoutineAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_endpoint_post_returns_200(self):
        response = self.client.post('/api/products/routine/', {
            'skin_type': 'oily',
            'concern': 'acne',
        }, format='json')
        self.assertEqual(response.status_code, 200)

    def test_endpoint_get_not_allowed(self):
        response = self.client.get('/api/products/routine/')
        self.assertEqual(response.status_code, 405)

    def test_endpoint_missing_skin_type(self):
        response = self.client.post('/api/products/routine/', {
            'concern': 'acne',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_endpoint_missing_concern(self):
        response = self.client.post('/api/products/routine/', {
            'skin_type': 'oily',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_endpoint_invalid_skin_type(self):
        response = self.client.post('/api/products/routine/', {
            'skin_type': 'alien',
            'concern': 'acne',
        }, format='json')
        self.assertEqual(response.status_code, 400)
