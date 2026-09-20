"""
Rule-Based Product FAQ Assistant Service for Joyory SmartMatch.

Resolves product and beauty queries strictly using SQLite product records
and a verified knowledge base.
Does NOT use paid AI APIs, external models, or fabricate medical claims.
Clearly labels responses as coming from a demo FAQ assistant.
"""

import re
from typing import Dict, Any, List, Optional
from django.db.models import Q
from products.models import Product


DISCLAIMER = "⚠️ Demo FAQ Assistant: This assistant is an automated catalog helper, not a medical professional. All information is derived directly from product catalog specifications for demonstration only and does not constitute medical advice, treatment, or dermatological diagnosis."


CURATED_FAQS = [
    {
        'keywords': ['smartmatch', 'how it works', 'how does smartmatch work', 'algorithm', 'recommendation'],
        'answer': "Joyory SmartMatch uses a deterministic rule-based matching engine. It evaluates your selected category, skin type compatibility, target concerns, key active ingredients, and budget against verified product attributes to recommend the best match.",
    },
    {
        'keywords': ['authentic', 'real', 'fake', 'genuine', 'original'],
        'answer': "All products listed in the Joyory SmartMatch catalog are simulated 100% authentic formulations with full INCI ingredient transparency and verified brand specifications.",
    },
    {
        'keywords': ['shipping', 'delivery', 'cost', 'fee', 'charge'],
        'answer': "Standard shipping is FREE on orders above ₹499. For orders below ₹499, a flat shipping fee of ₹50 applies. Estimated delivery is 2–3 business days.",
    },
    {
        'keywords': ['payment', 'pay', 'card', 'checkout', 'cod'],
        'answer': "This is a hackathon prototype with a simulated demo checkout. We support demo Cash on Delivery and demo Net Banking. No real payment or credit card is processed.",
    },
    {
        'keywords': ['patch test', 'how to patch test', 'allergy'],
        'answer': "To perform a patch test: Apply 2–3 drops of the formula to a small area of clean skin on your inner forearm. Wait 24 hours. If no redness, itching, or irritation occurs, the product is generally suitable for regular use.",
    },
]


class ProductFaqAssistant:
    """
    Rule-based assistant for answering customer questions about products,
    ingredients, usage routines, and cautions.
    """

    def __init__(self, question: str, product_id: Optional[int] = None):
        self.raw_question = (question or '').strip()
        self.question_lower = self.raw_question.lower()
        self.product_id = product_id

    def answer_query(self) -> Dict[str, Any]:
        """
        Main query resolver pipeline.
        """
        if not self.raw_question:
            return {
                'found': False,
                'answer': "Please ask a question about our products, ingredients, or usage instructions.",
                'disclaimer': DISCLAIMER,
                'referenced_products': [],
            }

        # Step 1: Specific Product Context Query
        if self.product_id:
            try:
                product = Product.objects.get(pk=self.product_id)
                prod_answer = self._answer_for_specific_product(product)
                if prod_answer:
                    return prod_answer
            except Product.DoesNotExist:
                pass

        # Step 2: Try matching product mentioned by name in query
        matched_product = self._find_product_by_name_in_query()
        if matched_product:
            prod_answer = self._answer_for_specific_product(matched_product)
            if prod_answer:
                return prod_answer

        # Step 3: Ingredient & Formulation Queries (e.g. "Which products have Ceramides?")
        ing_answer = self._answer_ingredient_query()
        if ing_answer:
            return ing_answer

        # Step 4: Category Queries (e.g. "What haircare products do you have?")
        cat_answer = self._answer_category_query()
        if cat_answer:
            return cat_answer

        # Step 5: Skin-Type / Concern Query (e.g. "What is best for dry skin?")
        skin_answer = self._answer_skin_type_query()
        if skin_answer:
            return skin_answer

        # Step 6: Curated Platform / General FAQs
        general_answer = self._answer_general_faq()
        if general_answer:
            return general_answer

        # Step 7: Transparent Fallback when information is unavailable
        return {
            'found': False,
            'topic': 'unavailable',
            'intent': 'unavailable',
            'answer': (
                f"Information regarding '{self.raw_question}' is not currently available in the Joyory product catalog. "
                "You can explore our product details, ingredients, and instructions directly on each product page. "
                "For specific medical concerns, please consult a dermatologist."
            ),
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': [],
        }

    def _find_product_by_name_in_query(self) -> Optional[Product]:
        """Search if any product name is a substring in the user's question."""
        for prod in Product.objects.all():
            if prod.name.lower() in self.question_lower:
                return prod
            # Also check simple keywords like "vitamin c serum", "niacinamide gel", "aloe vera"
            words = prod.name.lower().split()
            if len(words) >= 2 and ' '.join(words[:2]) in self.question_lower:
                return prod
        return None

    def _answer_for_specific_product(self, product: Product) -> Optional[Dict[str, Any]]:
        """Extract specific answer about a given product."""
        q = self.question_lower
        ref_prod = [{
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'category': product.category,
            'price': float(product.discounted_price or product.price),
        }]

        # Usage Instructions
        if any(w in q for w in ['how to use', 'how do i use', 'how should i use', 'how to apply', 'how should i apply', 'apply', 'when to use', 'usage', 'application', 'directions', 'routine', 'steps']):
            return {
                'found': True,
                'topic': 'usage',
                'intent': 'usage',
                'answer': (
                    f"**How to use {product.name} ({product.brand}):**\n\n"
                    f"{product.usage_instructions or 'Apply as directed on clean skin/hair.'}\n\n"
                    f"**Target Skin Type:** {product.skin_type.capitalize()}."
                ),
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # Ingredients / Actives
        if any(w in q for w in ['ingredient', 'ingredients', 'actives', 'what is in', 'formula', 'inci', 'composition', 'contain']):
            return {
                'found': True,
                'topic': 'ingredient',
                'intent': 'ingredient',
                'answer': (
                    f"**Ingredients in {product.name}:**\n\n"
                    f"• **Key Actives:** {product.key_ingredients or 'Clean formulation'}\n"
                    f"• **Full INCI:** {product.full_ingredients or 'Refer to product packaging'}"
                ),
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # Caution / Warnings / Safety
        if any(w in q for w in ['caution', 'cautions', 'warning', 'warnings', 'precaution', 'precautions', 'safe', 'safety', 'side effect', 'sun', 'irritat', 'allergy']):
            return {
                'found': True,
                'topic': 'caution',
                'intent': 'caution',
                'answer': (
                    f"**Safety & Caution Information for {product.name}:**\n\n"
                    f"{product.caution_info or 'For external use only. Patch test before first use.'}"
                ),
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # Price / Discount / Stock
        if any(w in q for w in ['price', 'cost', 'how much', 'discount', 'stock', 'available']):
            price_str = f"₹{product.discounted_price or product.price}"
            orig_str = f" (Original: ₹{product.price})" if product.discount_percent > 0 else ""
            return {
                'found': True,
                'topic': 'pricing',
                'intent': 'pricing',
                'answer': (
                    f"**{product.name}** is currently priced at **{price_str}**{orig_str} "
                    f"and is **{product.availability.replace('_', ' ').title()}**."
                ),
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': ref_prod,
            }

        # General Product Description
        return {
            'found': True,
            'topic': 'overview',
            'intent': 'overview',
            'answer': (
                f"**{product.name}** by {product.brand} ({product.category.capitalize()}):\n\n"
                f"{product.description}\n\n"
                f"• **Key Ingredients:** {product.key_ingredients}\n"
                f"• **Intended for:** {product.skin_type.capitalize()} skin types ({product.concern_tags})"
            ),
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prod,
        }

    def _answer_ingredient_query(self) -> Optional[Dict[str, Any]]:
        """Search products by active ingredients mentioned in question."""
        active_keywords = [
            'vitamin c', 'niacinamide', 'hyaluronic', 'ceramide', 'squalane',
            'aloe vera', 'keratin', 'biotin', 'caffeine', 'argan', 'cocoa butter',
            'charcoal', 'jojoba', 'zinc', 'spf', 'sunscreen'
        ]

        found_active = None
        for active in active_keywords:
            if active in self.question_lower:
                found_active = active
                break

        if not found_active:
            return None

        # Search matching products
        matches = Product.objects.filter(
            Q(key_ingredients__icontains=found_active) |
            Q(full_ingredients__icontains=found_active) |
            Q(description__icontains=found_active)
        )

        if not matches.exists():
            return {
                'found': False,
                'topic': 'ingredient',
                'intent': 'ingredient',
                'answer': f"We currently do not have any products containing '{found_active.title()}' in our SQLite catalog.",
                'disclaimer': DISCLAIMER,
                'is_disclaimer_applicable': True,
                'referenced_products': [],
            }

        prods_info = []
        ref_prods = []
        for p in matches[:3]:
            prods_info.append(f"• **{p.name}** ({p.brand}) — ₹{p.discounted_price or p.price} (Key Actives: {p.key_ingredients})")
            ref_prods.append({'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price)})

        return {
            'found': True,
            'topic': 'ingredient',
            'intent': 'ingredient',
            'answer': (
                f"Here are the product(s) containing **{found_active.title()}** in our catalog:\n\n" +
                '\n'.join(prods_info)
            ),
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    def _answer_category_query(self) -> Optional[Dict[str, Any]]:
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

        prods_info = []
        ref_prods = []
        for p in prods[:4]:
            prods_info.append(f"• **{p.name}** — ₹{p.discounted_price or p.price} ({p.concern_tags})")
            ref_prods.append({'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price)})

        return {
            'found': True,
            'topic': 'category',
            'intent': 'category',
            'answer': (
                f"We offer {prods.count()} product(s) in **{matched_cat.capitalize()}**:\n\n" +
                '\n'.join(prods_info)
            ),
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    def _answer_skin_type_query(self) -> Optional[Dict[str, Any]]:
        """Search products by skin type or concern."""
        skin_types = ['oily', 'dry', 'sensitive', 'combination']
        matched_st = None
        for st in skin_types:
            if st in self.question_lower:
                matched_st = st
                break

        if not matched_st:
            return None

        prods = Product.objects.filter(
            Q(skin_type__iexact=matched_st) | Q(skin_type='all')
        ).filter(category='skincare')

        if not prods.exists():
            return None

        prods_info = []
        ref_prods = []
        for p in prods[:3]:
            prods_info.append(f"• **{p.name}** ({p.brand}) — ₹{p.discounted_price or p.price} (Key: {p.key_ingredients})")
            ref_prods.append({'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': float(p.discounted_price or p.price)})

        return {
            'found': True,
            'topic': 'skin_type',
            'intent': 'skin_type',
            'answer': (
                f"For **{matched_st.capitalize()} Skin**, our catalog offers the following compatible formulas:\n\n" +
                '\n'.join(prods_info)
            ),
            'disclaimer': DISCLAIMER,
            'is_disclaimer_applicable': True,
            'referenced_products': ref_prods,
        }

    def _answer_general_faq(self) -> Optional[Dict[str, Any]]:
        """Search curated FAQs."""
        for item in CURATED_FAQS:
            if any(k in self.question_lower for k in item['keywords']):
                return {
                    'found': True,
                    'topic': 'platform_faq',
                    'intent': 'platform_faq',
                    'answer': item['answer'],
                    'disclaimer': DISCLAIMER,
                    'is_disclaimer_applicable': True,
                    'referenced_products': [],
                }
        return None
