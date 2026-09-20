"""
Ingredient Safety Checker for Joyory SmartMatch.

Deterministic, rule-based conflict detection using a curated
ingredient interaction database sourced from widely accepted
cosmetic chemistry references.

DISCLAIMER: This tool is for educational reference only and does
not constitute dermatological or medical advice.
"""

from typing import List, Dict, Any

# ── Curated Conflict Database ─────────────────────────────────────────────────
# Structure: ingredient_key -> list of (conflicting_ingredient, severity, reason)
# severity: 'high' | 'medium' | 'low'
CONFLICT_DB = {
    'vitamin c': [
        ('benzoyl peroxide', 'high',
         'Benzoyl peroxide oxidises Vitamin C (L-Ascorbic Acid), degrading it and '
         'rendering it ineffective. Use Vitamin C in the morning and Benzoyl Peroxide at night.'),
        ('retinol', 'medium',
         'Both are active ingredients that can cause irritation when combined, especially '
         'on sensitive skin. Use Vitamin C in the AM routine and Retinol in the PM routine.'),
        ('niacinamide', 'low',
         'Historically considered potentially irritating when combined (forms niacin), '
         'though modern research shows this is unlikely at normal skin-care concentrations. '
         'Low concern for most skin types; monitor for flushing.'),
        ('aha', 'medium',
         'Combining acidic Vitamin C with AHAs (Glycolic/Lactic Acid) can lower pH '
         'beyond the skin\'s tolerance and increase irritation risk. Alternate usage times.'),
        ('bha', 'medium',
         'Similar to AHAs — combining with BHA (Salicylic Acid) may cause excess irritation. '
         'Use at separate times of day.'),
    ],
    'retinol': [
        ('aha', 'high',
         'AHAs (Glycolic Acid, Lactic Acid) combined with Retinol significantly increases '
         'photosensitivity and irritation, including peeling and redness. Avoid same-session use.'),
        ('bha', 'high',
         'BHA (Salicylic Acid) with Retinol risks over-exfoliation, barrier damage, and '
         'significant irritation. Use on alternating nights if needed.'),
        ('benzoyl peroxide', 'high',
         'Benzoyl Peroxide can oxidise and inactivate Retinol, making both ingredients less '
         'effective. Separate AM/PM use.'),
        ('vitamin c', 'medium',
         'See Vitamin C + Retinol conflict above.'),
    ],
    'benzoyl peroxide': [
        ('vitamin c', 'high',
         'See Vitamin C + Benzoyl Peroxide conflict above.'),
        ('retinol', 'high',
         'See Retinol + Benzoyl Peroxide conflict above.'),
        ('hydroquinone', 'medium',
         'Combining these two can temporarily stain the skin brown/orange. Not harmful but '
         'aesthetically undesirable. Use separately.'),
    ],
    'aha': [
        ('retinol', 'high',
         'See Retinol + AHA conflict above.'),
        ('vitamin c', 'medium',
         'See Vitamin C + AHA conflict above.'),
        ('bha', 'low',
         'Mixing multiple exfoliating acids (AHA + BHA) simultaneously can cause over-exfoliation '
         'and barrier damage, especially for sensitive skin. Use with caution or on alternate days.'),
    ],
    'glycolic acid': [
        ('retinol', 'high',
         'Glycolic Acid (AHA) combined with Retinol significantly increases skin sensitivity. '
         'Use Retinol at night and Glycolic Acid on alternating nights.'),
        ('salicylic acid', 'low',
         'Combining two exfoliating acids simultaneously risks over-exfoliation for sensitive skin.'),
    ],
    'lactic acid': [
        ('retinol', 'high',
         'Lactic Acid (AHA) with Retinol increases irritation and sensitivity risk.'),
        ('vitamin c', 'medium',
         'Combined acidity may cause excessive irritation for sensitive skin types.'),
    ],
    'bha': [
        ('retinol', 'high',
         'See Retinol + BHA conflict above.'),
        ('vitamin c', 'medium',
         'See Vitamin C + BHA conflict above.'),
        ('aha', 'low',
         'See AHA + BHA conflict above.'),
    ],
    'salicylic acid': [
        ('retinol', 'high',
         'Salicylic Acid (BHA) combined with Retinol risks barrier disruption and significant '
         'peeling. Use on alternating nights with caution.'),
        ('glycolic acid', 'low',
         'Over-exfoliation risk with combined acids.'),
        ('niacinamide', 'low',
         'Generally well-tolerated together; however, niacinamide may slightly reduce the '
         'efficacy of Salicylic Acid if applied simultaneously. Consider layering separately.'),
    ],
    'niacinamide': [
        ('vitamin c', 'low',
         'See Vitamin C + Niacinamide conflict above.'),
        ('salicylic acid', 'low',
         'See Salicylic Acid + Niacinamide conflict above.'),
    ],
    'copper peptide': [
        ('vitamin c', 'medium',
         'Vitamin C can chelate copper peptides, reducing their effectiveness. '
         'Use Vitamin C in the AM and Copper Peptides in PM.'),
        ('aha', 'medium',
         'Acidic AHAs may degrade copper peptide complexes. Use separately.'),
        ('retinol', 'low',
         'Both are powerful actives; using together may increase irritation for sensitive skin. '
         'Introduce slowly and alternate if needed.'),
    ],
    'hydroquinone': [
        ('benzoyl peroxide', 'medium',
         'See Benzoyl Peroxide + Hydroquinone conflict above.'),
        ('aha', 'low',
         'Combined use can increase skin sensitivity and irritation. Monitor skin response.'),
    ],
    'tretinoin': [
        ('aha', 'high',
         'Tretinoin (prescription Retinoid) with AHAs dramatically increases skin irritation, '
         'dryness, and peeling. Avoid combining.'),
        ('bha', 'high',
         'Same as AHA — Tretinoin with BHA is a high-irritation risk combination.'),
        ('benzoyl peroxide', 'high',
         'Benzoyl Peroxide can inactivate Tretinoin. Use strictly on alternate routines.'),
        ('vitamin c', 'medium',
         'Tretinoin with Vitamin C can increase sensitivity, especially in early use. '
         'Use vitamin C AM and Tretinoin PM after skin acclimates.'),
    ],
    'kojic acid': [
        ('vitamin c', 'low',
         'Both are brightening agents and generally safe to combine; however, simultaneous '
         'use on very sensitive skin can cause irritation. Patch test recommended.'),
        ('aha', 'low',
         'Acidic environment may cause minor irritation when layered directly.'),
    ],
    'peptides': [
        ('aha', 'medium',
         'Acidic AHAs can degrade certain peptide complexes, reducing their effectiveness. '
         'Apply peptides after acids have been absorbed or at different routine steps.'),
        ('bha', 'medium',
         'Similar to AHAs — acids can interfere with peptide function.'),
    ],
    'spf': [
        ('retinol', 'low',
         'Retinol increases photosensitivity — always apply SPF in the morning when using '
         'Retinol. Not a conflict but a mandatory pairing for safety.'),
        ('aha', 'low',
         'AHAs increase photosensitivity — mandatory SPF use is required in the AM routine.'),
    ],
}

# ── Canonical name normalisations ─────────────────────────────────────────────
INGREDIENT_ALIASES = {
    'ascorbic acid': 'vitamin c',
    'l-ascorbic acid': 'vitamin c',
    'vit c': 'vitamin c',
    'vitamin-c': 'vitamin c',
    'retin-a': 'tretinoin',
    'retina': 'tretinoin',
    'retinoids': 'retinol',
    'retinoid': 'retinol',
    'glycolic': 'glycolic acid',
    'lactic': 'lactic acid',
    'salicylic': 'salicylic acid',
    'bha': 'salicylic acid',
    'aha': 'glycolic acid',
    'alpha hydroxy': 'aha',
    'beta hydroxy': 'bha',
    'sa': 'salicylic acid',
    'bp': 'benzoyl peroxide',
    'niacin': 'niacinamide',
    'niacinimide': 'niacinamide',
    'bpo': 'benzoyl peroxide',
    'copper': 'copper peptide',
    'kojic': 'kojic acid',
    'hq': 'hydroquinone',
}

SEVERITY_ORDER = {'high': 3, 'medium': 2, 'low': 1}
SEVERITY_LABELS = {
    'high': '⛔ High Risk',
    'medium': '⚠️ Moderate Caution',
    'low': '💡 Low Concern',
}
SEVERITY_COLORS = {
    'high': '#e53935',
    'medium': '#f57c00',
    'low': '#388e3c',
}


def _normalise(ingredient: str) -> str:
    """Lowercase, strip, and apply alias mapping."""
    clean = ingredient.lower().strip()
    return INGREDIENT_ALIASES.get(clean, clean)


def _get_canonical_keys(ingredient_norm: str) -> list:
    """Return all conflict DB keys that are contained in or contain the ingredient name."""
    matches = []
    for key in CONFLICT_DB:
        if key in ingredient_norm or ingredient_norm in key:
            matches.append(key)
    return matches


class IngredientChecker:
    """
    Accepts a list of ingredient names and returns a conflict analysis report.
    """

    def __init__(self, ingredients: List[str]):
        self.raw_ingredients = [i.strip() for i in ingredients if isinstance(i, str) and i.strip()]
        self.normalised = [_normalise(i) for i in self.raw_ingredients]

    def check(self) -> Dict[str, Any]:
        """Run conflict analysis and return structured result."""
        if not self.normalised:
            return {
                'status': 'error',
                'message': 'No valid ingredient names were provided.',
                'conflicts': [],
                'safe_pairs': [],
                'overall_safety': 'unknown',
                'total_ingredients_checked': 0,
            }

        conflicts = []
        seen_pairs = set()

        for i, ing_a in enumerate(self.normalised):
            keys_a = _get_canonical_keys(ing_a)
            for key_a in keys_a:
                conflict_list = CONFLICT_DB.get(key_a, [])
                for conflict_key, severity, reason in conflict_list:
                    # Check if conflict_key matches any other provided ingredient
                    for j, ing_b in enumerate(self.normalised):
                        if i == j:
                            continue
                        if conflict_key in ing_b or ing_b in conflict_key:
                            pair = tuple(sorted([self.raw_ingredients[i], self.raw_ingredients[j]]))
                            if pair not in seen_pairs:
                                seen_pairs.add(pair)
                                conflicts.append({
                                    'ingredient_a': self.raw_ingredients[i],
                                    'ingredient_b': self.raw_ingredients[j],
                                    'severity': severity,
                                    'severity_label': SEVERITY_LABELS[severity],
                                    'severity_color': SEVERITY_COLORS[severity],
                                    'reason': reason,
                                    'recommendation': self._get_recommendation(severity),
                                })

        # Sort conflicts by severity descending
        conflicts.sort(key=lambda c: SEVERITY_ORDER.get(c['severity'], 0), reverse=True)

        # Determine overall safety rating
        if any(c['severity'] == 'high' for c in conflicts):
            overall = 'unsafe'
            overall_label = '⛔ Unsafe Combination — High risk conflicts detected'
            overall_color = '#e53935'
        elif any(c['severity'] == 'medium' for c in conflicts):
            overall = 'caution'
            overall_label = '⚠️ Use With Caution — Moderate interaction risk'
            overall_color = '#f57c00'
        elif conflicts:
            overall = 'low_risk'
            overall_label = '💡 Generally Safe — Minor concerns noted'
            overall_color = '#388e3c'
        else:
            overall = 'safe'
            overall_label = '✅ No Known Conflicts — Safe to combine'
            overall_color = '#2e7d32'

        # Build safe pairs list (all ingredient pairs with no detected conflict)
        all_pairs = []
        for i in range(len(self.raw_ingredients)):
            for j in range(i + 1, len(self.raw_ingredients)):
                pair = tuple(sorted([self.raw_ingredients[i], self.raw_ingredients[j]]))
                if pair not in seen_pairs:
                    all_pairs.append({
                        'ingredient_a': self.raw_ingredients[i],
                        'ingredient_b': self.raw_ingredients[j],
                    })

        return {
            'status': 'ok',
            'total_ingredients_checked': len(self.normalised),
            'ingredients_analysed': self.raw_ingredients,
            'overall_safety': overall,
            'overall_label': overall_label,
            'overall_color': overall_color,
            'total_conflicts': len(conflicts),
            'conflicts': conflicts,
            'safe_pairs': all_pairs,
            'disclaimer': (
                'This tool provides educational guidance based on commonly cited cosmetic chemistry '
                'references. It does not constitute medical or dermatological advice. Always consult '
                'a qualified professional for personalised skincare recommendations.'
            ),
        }

    @staticmethod
    def _get_recommendation(severity: str) -> str:
        if severity == 'high':
            return 'Do not use together. Apply in separate AM/PM routines.'
        elif severity == 'medium':
            return 'Use with caution. Consider alternating days or separate routine steps.'
        else:
            return 'Generally manageable. Monitor skin response; patch test if sensitive.'
