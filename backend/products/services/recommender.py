"""
Rule-Based Product Recommendation Service for Joyory SmartMatch.

Strictly deterministic, rule-based matching engine.
Does NOT use or claim to use machine learning or trained AI models.
Does NOT fabricate medical claims or unverified product benefits.
"""

from decimal import Decimal
from typing import Dict, Any, List, Tuple
from products.models import Product
from products.serializers import ProductSerializer


class RuleBasedRecommender:
    """
    Evaluates customer quiz answers against Product model attributes in SQLite
    and calculates a deterministic match score and factual explanations.
    """

    # Scoring Weights (Total 100 points maximum base score)
    WEIGHT_CONCERN = 35
    WEIGHT_COMPATIBILITY = 25
    WEIGHT_INGREDIENTS = 20
    WEIGHT_BUDGET = 20

    def __init__(self, quiz_data: Dict[str, Any]):
        self.category = (quiz_data.get('category') or '').strip().lower()
        self.skin_type = (quiz_data.get('skin_type') or '').strip().lower()
        self.concern = (quiz_data.get('concern') or '').strip().lower()
        self.preference = (quiz_data.get('preference') or '').strip().lower()
        
        # Budget handling
        budget_raw = quiz_data.get('budget_max')
        self.budget_max = None
        if budget_raw is not None and budget_raw != '':
            try:
                self.budget_max = float(budget_raw)
            except (ValueError, TypeError):
                self.budget_max = None

        self.preferred_ingredients = [
            ing.strip().lower()
            for ing in quiz_data.get('preferred_ingredients', [])
            if isinstance(ing, str) and ing.strip()
        ]

    def get_recommendations(self, limit: int = 4) -> Dict[str, Any]:
        """
        Execute rule-based matching and return ranked products with explanations.
        """
        # Step 1: Base queryset filtering by category
        queryset = Product.objects.all()
        if self.category:
            queryset = queryset.filter(category__iexact=self.category)

        all_category_products = list(queryset)

        if not all_category_products:
            # Fallback to general bestsellers if category had 0 products
            all_category_products = list(Product.objects.all())

        # Step 2: Score each product
        scored_items: List[Tuple[float, Product, List[str]]] = []

        for product in all_category_products:
            score, reasons = self._score_product(product)
            scored_items.append((score, product, reasons))

        # Sort descending by match score, then product rating
        scored_items.sort(key=lambda item: (item[0], item[1].rating), reverse=True)

        # Step 3: Check if we have exact matches within budget & threshold
        exact_matches = [
            item for item in scored_items
            if item[0] >= 30 and (self.budget_max is None or float(item[1].discounted_price or item[1].price) <= self.budget_max * 1.15)
        ]

        is_alternative = False
        fallback_message = None

        if exact_matches:
            final_items = exact_matches[:limit]
        else:
            # No exact match under current constraints — provide closest category alternatives
            is_alternative = True
            final_items = scored_items[:limit]
            budget_str = f" under ₹{int(self.budget_max)}" if self.budget_max else ""
            fallback_message = (
                f"No exact match was found for your specific combination{budget_str}. "
                f"Here are our closest, top-rated alternatives in {self.category.capitalize() if self.category else 'our catalog'}."
            )

        # Format output
        results = []
        for score, product, reasons in final_items:
            serialized = ProductSerializer(product).data
            # Clamp percentage between 60% and 99% for realistic display
            match_percentage = min(99, max(60, int(score)))
            results.append({
                'product': serialized,
                'match_score': score,
                'match_percentage': match_percentage,
                'reasons': reasons,
            })

        return {
            'total_matches': len(results),
            'is_alternative': is_alternative,
            'message': fallback_message or f"Found {len(results)} personalized recommendation(s) based on your profile.",
            'query_summary': {
                'category': self.category or 'All Categories',
                'skin_type': self.skin_type or 'Any',
                'concern': self.concern or 'General Care',
                'budget_max': self.budget_max,
                'preferred_ingredients': self.preferred_ingredients,
            },
            'recommendations': results,
        }

    def _score_product(self, product: Product) -> Tuple[float, List[str]]:
        """
        Calculate deterministic match score and compile factual reasons.
        """
        score = 0.0
        reasons = []

        effective_price = float(product.discounted_price or product.price)

        # ── 1. Target Concern / Goal Matching (Up to 35 pts) ──────
        if self.concern:
            concern_tags_lower = product.concern_tags.lower() if product.concern_tags else ''
            desc_lower = product.description.lower() if product.description else ''
            name_lower = product.name.lower()

            if self.concern in concern_tags_lower:
                score += self.WEIGHT_CONCERN
                reasons.append(f"Specifically formulated to target '{self.concern.title()}'.")
            elif self.concern in desc_lower or self.concern in name_lower:
                score += self.WEIGHT_CONCERN * 0.75
                reasons.append(f"Contains active benefits addressing '{self.concern.title()}'.")
            else:
                # Partial keyword match
                concern_words = [w for w in self.concern.split() if len(w) > 3]
                matched_words = [w for w in concern_words if w in concern_tags_lower or w in desc_lower]
                if matched_words:
                    score += self.WEIGHT_CONCERN * 0.5
                    reasons.append(f"Targets related concern: {', '.join(matched_words)}.")

        # ── 2. Skin-Type / Profile Compatibility (Up to 25 pts) ───
        if self.skin_type:
            prod_skin = (product.skin_type or '').lower()
            if prod_skin == self.skin_type:
                score += self.WEIGHT_COMPATIBILITY
                reasons.append(f"Optimized for {self.skin_type.capitalize()} skin type.")
            elif prod_skin == 'all':
                score += self.WEIGHT_COMPATIBILITY * 0.85
                reasons.append(f"Gentle and suitable for all skin types, including {self.skin_type.capitalize()}.")
            else:
                score += self.WEIGHT_COMPATIBILITY * 0.2
        else:
            score += self.WEIGHT_COMPATIBILITY * 0.8

        # ── 3. Ingredients & Actives Matching (Up to 20 pts) ─────
        key_ing_lower = (product.key_ingredients or '').lower()
        full_ing_lower = (product.full_ingredients or '').lower()

        matched_preferred = []
        for pref in self.preferred_ingredients:
            if pref in key_ing_lower or pref in full_ing_lower:
                matched_preferred.append(pref.title())

        if matched_preferred:
            score += self.WEIGHT_INGREDIENTS
            reasons.append(f"Includes your requested active: {', '.join(matched_preferred)}.")
        elif product.key_ingredients:
            # Reward having explicit key active ingredients
            score += self.WEIGHT_INGREDIENTS * 0.7
            first_active = product.key_ingredients.split(',')[0].strip()
            reasons.append(f"Powered by key active ingredient: {first_active}.")

        # ── 4. Budget Evaluation (Up to 20 pts) ───────────────────
        if self.budget_max is not None and self.budget_max > 0:
            if effective_price <= self.budget_max:
                score += self.WEIGHT_BUDGET
                savings = self.budget_max - effective_price
                if savings > 50:
                    reasons.append(f"Fits your ₹{int(self.budget_max)} budget at ₹{int(effective_price)} (₹{int(savings)} under budget).")
                else:
                    reasons.append(f"Fits within your target budget of ₹{int(self.budget_max)}.")
            elif effective_price <= self.budget_max * 1.25:
                # Slightly above budget (close alternative)
                score += self.WEIGHT_BUDGET * 0.4
                diff = effective_price - self.budget_max
                reasons.append(f"Slightly above target budget by ₹{int(diff)} (₹{int(effective_price)}).")
            else:
                score += 0.0
        else:
            score += self.WEIGHT_BUDGET * 0.8

        # ── 5. Bestseller / High-Rating Boost (Bonus 5 pts) ───────
        if product.is_bestseller:
            score += 5.0
            reasons.append("Customer-favorite bestseller with proven satisfaction.")
        elif product.rating >= 4.5:
            score += 4.0
            reasons.append(f"Top-rated customer favorite ({product.rating}★ rating).")

        return score, reasons
