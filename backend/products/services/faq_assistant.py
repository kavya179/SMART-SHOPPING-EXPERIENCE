"""
Joyory SmartMatch — Hybrid NLP Product FAQ Assistant Service.

Features:
- Machine Learning Intent Classification (scikit-learn TF-IDF + Logistic Regression)
- Semantic Question-Answer Retrieval (Cosine Similarity on Verified Knowledge Base)
- Product Entity Extraction & Contextual Resolution (from SQLite Catalog)
- Diverse, Direct, Natural Language Response Generation
- Strict Non-Medical Guardrails and Transparent Fallback Handling
"""

import os
import re
import joblib
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from django.db.models import Q
from products.models import Product

# Non-Medical Disclaimer Banner
DISCLAIMER = "⚠️ Demo Catalog Assistant: Automated catalog helper, not a medical professional. Derived directly from product specifications. Does not constitute medical advice or dermatological diagnosis."

INTENT_LABELS = {
    'usage_instructions': '🏷️ Usage Directions',
    'ingredients': '🏷️ Ingredients & Actives',
    'product_purpose': '🏷️ Product Overview & Benefits',
    'safety_and_cautions': '🏷️ Safety, Cautions & Patch Test',
    'price_and_discount': '🏷️ Pricing & Offers',
    'availability_and_stock': '🏷️ Inventory & Availability',
    'comparison_and_alternatives': '🏷️ Formulation Comparison',
    'skin_type_recommendation': '🏷️ Skin & Hair Recommendations',
    'platform_policy': '🏷️ Store Policy & FAQs',
    'medical_disclaimer_fallback': '🏷️ Medical & Safety Notice',
    'unavailable': '🏷️ Catalog Assistant',
}

# Curated In-Memory Knowledge Base Fallback
FALLBACK_CURATED_FAQS = [
    {
        "keywords": ["smartmatch", "quiz", "algorithm", "how it works", "recommendation score"],
        "intent": "platform_policy",
        "answer": "Joyory SmartMatch uses a deterministic rule-based matching engine. It calculates compatibility scores by evaluating your category, skin profile, primary concerns, preferred active ingredients, and budget against verified catalog attributes."
    },
    {
        "keywords": ["authentic", "genuine", "real", "fake", "original"],
        "intent": "platform_policy",
        "answer": "All products listed in the Joyory SmartMatch catalog feature verified brand specifications, 100% genuine formulation profiles, and complete INCI ingredient transparency."
    },
    {
        "keywords": ["shipping", "delivery", "fee", "cost", "charge", "delivery time"],
        "intent": "platform_policy",
        "answer": "Standard shipping is FREE on orders above ₹499. For orders below ₹499, a flat shipping fee of ₹50 applies. Estimated delivery is 2–3 business days."
    },
    {
        "keywords": ["payment", "pay", "card", "checkout", "cod", "cash on delivery"],
        "intent": "platform_policy",
        "answer": "Joyory SmartMatch features a simulated demo checkout for prototype safety. We support demo Cash on Delivery and simulated Net Banking. No real payment or credit card is processed."
    },
    {
        "keywords": ["patch test", "how to patch test", "allergy test", "forearm"],
        "intent": "safety_and_cautions",
        "answer": "To perform a patch test: Apply 2–3 drops of the formula to a small area of clean skin on your inner forearm. Wait 24 hours. If no redness, itching, or irritation occurs, the product is generally suitable for regular use."
    },
    {
        "keywords": ["return", "refund", "exchange", "cancel"],
        "intent": "platform_policy",
        "answer": "Unopened products in original packaging can be returned within 14 days of delivery. In this demo prototype, returns and refunds are simulated via customer support."
    }
]

# Cache ML Model in Memory
_LOADED_CLASSIFIER = None
_LOADED_SEMANTIC_INDEX = None
_MODELS_INITIALIZED = False


def _init_models():
    global _LOADED_CLASSIFIER, _LOADED_SEMANTIC_INDEX, _MODELS_INITIALIZED
    if _MODELS_INITIALIZED:
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, 'ml_models')

    clf_path = os.path.join(models_dir, 'faq_intent_classifier.joblib')
    idx_path = os.path.join(models_dir, 'faq_semantic_index.joblib')

    try:
        if os.path.exists(clf_path):
            _LOADED_CLASSIFIER = joblib.load(clf_path)
        if os.path.exists(idx_path):
            _LOADED_SEMANTIC_INDEX = joblib.load(idx_path)
    except Exception as e:
        print(f"[Warning] Failed to load FAQ ML models: {e}. Falling back to rule-based retrieval.")

    _MODELS_INITIALIZED = True


class ProductFaqAssistant:
    """
    Intelligent Hybrid NLP Product FAQ Assistant for Joyory SmartMatch.
    """

    def __init__(self, question: str, product_id: Optional[int] = None):
        _init_models()
        self.raw_question = (question or '').strip()
        self.question_lower = self.raw_question.lower()
        self.product_id = product_id
        self.identified_product = self._resolve_target_product()

    def _resolve_target_product(self) -> Optional[Product]:
        """Resolve product from explicit product_id context or name mentioned in question."""
        if self.product_id:
            try:
                return Product.objects.get(pk=self.product_id)
            except Product.DoesNotExist:
                pass

        # Search if any product name/brand is mentioned in the query
        for prod in Product.objects.all():
            prod_name_lower = prod.name.lower()
            if prod_name_lower in self.question_lower:
                return prod
            # Check 2-word combinations e.g. "vitamin c serum", "hydration cream", "silkstrand shampoo"
            words = prod_name_lower.split()
            if len(words) >= 2 and ' '.join(words[:2]) in self.question_lower:
                return prod

        return None

    def _classify_intent_ml(self) -> Tuple[str, float]:
        """Classify question intent using trained scikit-learn pipeline."""
        if not _LOADED_CLASSIFIER:
            return ('unknown', 0.0)

        try:
            probs = _LOADED_CLASSIFIER.predict_proba([self.raw_question])[0]
            classes = _LOADED_CLASSIFIER.classes_
            best_idx = np.argmax(probs)
            return (str(classes[best_idx]), float(probs[best_idx]))
        except Exception:
            return ('unknown', 0.0)

    def _search_semantic_faqs(self, threshold: float = 0.45) -> Optional[Dict[str, Any]]:
        """Search curated QA index using TF-IDF cosine similarity."""
        if not _LOADED_SEMANTIC_INDEX:
            return None

        try:
            vec = _LOADED_SEMANTIC_INDEX['vectorizer']
            matrix = _LOADED_SEMANTIC_INDEX['tfidf_matrix']
            records = _LOADED_SEMANTIC_INDEX['records']

            query_vec = vec.transform([self.raw_question])
            sims = (matrix * query_vec.T).toarray().flatten()

            best_idx = np.argmax(sims)
            best_score = float(sims[best_idx])

            if best_score >= threshold:
                matched_record = records[best_idx]
                return {
                    'found': True,
                    'topic': matched_record.get('intent', 'platform_policy'),
                    'intent': matched_record.get('intent', 'platform_policy'),
                    'intent_label': INTENT_LABELS.get(matched_record.get('intent', 'platform_policy'), '🏷️ Store Policy & FAQs'),
                    'answer': matched_record['answer'],
                    'confidence': round(best_score, 2),
                    'disclaimer': DISCLAIMER,
                    'is_disclaimer_applicable': True,
                    'referenced_products': [],
                }
        except Exception:
            pass

        return None

    def answer_query(self) -> Dict[str, Any]:
        """
        Main multi-stage resolution pipeline:
        1. Input validation
        2. Medical emergency / treatment keyword intercept
        3. Product-specific intent resolution (if product identified)
        4. Semantic FAQ matching & Intent ML classification
        5. Catalog entity lookups (ingredients, categories, skin types)
        6. Transparent fallback
        """
        if not self.raw_question:
            return {
                'found': False,
                'topic': 'unavailable',
                'intent': 'unavailable',
                'intent_label': INTENT_LABELS['unavailable'],
                'answer': "Please ask a question about our products, ingredients, routine usage, or store policies.",
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        q = self.question_lower

        # ── Medical Intercept ──────────────────────────────────────────
        medical_terms = ['cure', 'heal', 'disease', 'prescribe', 'prescription', 'eczema', 'psoriasis', 'dermatitis', 'infection', 'fungal']
        if any(term in q for term in medical_terms):
            return {
                'found': True,
                'topic': 'medical_disclaimer_fallback',
                'intent': 'medical_disclaimer_fallback',
                'intent_label': INTENT_LABELS['medical_disclaimer_fallback'],
                'answer': (
                    "⚠️ **Medical Advisory:** Joyory SmartMatch is a beauty and personal care shopping platform, not a medical professional.\n\n"
                    "Our products are cosmetic formulations designed for daily hygiene, hydration, and appearance improvement. "
                    "They do **not** claim to diagnose, cure, heal, or treat medical conditions such as eczema, dermatitis, or psoriasis.\n\n"
                    "For clinical skin conditions or medical treatments, please consult a certified dermatologist."
                ),
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        # ── Intent Prediction via ML ───────────────────────────────────
        predicted_intent, confidence = self._classify_intent_ml()

        # ── Product-Specific Query Resolution ─────────────────────────
        if self.identified_product:
            prod_response = self._answer_for_product(self.identified_product, predicted_intent, confidence)
            if prod_response:
                return prod_response

        # ── Curated Semantic Knowledge Base Search ─────────────────────
        semantic_match = self._search_semantic_faqs(threshold=0.45)
        if semantic_match:
            return semantic_match

        # ── Catalog Active Ingredient Search ──────────────────────────
        ing_answer = self._answer_ingredient_search()
        if ing_answer:
            return ing_answer

        # ── Catalog Category Search ────────────────────────────────────
        cat_answer = self._answer_category_search()
        if cat_answer:
            return cat_answer

        # ── Catalog Skin-Type Search ───────────────────────────────────
        skin_answer = self._answer_skin_type_search()
        if skin_answer:
            return skin_answer

        # ── Fallback Curated Keyword Rules ─────────────────────────────
        for item in FALLBACK_CURATED_FAQS:
            if any(k in q for k in item['keywords']):
                return {
                    'found': True,
                    'topic': item['intent'],
                    'intent': item['intent'],
                    'intent_label': INTENT_LABELS.get(item['intent'], '🏷️ Store Policy & FAQs'),
                    'answer': item['answer'],
                    'confidence': 0.85,
                    'disclaimer': DISCLAIMER,
                    'is_disclaimer_applicable': True,
                    'referenced_products': [],
                }

        # ── Transparent Fallback ───────────────────────────────────────
        return {
            'found': False,
            'topic': 'unavailable',
            'intent': 'unavailable',
            'intent_label': INTENT_LABELS['unavailable'],
            'answer': (
                f"Information regarding '{self.raw_question}' is not currently available in the Joyory product catalog. "
                "You can explore our product details, ingredients, and instructions directly on each product page. "
                "For specific medical concerns, please consult a dermatologist."
            ),
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': [],
        }

    def _answer_for_product(self, product: Product, intent: str, confidence: float) -> Optional[Dict[str, Any]]:
        """Build dynamic, direct, and non-repetitive answers for a specific product."""
        q = self.question_lower
        ref_prod = [{
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'category': product.category,
            'price': float(product.discounted_price or product.price),
        }]

        # 1. Usage / Directions
        if intent == 'usage_instructions' or any(w in q for w in ['how to use', 'how do i use', 'how should i use', 'how to apply', 'how should i apply', 'apply', 'when to use', 'usage', 'application', 'directions', 'routine', 'steps', 'morning', 'night', 'frequency']):
            return {
                'found': True,
                'topic': 'usage',
                'intent': 'usage_instructions',
                'intent_label': INTENT_LABELS['usage_instructions'],
                'answer': (
                    f"**Application Guide for {product.name} ({product.brand}):**\n\n"
                    f"{product.usage_instructions or 'Apply evenly to clean skin or hair as part of your daily routine.'}\n\n"
                    f"• **Target Profile:** Suitable for {product.skin_type.capitalize()} skin types.\n"
                    f"• **Routine Tip:** Always follow daytime active serums with a broad-spectrum sunscreen."
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.9,
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # 2. Ingredients / Formulation
        if intent == 'ingredients' or any(w in q for w in ['ingredient', 'ingredients', 'actives', 'what is in', 'formula', 'inci', 'composition', 'contain', 'chemical']):
            return {
                'found': True,
                'topic': 'ingredient',
                'intent': 'ingredients',
                'intent_label': INTENT_LABELS['ingredients'],
                'answer': (
                    f"**Ingredient Profile for {product.name}:**\n\n"
                    f"• **Key Active Ingredients:** {product.key_ingredients or 'Verified gentle active formulation'}\n"
                    f"• **Full INCI Formula List:** {product.full_ingredients or 'Refer to product packaging for complete list.'}"
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.9,
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # 3. Safety, Cautions & Patch Test
        if intent == 'safety_and_cautions' or any(w in q for w in ['caution', 'cautions', 'warning', 'warnings', 'precaution', 'precautions', 'safe', 'safety', 'side effect', 'sun', 'irritat', 'allergy', 'patch test']):
            return {
                'found': True,
                'topic': 'caution',
                'intent': 'safety_and_cautions',
                'intent_label': INTENT_LABELS['safety_and_cautions'],
                'answer': (
                    f"**Safety & Caution Advice for {product.name}:**\n\n"
                    f"{product.caution_info or 'For external cosmetic use only. Discontinue if irritation occurs.'}\n\n"
                    f"• **Patch Test Recommendation:** Apply 2–3 drops to inner forearm and observe for 24 hours prior to regular use."
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.9,
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # 4. Pricing & Stock
        if intent == 'price_and_discount' or intent == 'availability_and_stock' or any(w in q for w in ['price', 'cost', 'how much', 'discount', 'stock', 'available', 'mrp', 'rate']):
            orig_str = f" (Original MRP: ₹{product.price})" if product.discount_percent > 0 else ""
            discount_note = f" with a **{product.discount_percent}% discount**" if product.discount_percent > 0 else ""
            return {
                'found': True,
                'topic': 'pricing',
                'intent': 'price_and_discount',
                'intent_label': INTENT_LABELS['price_and_discount'],
                'answer': (
                    f"**Pricing & Availability for {product.name}:**\n\n"
                    f"Currently available at **₹{product.discounted_price or product.price}**{orig_str}{discount_note}.\n"
                    f"• **Stock Status:** **{product.availability.replace('_', ' ').title()}**."
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.9,
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # 5. Product Purpose / Overview
        if intent == 'product_purpose' or any(w in q for w in ['what is this', 'what does this do', 'benefit', 'benefits', 'overview', 'goal', 'why buy', 'purpose']):
            return {
                'found': True,
                'topic': 'overview',
                'intent': 'product_purpose',
                'intent_label': INTENT_LABELS['product_purpose'],
                'answer': (
                    f"**About {product.name} ({product.brand}):**\n\n"
                    f"{product.description}\n\n"
                    f"• **Primary Target Concerns:** {product.concern_tags or 'General daily care'}\n"
                    f"• **Skin Compatibility:** Formulated for {product.skin_type.capitalize()} skin types."
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.85,
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # 6. Comparison & Alternatives
        if intent == 'comparison_and_alternatives' or any(w in q for w in ['compare', 'difference', 'vs', 'alternative', 'other product']):
            related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
            related_lines = [f"• **{p.name}** — ₹{p.discounted_price or p.price} (Actives: {p.key_ingredients})" for p in related_products]
            related_ref = [{'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price)} for p in related_products]
            return {
                'found': True,
                'topic': 'comparison',
                'intent': 'comparison_and_alternatives',
                'intent_label': INTENT_LABELS['comparison_and_alternatives'],
                'answer': (
                    f"**Comparing {product.name} with similar {product.category.capitalize()} formulas:**\n\n"
                    f"{product.name} is formulated specifically with **{product.key_ingredients}** for {product.concern_tags}.\n\n"
                    f"**Other options in {product.category.capitalize()}:**\n" + '\n'.join(related_lines) +
                    "\n\n*Tip: You can use our Formula Comparison Studio to evaluate up to 3 products side-by-side.*"
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.85,
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod + related_ref,
            }

        # Default to direct overview if specific product matched
        return {
            'found': True,
            'topic': 'overview',
            'intent': 'product_purpose',
            'intent_label': INTENT_LABELS['product_purpose'],
            'answer': (
                f"**{product.name}** by {product.brand} ({product.category.capitalize()}):\n\n"
                f"{product.description}\n\n"
                f"• **Key Ingredients:** {product.key_ingredients}\n"
                f"• **Intended for:** {product.skin_type.capitalize()} skin types ({product.concern_tags})"
            ),
            'confidence': 0.8,
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prod,
        }

    def _answer_ingredient_search(self) -> Optional[Dict[str, Any]]:
        """Search products by active ingredients mentioned in question."""
        actives = [
            'vitamin c', 'niacinamide', 'hyaluronic', 'ceramide', 'squalane',
            'aloe vera', 'keratin', 'biotin', 'caffeine', 'argan', 'cocoa butter',
            'charcoal', 'jojoba', 'zinc', 'spf', 'sunscreen', 'salicylic', 'ferulic'
        ]

        found_active = next((a for a in actives if a in self.question_lower), None)
        if not found_active:
            return None

        matches = Product.objects.filter(
            Q(key_ingredients__icontains=found_active) |
            Q(full_ingredients__icontains=found_active) |
            Q(description__icontains=found_active)
        )

        if not matches.exists():
            return {
                'found': False,
                'topic': 'ingredient',
                'intent': 'ingredients',
                'intent_label': INTENT_LABELS['ingredients'],
                'answer': f"We currently do not have any products containing '{found_active.title()}' in our catalog.",
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        prods_info = [f"• **{p.name}** ({p.brand}) — ₹{p.discounted_price or p.price} (Key: {p.key_ingredients})" for p in matches[:3]]
        ref_prods = [{'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price)} for p in matches[:3]]

        return {
            'found': True,
            'topic': 'ingredient',
            'intent': 'ingredients',
            'intent_label': INTENT_LABELS['ingredients'],
            'answer': (
                f"Here are the product(s) containing **{found_active.title()}** in our catalog:\n\n" +
                '\n'.join(prods_info)
            ),
            'confidence': 0.92,
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    def _answer_category_search(self) -> Optional[Dict[str, Any]]:
        """Search products by category."""
        categories = ['skincare', 'haircare', 'makeup', 'fragrance', 'bodycare', 'nailcare']
        matched_cat = None
        for cat in categories:
            if cat in self.question_lower or (cat == 'bodycare' and 'body' in self.question_lower) or (cat == 'haircare' and 'hair' in self.question_lower):
                matched_cat = cat
                break

        if not matched_cat:
            return None

        prods = Product.objects.filter(category=matched_cat)
        if not prods.exists():
            return None

        prods_info = [f"• **{p.name}** — ₹{p.discounted_price or p.price} ({p.concern_tags})" for p in prods[:4]]
        ref_prods = [{'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price)} for p in prods[:4]]

        return {
            'found': True,
            'topic': 'category',
            'intent': 'skin_type_recommendation',
            'intent_label': INTENT_LABELS['skin_type_recommendation'],
            'answer': (
                f"We offer {prods.count()} product(s) in **{matched_cat.capitalize()}**:\n\n" +
                '\n'.join(prods_info)
            ),
            'confidence': 0.9,
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    def _answer_skin_type_search(self) -> Optional[Dict[str, Any]]:
        """Search products by skin type."""
        skin_types = ['oily', 'dry', 'sensitive', 'combination']
        matched_st = next((st for st in skin_types if st in self.question_lower), None)

        if not matched_st:
            return None

        prods = Product.objects.filter(
            Q(skin_type__iexact=matched_st) | Q(skin_type='all')
        ).filter(category='skincare')

        if not prods.exists():
            return None

        prods_info = [f"• **{p.name}** ({p.brand}) — ₹{p.discounted_price or p.price} (Key: {p.key_ingredients})" for p in prods[:3]]
        ref_prods = [{'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price)} for p in prods[:3]]

        return {
            'found': True,
            'topic': 'skin_type',
            'intent': 'skin_type_recommendation',
            'intent_label': INTENT_LABELS['skin_type_recommendation'],
            'answer': (
                f"For **{matched_st.capitalize()} Skin**, our catalog offers the following compatible formulas:\n\n" +
                '\n'.join(prods_info)
            ),
            'confidence': 0.88,
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }
