"""
Joyory SmartMatch — Hybrid NLP Product FAQ & Assistant Service.

Features:
- Conversational Dialog Manager (Greetings, Social turns, Gratitude, Farewell)
- Pronoun & Follow-up Context Tracking (Resolving 'it', 'its', 'this product' via context_product_id)
- Real SQLite Catalog Data Grounding (Product details, pricing, ingredients, directions, cautions)
- Category, Skin-Type, Concern & Budget Extraction (e.g., 'products under ₹500')
- Multi-Product Comparison Engine (Side-by-side INCI, pricing, and skin compatibility)
- Scikit-Learn TF-IDF Intent Classifier & Semantic QA Retrieval
- Strict Non-Medical Guardrails and Missing-Data Transparency
"""

import os
import re
import joblib
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
from django.db.models import Q
from products.models import Product

# Non-Medical Disclaimer
DISCLAIMER = "⚠️ Demo Catalog Assistant: Automated helper, not a medical professional. Catalog specifications only. Does not constitute medical diagnosis or clinical advice."

INTENT_LABELS = {
    'greeting': '👋 Greeting & Welcome',
    'gratitude': '🙏 Gratitude',
    'farewell': '👋 Farewell',
    'usage_instructions': '🏷️ Usage Directions',
    'ingredients': '🏷️ Ingredients & Actives',
    'product_purpose': '🏷️ Product Overview & Benefits',
    'safety_and_cautions': '🏷️ Safety, Cautions & Patch Test',
    'price_and_discount': '🏷️ Pricing & Offers',
    'budget_search': '🏷️ Budget-Based Search',
    'availability_and_stock': '🏷️ Inventory & Availability',
    'comparison_and_alternatives': '🏷️ Formulation Comparison',
    'skin_type_recommendation': '🏷️ Skin & Hair Recommendations',
    'platform_policy': '🏷️ Store Policy & FAQs',
    'medical_disclaimer_fallback': '🏷️ Medical & Safety Notice',
    'unknown': '🏷️ Catalog Assistant',
    'unavailable': '🏷️ Catalog Assistant',
}

# Curated Policy & Store Knowledge Base
CURATED_FAQS = [
    {
        "keywords": ["smartmatch", "quiz", "algorithm", "how it works", "recommendation score", "match score"],
        "intent": "platform_policy",
        "answer": (
            "**How Joyory SmartMatch Works:**\n\n"
            "Joyory SmartMatch uses a deterministic, rule-based recommendation engine. "
            "It evaluates your selected category, skin type profile, specific target concerns, "
            "preferred active ingredients, and maximum budget against verified catalog attributes to calculate a compatibility score (0–100%)."
        ),
        "suggested_questions": ["Take the recommendation quiz", "Show skincare products", "Which products contain Niacinamide?"]
    },
    {
        "keywords": ["authentic", "genuine", "real", "fake", "original", "authenticity"],
        "intent": "platform_policy",
        "answer": (
            "**Authenticity & Quality Guarantee:**\n\n"
            "All items listed in the Joyory SmartMatch catalog feature 100% verified brand specifications, "
            "genuine active formulations, and complete INCI ingredient transparency."
        ),
        "suggested_questions": ["Show bestsellers", "What is the return policy?", "Show products under ₹600"]
    },
    {
        "keywords": ["shipping", "delivery", "fee", "cost", "charge", "delivery time", "how long to deliver"],
        "intent": "platform_policy",
        "answer": (
            "**Shipping & Delivery Policy:**\n\n"
            "• **Standard Shipping:** FREE on all orders above ₹499.\n"
            "• **Orders below ₹499:** A flat ₹50 shipping fee applies.\n"
            "• **Estimated Delivery:** 2 to 3 business days across major cities."
        ),
        "suggested_questions": ["What payment methods do you accept?", "What is the return policy?"]
    },
    {
        "keywords": ["payment", "pay", "card", "checkout", "cod", "cash on delivery", "upi", "net banking"],
        "intent": "platform_policy",
        "answer": (
            "**Payment & Checkout Options:**\n\n"
            "Joyory SmartMatch provides a simulated demo checkout environment for hackathon evaluation.\n\n"
            "• We support simulated **Cash on Delivery (COD)** and **Demo Net Banking/UPI**.\n"
            "• **Safety Notice:** No real credit card or bank credentials are required or processed."
        ),
        "suggested_questions": ["What is your return policy?", "Show skincare products"]
    },
    {
        "keywords": ["patch test", "how to patch test", "allergy test", "forearm", "sensitive test"],
        "intent": "safety_and_cautions",
        "answer": (
            "**How to Perform a Cosmetic Patch Test:**\n\n"
            "1. Dispense 2–3 drops of the formulation onto clean skin on your inner forearm.\n"
            "2. Leave the area undisturbed for 24 hours.\n"
            "3. If no redness, itching, swelling, or burning develops, the product is generally safe for regular use.\n\n"
            "*If irritation occurs, rinse thoroughly with cool water and discontinue use.*"
        ),
        "suggested_questions": ["What products are best for sensitive skin?", "Show gentle cleansers"]
    },
    {
        "keywords": ["return", "refund", "exchange", "cancel", "cancellation"],
        "intent": "platform_policy",
        "answer": (
            "**Returns & Refunds Policy:**\n\n"
            "• Unopened products in their original packaging can be returned within **14 days of delivery**.\n"
            "• For demo prototype orders, simulated refunds are credited to your demo wallet within 48 hours."
        ),
        "suggested_questions": ["What is the shipping fee?", "How does checkout work?"]
    }
]

# ML Cache
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
    Intelligent Conversational, Context-Aware, and Product-Grounded FAQ Assistant.
    """

    def __init__(self, question: str, product_id: Optional[int] = None, context_product_id: Optional[int] = None):
        _init_models()
        self.raw_question = (question or '').strip()
        self.question_lower = self.raw_question.lower()
        self.active_product_id = product_id
        self.context_product_id = context_product_id
        self.identified_product, self.is_pronoun_reference = self._resolve_target_product()

    def _resolve_target_product(self) -> Tuple[Optional[Product], bool]:
        """
        Identify target product by:
        1. Explicit product name matching in the query.
        2. Pronoun / follow-up resolution ('it', 'its', 'this product') via context_product_id or active_product_id.
        """
        q = self.question_lower

        # 1. Check for explicit product name in question
        all_products = list(Product.objects.all())
        # Sort by name length descending to match longest specific name first
        all_products.sort(key=lambda p: len(p.name), reverse=True)

        for prod in all_products:
            prod_name_lower = prod.name.lower()
            if prod_name_lower in q:
                return prod, False

            # Check 2-3 word distinctive prefixes (e.g., 'vitamin c serum', 'hydration boost cream')
            words = prod_name_lower.split()
            if len(words) >= 2:
                two_word = ' '.join(words[:2])
                if two_word in q and len(two_word) > 5:
                    return prod, False

        # 2. Check for brand + category matching (e.g., 'joyory cleanser', 'lumina serum')
        for prod in all_products:
            brand_cat = f"{prod.brand.lower()} {prod.category.lower()}"
            if brand_cat in q:
                return prod, False

        # 3. Check for pronoun / follow-up references
        pronoun_patterns = [
            r'\b(it|its|this|that|the product|this product|this one|the item)\b',
            r'\b(how to use it|what is its price|what are its ingredients|is it safe|how much is it)\b'
        ]
        has_pronoun = any(re.search(pattern, q) for pattern in pronoun_patterns)

        if has_pronoun or len(q.split()) <= 4:
            # Check context_product_id first, then active_product_id
            target_id = self.context_product_id or self.active_product_id
            if target_id:
                try:
                    prod = Product.objects.get(pk=target_id)
                    return prod, True
                except Product.DoesNotExist:
                    pass

        # If active_product_id is explicitly supplied on PDP
        if self.active_product_id:
            try:
                return Product.objects.get(pk=self.active_product_id), False
            except Product.DoesNotExist:
                pass

        return None, False

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

    def _search_semantic_faqs(self, threshold: float = 0.48) -> Optional[Dict[str, Any]]:
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
                intent = matched_record.get('intent', 'platform_policy')
                return {
                    'found': True,
                    'topic': intent,
                    'intent': intent,
                    'intent_label': INTENT_LABELS.get(intent, '🏷️ Store Policy & FAQs'),
                    'answer': matched_record['answer'],
                    'confidence': round(best_score, 2),
                    'context_product_id': self.context_product_id,
                    'suggested_questions': [
                        "What skincare products are available?",
                        "Show products under ₹500",
                        "Which products contain Niacinamide?"
                    ],
                    'disclaimer': DISCLAIMER,
                    'is_disclaimer_applicable': True,
                    'referenced_products': [],
                }
        except Exception:
            pass

        return None

    def answer_query(self) -> Dict[str, Any]:
        """
        Main multi-stage conversational & catalog resolution pipeline.
        """
        # 1. Empty input validation
        if not self.raw_question:
            return {
                'found': False,
                'topic': 'unavailable',
                'intent': 'unavailable',
                'intent_label': INTENT_LABELS['unavailable'],
                'answer': "Please ask a question about our products, ingredients, routine directions, or store policies.",
                'confidence': 0.0,
                'context_product_id': None,
                'suggested_questions': [
                    "What skincare products are available?",
                    "Which products contain Vitamin C?",
                    "Show products under ₹500"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        q = self.question_lower

        # 2. Medical emergency / treatment keyword intercept
        medical_terms = ['cure', 'heal', 'disease', 'prescribe', 'prescription', 'eczema', 'psoriasis', 'dermatitis', 'infection', 'fungal', 'diagnose', 'diagnosis', 'medical condition']
        if any(term in q for term in medical_terms):
            return {
                'found': True,
                'topic': 'medical_disclaimer_fallback',
                'intent': 'medical_disclaimer_fallback',
                'intent_label': INTENT_LABELS['medical_disclaimer_fallback'],
                'answer': (
                    "⚠️ **Medical Advisory:** Joyory SmartMatch is a beauty and personal care shopping platform, not a medical professional.\n\n"
                    "Our products are cosmetic formulations designed for daily hygiene, hydration, and cosmetic care. "
                    "They do **not** claim to diagnose, cure, heal, or treat clinical medical conditions such as eczema, dermatitis, or fungal infections.\n\n"
                    "For clinical skin conditions or prescription treatments, please consult a certified dermatologist."
                ),
                'confidence': 1.0,
                'context_product_id': self.context_product_id,
                'suggested_questions': [
                    "What products are suitable for sensitive skin?",
                    "How to perform a patch test?",
                    "Show gentle hydration creams"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        # 3. Conversational / Social Intents (Greetings, Gratitude, Farewell, Capabilities)
        social_resp = self._handle_social_conversation()
        if social_resp:
            return social_resp

        # 4. Product Comparison Request (e.g. 'compare X and Y' or 'X vs Y')
        comp_resp = self._handle_product_comparison()
        if comp_resp:
            return comp_resp

        # 5. Budget-Based Search (e.g. 'under 500', 'below 1000', 'budget of 600')
        budget_resp = self._handle_budget_search()
        if budget_resp:
            return budget_resp

        # 6. Intent Prediction via ML
        predicted_intent, ml_confidence = self._classify_intent_ml()

        # 7. Product-Specific Query Resolution (Named or Contextual)
        if self.identified_product:
            prod_response = self._answer_for_product(self.identified_product, predicted_intent, ml_confidence)
            if prod_response:
                return prod_response

        # 8. Pronoun reference without known context
        pronoun_words = ['it', 'its', 'this', 'that', 'this product']
        if any(re.search(rf'\b{w}\b', q) for w in pronoun_words) and not self.identified_product:
            return {
                'found': False,
                'topic': 'ambiguous_product',
                'intent': 'unknown',
                'intent_label': '❓ Clarification Needed',
                'answer': (
                    "Which product are you referring to? Please mention the product name (e.g., *Radiant Vitamin C Serum* or *Hydration Boost Cream*), "
                    "or open a specific product page so I can look up its exact ingredients, price, and usage directions."
                ),
                'confidence': 0.75,
                'context_product_id': None,
                'suggested_questions': [
                    "Show all skincare products",
                    "What products contain Vitamin C?",
                    "Show products under ₹500"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        # 9. Check if user asked specifically about an unknown/external product name
        unknown_prod_match = self._check_unfound_product_mention()
        if unknown_prod_match:
            return unknown_prod_match

        # 10. Curated Semantic Knowledge Base Search
        semantic_match = self._search_semantic_faqs(threshold=0.48)
        if semantic_match:
            return semantic_match

        # 11. Specific Catalog Entity Searches (Ingredients, Categories, Skin-Types, Concerns)
        ing_answer = self._answer_ingredient_search()
        if ing_answer:
            return ing_answer

        concern_answer = self._answer_concern_search()
        if concern_answer:
            return concern_answer

        cat_answer = self._answer_category_search()
        if cat_answer:
            return cat_answer

        skin_answer = self._answer_skin_type_search()
        if skin_answer:
            return skin_answer

        # 12. Curated Fallback Knowledge Base Check
        for item in CURATED_FAQS:
            if any(k in q for k in item['keywords']):
                return {
                    'found': True,
                    'topic': item['intent'],
                    'intent': item['intent'],
                    'intent_label': INTENT_LABELS.get(item['intent'], '🏷️ Store Policy & FAQs'),
                    'answer': item['answer'],
                    'confidence': 0.85,
                    'context_product_id': self.context_product_id,
                    'suggested_questions': item.get('suggested_questions', [
                        "What skincare products are available?",
                        "Show products under ₹500"
                    ]),
                    'disclaimer': DISCLAIMER,
                    'is_disclaimer_applicable': True,
                    'referenced_products': [],
                }

        # 13. Transparent, Helpful Fallback
        return {
            'found': False,
            'topic': 'unavailable',
            'intent': 'unavailable',
            'intent_label': INTENT_LABELS['unavailable'],
            'answer': (
                f"I could not find specific catalog information matching **\"{self.raw_question}\"** in our verified database.\n\n"
                "You can ask me about:\n"
                "• **Products & Prices:** e.g., *'What is the price of Radiant Vitamin C Serum?'*\n"
                "• **Ingredients & Actives:** e.g., *'Which products have Niacinamide or Ceramides?'*\n"
                "• **Routine Usage:** e.g., *'How to use Hydration Boost Gel Cream?'*\n"
                "• **Budget & Filters:** e.g., *'Show skincare products under ₹500'*"
            ),
            'confidence': 0.0,
            'context_product_id': None,
            'suggested_questions': [
                "What skincare products are available?",
                "Which products contain Niacinamide?",
                "Show products under ₹500",
                "How does the SmartMatch quiz work?"
            ],
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': [],
        }

    # ── Social / Conversational Handler ──────────────────────────────
    def _handle_social_conversation(self) -> Optional[Dict[str, Any]]:
        q = self.question_lower.strip('?!., ')

        # 1. Greetings
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'good afternoon', 'hey there', 'namaste', 'hi assistant', 'hello assistant']
        if q in greetings or any(q.startswith(g + ' ') for g in ['hi', 'hello', 'hey', 'good morning', 'good evening']):
            return {
                'found': True,
                'topic': 'greeting',
                'intent': 'greeting',
                'intent_label': INTENT_LABELS['greeting'],
                'answer': (
                    "👋 Hello! Welcome to **Joyory SmartMatch**.\n\n"
                    "I am your product-aware shopping assistant. I can help you look up **real product details**, "
                    "check **prices & active ingredients**, compare formulations, or find items within your budget.\n\n"
                    "How can I assist your beauty routine today?"
                ),
                'confidence': 0.98,
                'context_product_id': self.context_product_id,
                'suggested_questions': [
                    "What skincare products are available?",
                    "Which products contain Vitamin C or Niacinamide?",
                    "Show products under ₹500",
                    "How does the SmartMatch quiz work?"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        # 2. How are you / Status inquiry
        if any(p in q for p in ['how are you', 'how r u', 'how are you doing', 'how do you do', 'what is up', "what's up"]):
            return {
                'found': True,
                'topic': 'greeting',
                'intent': 'greeting',
                'intent_label': INTENT_LABELS['greeting'],
                'answer': (
                    "😊 I'm doing great and ready to help you find the right skincare and beauty essentials at **Joyory SmartMatch**!\n\n"
                    "Ask me about any product in our catalog, explore specific ingredients, or check products tailored to your skin type."
                ),
                'confidence': 0.95,
                'context_product_id': self.context_product_id,
                'suggested_questions': [
                    "What products are best for oily skin?",
                    "Show products under ₹600",
                    "Which products contain Ceramides?"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        # 3. What can you do / Capabilities
        if any(p in q for p in ['what can you do', 'who are you', 'what are your features', 'help me', 'what is your purpose', 'what do you do']):
            return {
                'found': True,
                'topic': 'greeting',
                'intent': 'greeting',
                'intent_label': INTENT_LABELS['greeting'],
                'answer': (
                    "✨ **Here is what I can do with our live catalog:**\n\n"
                    "• 🔍 **Product Search:** Find items by category, skin type, or concern.\n"
                    "• 💰 **Price & Stock Lookup:** Check current discounted prices and availability.\n"
                    "• 🔬 **Ingredient Transparency:** Inspect key active ingredients and full INCI lists.\n"
                    "• 📋 **Usage Instructions:** Step-by-step application directions and patch testing.\n"
                    "• ⚖️ **Product Comparison:** Compare any two products side-by-side.\n"
                    "• 🏷️ **Budget Filters:** Discover top-rated items under a specific budget (e.g. *'under ₹500'*)."
                ),
                'confidence': 0.98,
                'context_product_id': self.context_product_id,
                'suggested_questions': [
                    "What skincare products are available?",
                    "Show products under ₹500",
                    "Compare Vitamin C Serum and Hydration Cream",
                    "How to perform a patch test?"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        # 4. Gratitude
        if any(p in q for p in ['thank you', 'thanks', 'thx', 'appreciate it', 'thank you so much', 'thanks a lot', 'great help']):
            return {
                'found': True,
                'topic': 'gratitude',
                'intent': 'gratitude',
                'intent_label': INTENT_LABELS['gratitude'],
                'answer': (
                    "🙏 You're very welcome! Let me know if you need any more recommendations, ingredient breakdowns, or price checks."
                ),
                'confidence': 0.95,
                'context_product_id': self.context_product_id,
                'suggested_questions': [
                    "Take the recommendation quiz",
                    "Show bestsellers",
                    "What is the shipping policy?"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        # 5. Farewell
        if any(p in q for p in ['bye', 'goodbye', 'see you', 'cya', 'have a good day', 'take care', 'talk to you later']):
            return {
                'found': True,
                'topic': 'farewell',
                'intent': 'farewell',
                'intent_label': INTENT_LABELS['farewell'],
                'answer': (
                    "👋 Goodbye! Have a radiant day. Feel free to come back whenever you need beauty guidance or product advice!"
                ),
                'confidence': 0.95,
                'context_product_id': None,
                'suggested_questions': [
                    "What skincare products are available?",
                    "Take the recommendation quiz"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        return None

    # ── Product-Specific Answer Generator ────────────────────────────
    def _answer_for_product(self, product: Product, intent: str, confidence: float) -> Optional[Dict[str, Any]]:
        """Build precise, direct, and non-repetitive answers grounded strictly in SQLite product attributes."""
        q = self.question_lower
        ref_prod = [{
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'category': product.category,
            'price': float(product.discounted_price or product.price),
            'rating': float(product.rating),
            'skin_type': product.skin_type,
            'concern_tags': product.concern_tags,
        }]

        # Context follow-up questions tailored to this product
        suggested_follow_ups = [
            f"What is the price of {product.name}?",
            f"What are the ingredients in {product.name}?",
            f"How to use {product.name}?",
            f"Show alternatives to {product.name}"
        ]

        # 1. Usage Instructions
        if intent == 'usage_instructions' or any(w in q for w in ['how to use', 'how do i use', 'how should i use', 'apply', 'application', 'directions', 'routine', 'steps', 'when to use', 'frequency']):
            usage_text = product.usage_instructions if product.usage_instructions else "Usage directions are not specified on the product profile. Apply as directed on product packaging."
            return {
                'found': True,
                'topic': 'usage',
                'intent': 'usage_instructions',
                'intent_label': INTENT_LABELS['usage_instructions'],
                'answer': (
                    f"**Application Guide for {product.name} ({product.brand}):**\n\n"
                    f"{usage_text}\n\n"
                    f"• **Target Skin Type:** Suitable for {product.skin_type.capitalize()} skin.\n"
                    f"• **Category:** {product.category.capitalize()}"
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.92,
                'context_product_id': product.id,
                'suggested_questions': [
                    f"What ingredients does {product.name} contain?",
                    f"What is the price of {product.name}?",
                    f"Show alternatives to {product.name}"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # 2. Ingredients & Actives
        if intent == 'ingredients' or any(w in q for w in ['ingredient', 'ingredients', 'actives', 'what is in', 'formula', 'inci', 'composition', 'contain', 'chemical']):
            key_ing = product.key_ingredients if product.key_ingredients else "Key active specifications are not listed in catalog."
            full_ing = product.full_ingredients if product.full_ingredients else "Refer to outer product packaging for complete INCI list."
            return {
                'found': True,
                'topic': 'ingredient',
                'intent': 'ingredients',
                'intent_label': INTENT_LABELS['ingredients'],
                'answer': (
                    f"**Ingredient Profile for {product.name}:**\n\n"
                    f"• **Key Active Ingredients:** {key_ing}\n"
                    f"• **Full INCI Formula:** {full_ing}"
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.92,
                'context_product_id': product.id,
                'suggested_questions': [
                    f"How to use {product.name}?",
                    f"Is {product.name} safe for sensitive skin?",
                    f"What is the price of {product.name}?"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # 3. Safety, Cautions & Suitability
        if intent == 'safety_and_cautions' or any(w in q for w in ['caution', 'cautions', 'warning', 'safe', 'safety', 'side effect', 'irritat', 'allergy', 'suitable for', 'suitability']):
            caution_text = product.caution_info if product.caution_info else "For external cosmetic use only. Discontinue if irritation occurs."
            return {
                'found': True,
                'topic': 'caution',
                'intent': 'safety_and_cautions',
                'intent_label': INTENT_LABELS['safety_and_cautions'],
                'answer': (
                    f"**Safety & Suitability for {product.name}:**\n\n"
                    f"• **Compatibility:** Formulated for **{product.skin_type.capitalize()}** skin types.\n"
                    f"• **Caution Notice:** {caution_text}\n"
                    f"• **Patch Test Recommendation:** Apply 2–3 drops to inner forearm for 24 hours prior to first facial use."
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.90,
                'context_product_id': product.id,
                'suggested_questions': [
                    f"How to use {product.name}?",
                    f"What ingredients are in {product.name}?",
                    f"What is the price of {product.name}?"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # 4. Pricing, Discount & Stock
        if intent in ['price_and_discount', 'availability_and_stock'] or any(w in q for w in ['price', 'cost', 'how much', 'discount', 'stock', 'available', 'mrp', 'rate']):
            orig_str = f" (Original MRP: ₹{product.price})" if product.discount_percent > 0 else ""
            discount_note = f" with a **{product.discount_percent}% discount**" if product.discount_percent > 0 else ""
            stock_label = product.availability.replace('_', ' ').title()
            return {
                'found': True,
                'topic': 'pricing',
                'intent': 'price_and_discount',
                'intent_label': INTENT_LABELS['price_and_discount'],
                'answer': (
                    f"**Pricing & Availability for {product.name}:**\n\n"
                    f"• **Current Price:** **₹{product.discounted_price or product.price}**{orig_str}{discount_note}\n"
                    f"• **Stock Status:** **{stock_label}**\n"
                    f"• **Customer Rating:** ⭐ {product.rating}/5.0 ({product.review_count} reviews)"
                ),
                'confidence': round(confidence, 2) if confidence > 0 else 0.95,
                'context_product_id': product.id,
                'suggested_questions': [
                    f"What are the ingredients in {product.name}?",
                    f"How to use {product.name}?",
                    f"Show alternatives to {product.name}"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # 5. Alternatives & Related Products
        if intent == 'comparison_and_alternatives' or any(w in q for w in ['alternative', 'alternatives', 'similar', 'other product', 'like this']):
            alts = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
            alt_lines = [f"• **{p.name}** ({p.brand}) — ₹{p.discounted_price or p.price} (Actives: {p.key_ingredients})" for p in alts]
            alt_refs = [{
                'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category,
                'price': float(p.discounted_price or p.price), 'rating': float(p.rating),
                'skin_type': p.skin_type, 'concern_tags': p.concern_tags
            } for p in alts]

            return {
                'found': True,
                'topic': 'comparison',
                'intent': 'comparison_and_alternatives',
                'intent_label': INTENT_LABELS['comparison_and_alternatives'],
                'answer': (
                    f"**Alternatives to {product.name} in {product.category.capitalize()}:**\n\n" +
                    ('\n'.join(alt_lines) if alt_lines else "No alternative products found in this category.") +
                    "\n\n*You can also use our Formula Comparison Studio to view detailed side-by-side specs.*"
                ),
                'confidence': 0.88,
                'context_product_id': product.id,
                'suggested_questions': [
                    f"What is the price of {product.name}?",
                    "Show products under ₹500",
                    "Take the recommendation quiz"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod + alt_refs,
            }

        # 6. Default Product Overview & Purpose
        desc = product.description if product.description else "No marketing description provided in catalog."
        return {
            'found': True,
            'topic': 'overview',
            'intent': 'product_purpose',
            'intent_label': INTENT_LABELS['product_purpose'],
            'answer': (
                f"**{product.name}** by {product.brand} ({product.category.capitalize()}):\n\n"
                f"{desc}\n\n"
                f"• **Price:** ₹{product.discounted_price or product.price}\n"
                f"• **Key Actives:** {product.key_ingredients or 'Verified gentle active formulation'}\n"
                f"• **Compatibility:** {product.skin_type.capitalize()} skin types ({product.concern_tags or 'General care'})"
            ),
            'confidence': 0.88,
            'context_product_id': product.id,
            'suggested_questions': suggested_follow_ups,
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prod,
        }

    # ── Multi-Product Comparison Handler ─────────────────────────────
    def _handle_product_comparison(self) -> Optional[Dict[str, Any]]:
        q = self.question_lower
        if not any(w in q for w in ['compare', ' vs ', ' versus ', 'difference between']):
            return None

        # Extract two products from question
        all_prods = list(Product.objects.all())
        all_prods.sort(key=lambda p: len(p.name), reverse=True)
        matched_prods = []

        for prod in all_prods:
            if prod.name.lower() in q:
                if prod not in matched_prods:
                    matched_prods.append(prod)
            else:
                words = prod.name.lower().split()
                if len(words) >= 2 and ' '.join(words[:2]) in q and prod not in matched_prods:
                    matched_prods.append(prod)

        if len(matched_prods) >= 2:
            p1, p2 = matched_prods[0], matched_prods[1]
            ref_prods = [
                {'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price), 'rating': float(p.rating), 'skin_type': p.skin_type, 'concern_tags': p.concern_tags}
                for p in [p1, p2]
            ]
            answer_text = (
                f"**Formula Comparison: {p1.name} vs {p2.name}**\n\n"
                f"| Specification | {p1.name} | {p2.name} |\n"
                f"| :--- | :--- | :--- |\n"
                f"| **Brand** | {p1.brand} | {p2.brand} |\n"
                f"| **Category** | {p1.category.capitalize()} | {p2.category.capitalize()} |\n"
                f"| **Price** | ₹{p1.discounted_price or p1.price} | ₹{p2.discounted_price or p2.price} |\n"
                f"| **Skin Type** | {p1.skin_type.capitalize()} | {p2.skin_type.capitalize()} |\n"
                f"| **Key Actives** | {p1.key_ingredients} | {p2.key_ingredients} |\n"
                f"| **Target Concerns** | {p1.concern_tags} | {p2.concern_tags} |\n"
                f"| **Rating** | ⭐ {p1.rating}/5.0 | ⭐ {p2.rating}/5.0 |\n\n"
                f"*Both products are verified genuine formulations available in our catalog.*"
            )
            return {
                'found': True,
                'topic': 'comparison',
                'intent': 'comparison_and_alternatives',
                'intent_label': INTENT_LABELS['comparison_and_alternatives'],
                'answer': answer_text,
                'confidence': 0.95,
                'context_product_id': p1.id,
                'suggested_questions': [
                    f"How to use {p1.name}?",
                    f"How to use {p2.name}?",
                    "Show products under ₹500"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prods,
            }

        return None

    # ── Budget-Based Search Handler ──────────────────────────────────
    def _handle_budget_search(self) -> Optional[Dict[str, Any]]:
        q = self.question_lower
        budget_pattern = r'(?:under|below|budget|less than|within|max|maximum)\s*(?:of)?\s*(?:₹|rs\.?|inr)?\s*(\d+)'
        match = re.search(budget_pattern, q)

        if not match:
            # Alternate pattern e.g. "500 rupees", "budget 600"
            alt_match = re.search(r'(\d+)\s*(?:rupees|rs|inr)\s*(?:budget|or less|under)', q)
            if alt_match:
                match = alt_match

        if not match:
            return None

        try:
            budget_amount = Decimal(match.group(1))
        except Exception:
            return None

        # Filter products where discounted_price <= budget_amount
        all_prods = Product.objects.all()
        matching_prods = [p for p in all_prods if p.discounted_price <= budget_amount]
        # Sort by rating descending
        matching_prods.sort(key=lambda p: (p.rating, p.review_count), reverse=True)

        if not matching_prods:
            return {
                'found': False,
                'topic': 'budget_search',
                'intent': 'budget_search',
                'intent_label': INTENT_LABELS['budget_search'],
                'answer': f"We currently do not have products priced under ₹{budget_amount} in our catalog. Our most affordable items start at ₹299.",
                'confidence': 0.92,
                'context_product_id': None,
                'suggested_questions': [
                    "Show products under ₹600",
                    "What skincare products are available?",
                    "Show bestsellers"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        top_prods = matching_prods[:4]
        prod_lines = [f"• **{p.name}** ({p.brand}) — **₹{p.discounted_price or p.price}** (⭐ {p.rating})" for p in top_prods]
        ref_prods = [
            {'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price), 'rating': float(p.rating), 'skin_type': p.skin_type, 'concern_tags': p.concern_tags}
            for p in top_prods
        ]

        return {
            'found': True,
            'topic': 'budget_search',
            'intent': 'budget_search',
            'intent_label': INTENT_LABELS['budget_search'],
            'answer': (
                f"Here are {len(matching_prods)} top-rated product(s) within your budget of **₹{budget_amount}**:\n\n" +
                '\n'.join(prod_lines) +
                "\n\n*Click on any product card below to view full ingredients and specifications.*"
            ),
            'confidence': 0.95,
            'context_product_id': top_prods[0].id if top_prods else None,
            'suggested_questions': [
                f"What is the price of {top_prods[0].name}?",
                "Which products contain Vitamin C?",
                "Take the recommendation quiz"
            ],
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    # ── Catalog Ingredient Search Handler ────────────────────────────
    def _answer_ingredient_search(self) -> Optional[Dict[str, Any]]:
        actives = [
            'vitamin c', 'niacinamide', 'hyaluronic', 'ceramide', 'ceramides', 'squalane',
            'aloe vera', 'keratin', 'biotin', 'caffeine', 'argan', 'cocoa butter',
            'charcoal', 'jojoba', 'zinc', 'spf', 'sunscreen', 'salicylic', 'salicylic acid', 'ferulic'
        ]

        found_active = next((a for a in actives if a in self.question_lower), None)
        if not found_active:
            return None

        # Clean search term
        search_term = found_active.replace('ceramides', 'ceramide')
        matches = Product.objects.filter(
            Q(key_ingredients__icontains=search_term) |
            Q(full_ingredients__icontains=search_term) |
            Q(description__icontains=search_term)
        )

        if not matches.exists():
            return {
                'found': False,
                'topic': 'ingredient',
                'intent': 'ingredients',
                'intent_label': INTENT_LABELS['ingredients'],
                'answer': f"We currently do not have any products containing **'{found_active.title()}'** in our catalog.",
                'confidence': 0.9,
                'context_product_id': None,
                'suggested_questions': [
                    "Which products contain Vitamin C?",
                    "Which products contain Niacinamide?",
                    "Show all skincare products"
                ],
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        top_matches = matches[:4]
        prods_info = [f"• **{p.name}** ({p.brand}) — ₹{p.discounted_price or p.price} (Key: {p.key_ingredients})" for p in top_matches]
        ref_prods = [
            {'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price), 'rating': float(p.rating), 'skin_type': p.skin_type, 'concern_tags': p.concern_tags}
            for p in top_matches
        ]

        return {
            'found': True,
            'topic': 'ingredient',
            'intent': 'ingredients',
            'intent_label': INTENT_LABELS['ingredients'],
            'answer': (
                f"We found {matches.count()} product(s) containing **{found_active.title()}** in our catalog:\n\n" +
                '\n'.join(prods_info)
            ),
            'confidence': 0.94,
            'context_product_id': top_matches[0].id if top_matches else None,
            'suggested_questions': [
                f"How to use {top_matches[0].name}?",
                f"What is the price of {top_matches[0].name}?",
                "Show products under ₹500"
            ],
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    # ── Concern Search Handler ───────────────────────────────────────
    def _answer_concern_search(self) -> Optional[Dict[str, Any]]:
        concerns = [
            'acne', 'dark spots', 'pigmentation', 'hydration', 'dryness', 'frizz',
            'hair fall', 'hair loss', 'dullness', 'glow', 'anti-aging', 'fine lines',
            'wrinkles', 'pores', 'blemish', 'blemishes', 'sun protection', 'tan'
        ]

        found_concern = next((c for c in concerns if c in self.question_lower), None)
        if not found_concern:
            return None

        # Normalize concern term
        search_key = 'acne' if found_concern in ['acne', 'blemish', 'blemishes'] else found_concern
        search_key = 'dark spots' if found_concern in ['dark spots', 'pigmentation'] else search_key
        search_key = 'hydration' if found_concern in ['hydration', 'dryness'] else search_key
        search_key = 'frizz' if found_concern in ['frizz'] else search_key
        search_key = 'anti-aging' if found_concern in ['anti-aging', 'fine lines', 'wrinkles'] else search_key

        matches = Product.objects.filter(
            Q(concern_tags__icontains=search_key) |
            Q(description__icontains=search_key)
        )

        if not matches.exists():
            return None

        top_matches = matches[:4]
        prods_info = [f"• **{p.name}** ({p.brand}) — ₹{p.discounted_price or p.price} ({p.concern_tags})" for p in top_matches]
        ref_prods = [
            {'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price), 'rating': float(p.rating), 'skin_type': p.skin_type, 'concern_tags': p.concern_tags}
            for p in top_matches
        ]

        return {
            'found': True,
            'topic': 'concern',
            'intent': 'skin_type_recommendation',
            'intent_label': INTENT_LABELS['skin_type_recommendation'],
            'answer': (
                f"For **{found_concern.title()}**, our catalog features {matches.count()} targeted product(s):\n\n" +
                '\n'.join(prods_info) +
                "\n\n*Take the SmartMatch Quiz for personalized compatibility scoring.*"
            ),
            'confidence': 0.92,
            'context_product_id': top_matches[0].id if top_matches else None,
            'suggested_questions': [
                f"What are the ingredients in {top_matches[0].name}?",
                "Take the recommendation quiz",
                "Show products under ₹600"
            ],
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    # ── Category Search Handler ──────────────────────────────────────
    def _answer_category_search(self) -> Optional[Dict[str, Any]]:
        categories = ['skincare', 'haircare', 'makeup', 'fragrance', 'bodycare', 'nailcare', 'tools']
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

        top_prods = prods[:4]
        prods_info = [f"• **{p.name}** — ₹{p.discounted_price or p.price} (⭐ {p.rating})" for p in top_prods]
        ref_prods = [
            {'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price), 'rating': float(p.rating), 'skin_type': p.skin_type, 'concern_tags': p.concern_tags}
            for p in top_prods
        ]

        return {
            'found': True,
            'topic': 'category',
            'intent': 'skin_type_recommendation',
            'intent_label': INTENT_LABELS['skin_type_recommendation'],
            'answer': (
                f"We offer {prods.count()} verified product(s) in **{matched_cat.capitalize()}**:\n\n" +
                '\n'.join(prods_info) +
                "\n\n*Select any product card below for complete ingredient transparency and usage directions.*"
            ),
            'confidence': 0.92,
            'context_product_id': top_prods[0].id if top_prods else None,
            'suggested_questions': [
                f"What is the price of {top_prods[0].name}?",
                f"Show {matched_cat} products under ₹500",
                "Take the recommendation quiz"
            ],
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    # ── Skin-Type Search Handler ─────────────────────────────────────
    def _answer_skin_type_search(self) -> Optional[Dict[str, Any]]:
        skin_types = ['oily', 'dry', 'sensitive', 'combination', 'normal']
        matched_st = next((st for st in skin_types if st in self.question_lower), None)

        if not matched_st:
            return None

        prods = Product.objects.filter(
            Q(skin_type__iexact=matched_st) | Q(skin_type='all')
        ).filter(category='skincare')

        if not prods.exists():
            return None

        top_prods = prods[:4]
        prods_info = [f"• **{p.name}** ({p.brand}) — ₹{p.discounted_price or p.price} (Actives: {p.key_ingredients})" for p in top_prods]
        ref_prods = [
            {'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price), 'rating': float(p.rating), 'skin_type': p.skin_type, 'concern_tags': p.concern_tags}
            for p in top_prods
        ]

        return {
            'found': True,
            'topic': 'skin_type',
            'intent': 'skin_type_recommendation',
            'intent_label': INTENT_LABELS['skin_type_recommendation'],
            'answer': (
                f"For **{matched_st.capitalize()} Skin**, our catalog offers {prods.count()} compatible formula(s):\n\n" +
                '\n'.join(prods_info)
            ),
            'confidence': 0.90,
            'context_product_id': top_prods[0].id if top_prods else None,
            'suggested_questions': [
                f"What are the ingredients in {top_prods[0].name}?",
                "Take the recommendation quiz",
                "Show products under ₹500"
            ],
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    # ── Unfound Product Detection ────────────────────────────────────
    def _check_unfound_product_mention(self) -> Optional[Dict[str, Any]]:
        # Check if user asked specifically for a product that does not exist in SQLite
        keywords = ['price of', 'cost of', 'ingredients in', 'ingredients of', 'how to use', 'buy', 'reviews for', 'details of']
        generic_words = ['a product', 'the product', 'this product', 'it', 'this', 'that', 'products', 'a cream', 'a serum', 'a moisturizer', 'a cleanser', 'skincare', 'haircare']

        for kw in keywords:
            if kw in self.question_lower:
                part = self.question_lower.split(kw, 1)[1].strip(' ?.')
                # If part is not empty and not just generic words
                if part and len(part) >= 3 and part not in generic_words:
                    return {
                        'found': False,
                        'topic': 'unfound_product',
                        'intent': 'unavailable',
                        'intent_label': INTENT_LABELS['unavailable'],
                        'answer': (
                            f"The product **\"{part.title()}\"** could not be found in our verified catalog.\n\n"
                            "Our catalog currently features authentic Joyory beauty products. "
                            "You can explore our skincare, haircare, and bodycare items or take our SmartMatch Quiz."
                        ),
                        'confidence': 0.88,
                        'context_product_id': None,
                        'suggested_questions': [
                            "What skincare products are available?",
                            "Show bestsellers",
                            "Show products under ₹500"
                        ],
                        'disclaimer': DISCLAIMER,
                        'is_disclaimer_applicable': True,
                        'referenced_products': [],
                    }
        return None
