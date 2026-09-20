"""
Beauty Routine Builder for Joyory SmartMatch.

Generates a personalised morning and evening skincare routine
using only actual products from the SQLite product catalog.

Rule-based step mapping — no ML or external APIs.
"""

from typing import Dict, Any, List, Optional
from products.models import Product
from products.serializers import ProductListSerializer


# ── Routine step definitions ──────────────────────────────────────────────────
# Each step has: step_name, icon, instruction, time (am/pm/both), category filters, concern keywords
ROUTINE_STEPS = [
    {
        'step': 1,
        'name': 'Cleanser',
        'icon': '🧴',
        'instruction': 'Apply to wet face, massage gently in circular motions for 60 seconds, then rinse thoroughly with lukewarm water.',
        'time': 'both',
        'categories': ['skincare'],
        'keywords': ['cleanser', 'wash', 'foam', 'gel cleanser', 'cleansing'],
    },
    {
        'step': 2,
        'name': 'Toner / Essence',
        'icon': '💧',
        'instruction': 'Apply a small amount to a cotton pad or palm and press gently into clean skin to balance pH and prep for actives.',
        'time': 'both',
        'categories': ['skincare'],
        'keywords': ['toner', 'essence', 'mist', 'hydrating toner', 'balancing'],
    },
    {
        'step': 3,
        'name': 'Active Serum',
        'icon': '⚗️',
        'instruction': 'Apply 3–4 drops to face and neck. Pat gently — do not rub. Allow 60–90 seconds to absorb before the next step.',
        'time': 'both',
        'categories': ['skincare'],
        'keywords': ['serum', 'ampoule', 'concentrate', 'booster'],
    },
    {
        'step': 4,
        'name': 'Eye Cream',
        'icon': '👁️',
        'instruction': 'Using your ring finger, gently tap a small amount around the orbital bone. Never rub the delicate eye area.',
        'time': 'both',
        'categories': ['skincare'],
        'keywords': ['eye cream', 'eye gel', 'under eye', 'eye serum'],
    },
    {
        'step': 5,
        'name': 'Moisturiser',
        'icon': '🌿',
        'instruction': 'Apply an even layer over the face and neck. Use upward strokes. Lock in previous serum layers.',
        'time': 'both',
        'categories': ['skincare'],
        'keywords': ['moisturiser', 'moisturizer', 'cream', 'lotion', 'gel cream', 'hydrating cream', 'barrier'],
    },
    {
        'step': 6,
        'name': 'SPF / Sunscreen',
        'icon': '☀️',
        'instruction': 'Apply SPF 30–50+ as the absolute final step of your morning routine. Reapply every 2 hours when outdoors. This step is mandatory — UV is the #1 cause of premature skin ageing.',
        'time': 'am',
        'categories': ['skincare', 'makeup'],
        'keywords': ['spf', 'sunscreen', 'sun protection', 'uv', 'pa+++'],
    },
    {
        'step': 7,
        'name': 'Overnight Treatment',
        'icon': '🌙',
        'instruction': 'Apply a generous layer as the last step of your evening routine. Sleep masks and overnight treatments work while your skin repairs itself.',
        'time': 'pm',
        'categories': ['skincare'],
        'keywords': ['overnight', 'night cream', 'sleeping mask', 'night repair', 'recovery'],
    },
    {
        'step': 8,
        'name': 'Facial Oil',
        'icon': '✨',
        'instruction': 'Press 2–3 drops between palms and gently press into skin as the last step (oils seal in moisture). Use PM or as needed.',
        'time': 'pm',
        'categories': ['skincare'],
        'keywords': ['facial oil', 'face oil', 'rosehip', 'jojoba', 'oil serum'],
    },
]

# ── Concern → keyword priority mapping ───────────────────────────────────────
CONCERN_KEYWORD_MAP = {
    'acne': ['niacinamide', 'salicylic', 'bha', 'tea tree', 'acne', 'pore', 'oil control', 'balancing'],
    'brightening': ['vitamin c', 'niacinamide', 'kojic', 'brightening', 'radiance', 'glow', 'dark spot'],
    'hydration': ['hyaluronic', 'ceramide', 'hydrating', 'moisture', 'water', 'plumping'],
    'anti-aging': ['retinol', 'peptide', 'collagen', 'firming', 'anti-age', 'wrinkle'],
    'redness': ['centella', 'cica', 'aloe', 'soothing', 'calming', 'sensitive', 'redness'],
    'dark spots': ['vitamin c', 'kojic', 'arbutin', 'brightening', 'dark spot', 'pigmentation'],
    'pores': ['niacinamide', 'salicylic', 'bha', 'pore', 'oil control'],
    'dryness': ['ceramide', 'hyaluronic', 'shea', 'barrier', 'moisturising', 'rich cream'],
    'general': [],  # no concern keyword filtering
}

# ── Skin type → product attribute preference ─────────────────────────────────
SKIN_TYPE_PREFERENCE = {
    'oily': ['oil control', 'gel', 'lightweight', 'non-comedogenic', 'balancing', 'water-based'],
    'dry': ['rich', 'cream', 'barrier', 'ceramide', 'shea', 'deeply moisturising', 'nourishing'],
    'combination': ['balancing', 'lightweight', 'hydrating', 'gel-cream'],
    'sensitive': ['soothing', 'calming', 'fragrance-free', 'gentle', 'cica', 'centella'],
    'normal': ['hydrating', 'balanced'],
    'all': [],
}


class RoutineBuilder:
    """
    Builds a personalised AM + PM skincare routine using real products from SQLite.
    """

    def __init__(self, skin_type: str, concern: str, budget_max: Optional[float] = None):
        self.skin_type = (skin_type or 'all').strip().lower()
        self.concern = (concern or 'general').strip().lower()
        self.budget_max = budget_max

    def build(self) -> Dict[str, Any]:
        """Generate the full morning and evening routine."""
        am_routine = self._build_routine_steps('am')
        pm_routine = self._build_routine_steps('pm')

        # Deduplicate: if same product appears in both AM and PM for same step type, keep it
        total_products = set()
        for step in am_routine + pm_routine:
            if step.get('product'):
                total_products.add(step['product']['id'])

        concern_label = self.concern.replace('-', ' ').title()
        skin_label = self.skin_type.replace('-', ' ').title()

        return {
            'status': 'ok',
            'skin_type': self.skin_type,
            'skin_type_label': skin_label,
            'concern': self.concern,
            'concern_label': concern_label,
            'total_products_found': len(total_products),
            'morning_routine': am_routine,
            'evening_routine': pm_routine,
            'routine_tips': self._get_routine_tips(),
            'disclaimer': (
                'This routine is generated from our available product catalog and is for '
                'general guidance only. Always patch test new products. '
                'Consult a dermatologist for personalised medical advice.'
            ),
        }

    def _build_routine_steps(self, time_of_day: str) -> List[Dict]:
        """Build ordered routine steps for AM or PM."""
        result = []
        steps = [s for s in ROUTINE_STEPS if s['time'] in (time_of_day, 'both')]

        for step_def in steps:
            product = self._find_best_product(step_def)
            result.append({
                'step': step_def['step'],
                'step_name': step_def['name'],
                'icon': step_def['icon'],
                'instruction': step_def['instruction'],
                'product': ProductListSerializer(product).data if product else None,
                'product_found': product is not None,
                'fallback_tip': self._fallback_tip(step_def['name']) if not product else None,
            })
        return result

    def _find_best_product(self, step_def: Dict) -> Optional[Product]:
        """
        Locate the best matching product from SQLite for a given routine step.
        Matching priority:
        1. Category + step keyword + concern keyword + skin type
        2. Category + step keyword + concern keyword
        3. Category + step keyword + skin type
        4. Category + step keyword
        5. Any skincare product with step keyword
        """
        concern_keywords = CONCERN_KEYWORD_MAP.get(self.concern, [])
        skin_keywords = SKIN_TYPE_PREFERENCE.get(self.skin_type, [])
        step_keywords = step_def['keywords']
        categories = step_def['categories']

        from django.db.models import Q

        def build_keyword_filter(keywords: List[str]) -> Q:
            q = Q()
            for kw in keywords:
                q |= (
                    Q(name__icontains=kw) |
                    Q(description__icontains=kw) |
                    Q(concern_tags__icontains=kw) |
                    Q(key_ingredients__icontains=kw)
                )
            return q

        # Build step filter
        step_q = build_keyword_filter(step_keywords)
        cat_q = Q(category__in=categories)

        # Try progressively relaxed queries
        queries_to_try = []

        if concern_keywords and skin_keywords:
            queries_to_try.append(
                cat_q & step_q & build_keyword_filter(concern_keywords) & build_keyword_filter(skin_keywords[:2])
            )

        if concern_keywords:
            queries_to_try.append(cat_q & step_q & build_keyword_filter(concern_keywords))

        if skin_keywords:
            queries_to_try.append(cat_q & step_q & build_keyword_filter(skin_keywords[:2]))

        queries_to_try.append(cat_q & step_q)
        queries_to_try.append(step_q)

        for q in queries_to_try:
            qs = Product.objects.filter(q).filter(availability='in_stock')
            if self.budget_max:
                qs = qs.filter(price__lte=self.budget_max)
            # Prefer bestsellers first, then highest rating
            qs = qs.order_by('-is_bestseller', '-rating')
            product = qs.first()
            if product:
                return product

        return None

    def _get_routine_tips(self) -> List[str]:
        """Return skin-type-specific and concern-specific routine tips."""
        tips = [
            'Always apply products from thinnest to thickest consistency.',
            'Allow 60–90 seconds between steps for absorption.',
            'Never skip SPF in the morning — it prevents UV-induced premature ageing.',
            'Introduce new active ingredients gradually — one at a time — to identify reactions.',
        ]

        concern_tips = {
            'acne': 'Do not over-cleanse — twice daily is optimal. Over-washing strips the barrier and triggers more oil production.',
            'brightening': 'Vitamin C works best in the morning where it also provides antioxidant protection against pollution.',
            'hydration': 'Apply your hydrating serum to slightly damp skin to maximise absorption.',
            'anti-aging': 'Retinol is most effective at night. Start with 2–3 nights per week before daily use.',
            'redness': 'Use lukewarm water only — never hot — as heat exacerbates redness and sensitivity.',
            'dark spots': 'Consistency is key for brightening — allow 8–12 weeks of daily use before evaluating results.',
            'pores': 'BHA (Salicylic Acid) is oil-soluble and can penetrate pores to clear congestion from inside.',
            'dryness': 'Apply your moisturiser to slightly damp skin to lock in hydration from your toner/essence.',
        }
        if self.concern in concern_tips:
            tips.insert(0, concern_tips[self.concern])

        skin_tips = {
            'oily': 'Gel-based and water-based formulas are ideal — they hydrate without clogging pores or adding shine.',
            'dry': 'Consider a barrier-repairing cream with ceramides and hyaluronic acid as your final PM step.',
            'sensitive': 'Perform a 24-hour patch test behind your ear before introducing any new active ingredient.',
            'combination': 'Multi-masking — different products for different zones — can help target T-zone oiliness without drying out your cheeks.',
        }
        if self.skin_type in skin_tips:
            tips.append(skin_tips[self.skin_type])

        return tips

    @staticmethod
    def _fallback_tip(step_name: str) -> str:
        fallbacks = {
            'Cleanser': 'No specific cleanser matched your profile — try our Skincare catalog for gentle cleansers.',
            'Toner / Essence': 'A simple rose water or hydrating mist works well as a toner step.',
            'Active Serum': 'Browse our Skincare serums for targeted treatments matching your concern.',
            'Eye Cream': 'Gently applying your regular moisturiser around the eye area works as a substitute.',
            'Moisturiser': 'Browse our Skincare moisturisers to find one for your skin type.',
            'SPF / Sunscreen': 'SPF is non-negotiable — browse our catalog for broad-spectrum options.',
            'Overnight Treatment': 'A richer moisturiser applied generously can substitute an overnight mask.',
            'Facial Oil': 'A few drops of pure Jojoba or Rosehip oil work as a universal facial oil.',
        }
        return fallbacks.get(step_name, f'Browse our skincare catalog for a {step_name.lower()}.')
