"""
Review Insight Analyzer for Joyory SmartMatch.

HONEST DATA AUDIT (recorded 2026-09-20):
=========================================
The SQLite database contains NO separate Review model and NO review text.
Each Product record has:
  - rating       : Decimal  (0.00 – 5.00, set at product creation)
  - review_count : Integer  (number of customer reviews received)

What this analyzer DOES:
  - Rating distribution across the catalog (★ band breakdown)
  - Per-category average rating & total review volume
  - Top-rated & most-reviewed product identification
  - Rating confidence tiers (fewer reviews = lower confidence)
  - Honest "no review text" disclosure

What this analyzer CANNOT do (and will not claim to do):
  - Sentiment analysis (no text to analyze)
  - Theme extraction (no text)
  - NPS or CSAT scoring (no response data)
  - Trend over time (no timestamps on reviews)

To enable full text analysis in the future, add a Review model with:
  product (ForeignKey), author, rating, body (TextField), created_at
"""

from typing import Dict, Any, List
from decimal import Decimal

try:
    from products.models import Product
except ImportError:
    Product = None  # allow import outside Django context for unit tests


# ── Rating band definitions ───────────────────────────────────────────────────
RATING_BANDS = [
    {'label': '★★★★★  Excellent (4.5 – 5.0)', 'min': 4.5, 'max': 5.01, 'emoji': '🌟'},
    {'label': '★★★★☆  Very Good (4.0 – 4.4)', 'min': 4.0, 'max': 4.5,  'emoji': '✨'},
    {'label': '★★★☆☆  Good     (3.0 – 3.9)', 'min': 3.0, 'max': 4.0,  'emoji': '👍'},
    {'label': '★★☆☆☆  Fair     (2.0 – 2.9)', 'min': 2.0, 'max': 3.0,  'emoji': '🤔'},
    {'label': '★☆☆☆☆  Poor     (0.0 – 1.9)', 'min': 0.0, 'max': 2.0,  'emoji': '⚠️'},
]

# Review count confidence thresholds
CONFIDENCE_TIERS = [
    {'min': 300, 'label': 'High Confidence', 'color': '#2e7d32'},
    {'min': 100, 'label': 'Moderate Confidence', 'color': '#f57c00'},
    {'min': 1,   'label': 'Low Confidence',      'color': '#e53935'},
    {'min': 0,   'label': 'No Reviews',           'color': '#9e9e9e'},
]


def _confidence(count: int) -> Dict[str, str]:
    for tier in CONFIDENCE_TIERS:
        if count >= tier['min']:
            return {'label': tier['label'], 'color': tier['color']}
    return {'label': 'No Reviews', 'color': '#9e9e9e'}


def _safe_float(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


class ReviewInsightAnalyzer:
    """
    Generates catalog-level rating insights using only verified fields
    from the Product model (rating, review_count).

    No synthetic data. No hallucinated review text. No fabricated themes.
    """

    def analyze(self) -> Dict[str, Any]:
        if Product is None:
            return {'status': 'error', 'message': 'Django not configured.'}

        products = list(Product.objects.all().order_by('-rating', '-review_count'))

        if not products:
            return {
                'status': 'no_products',
                'message': 'No products found in the catalog.',
                'data_available': False,
            }

        total_products = len(products)
        total_reviews = sum(p.review_count for p in products)
        ratings = [_safe_float(p.rating) for p in products]
        avg_catalog_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

        return {
            'status': 'ok',
            'data_available': True,
            'data_disclaimer': (
                'This analysis is based on aggregate rating scores and review counts '
                'stored per product. No individual review text is stored in the '
                'database. Sentiment analysis and theme extraction are not possible '
                'without review body text.'
            ),
            'what_is_missing': (
                'To enable full review text analysis in future, add a Review model '
                'with fields: product (FK), author, rating (1-5), body (TextField), '
                'created_at (DateTimeField).'
            ),
            'catalog_summary': self._catalog_summary(products, total_products, total_reviews, avg_catalog_rating),
            'rating_distribution': self._rating_distribution(products, total_products),
            'category_breakdown': self._category_breakdown(products),
            'top_products': self._top_products(products),
            'confidence_breakdown': self._confidence_breakdown(products, total_products),
        }

    def _catalog_summary(self, products, total_products, total_reviews, avg_rating) -> Dict:
        high_rated = sum(1 for p in products if _safe_float(p.rating) >= 4.5)
        low_rated  = sum(1 for p in products if _safe_float(p.rating) < 3.0)
        return {
            'total_products_analyzed': total_products,
            'total_review_count': total_reviews,
            'average_catalog_rating': avg_rating,
            'products_rated_4_5_plus': high_rated,
            'products_rated_below_3': low_rated,
            'highest_rated': max((_safe_float(p.rating) for p in products), default=0),
            'lowest_rated': min((_safe_float(p.rating) for p in products), default=0),
            'most_reviewed_count': max((p.review_count for p in products), default=0),
        }

    def _rating_distribution(self, products, total) -> List[Dict]:
        result = []
        for band in RATING_BANDS:
            matched = [p for p in products if band['min'] <= _safe_float(p.rating) < band['max']]
            pct = round(len(matched) / total * 100) if total else 0
            result.append({
                'band': band['label'],
                'emoji': band['emoji'],
                'count': len(matched),
                'percentage': pct,
                'products': [{'id': p.id, 'name': p.name, 'rating': float(p.rating), 'review_count': p.review_count} for p in matched],
            })
        return result

    def _category_breakdown(self, products) -> List[Dict]:
        cats: Dict[str, List] = {}
        for p in products:
            cats.setdefault(p.category, []).append(p)

        result = []
        for cat, prods in sorted(cats.items()):
            ratings = [_safe_float(p.rating) for p in prods]
            total_rev = sum(p.review_count for p in prods)
            avg = round(sum(ratings) / len(ratings), 2) if ratings else 0.0
            best = max(prods, key=lambda p: _safe_float(p.rating))
            result.append({
                'category': cat,
                'product_count': len(prods),
                'average_rating': avg,
                'total_reviews': total_rev,
                'best_rated_product': {'id': best.id, 'name': best.name, 'rating': float(best.rating)},
                'confidence': _confidence(total_rev),
            })
        return sorted(result, key=lambda x: x['average_rating'], reverse=True)

    def _top_products(self, products) -> Dict:
        top_rated = sorted(products, key=lambda p: (_safe_float(p.rating), p.review_count), reverse=True)[:3]
        most_reviewed = sorted(products, key=lambda p: p.review_count, reverse=True)[:3]
        highest_value = sorted(
            products,
            key=lambda p: (_safe_float(p.rating) * 100 / float(p.price)) if float(p.price) > 0 else 0,
            reverse=True
        )[:3]
        return {
            'top_rated': [
                {'id': p.id, 'name': p.name, 'brand': p.brand, 'rating': float(p.rating),
                 'review_count': p.review_count, 'category': p.category, 'confidence': _confidence(p.review_count)}
                for p in top_rated
            ],
            'most_reviewed': [
                {'id': p.id, 'name': p.name, 'brand': p.brand, 'rating': float(p.rating),
                 'review_count': p.review_count, 'category': p.category, 'confidence': _confidence(p.review_count)}
                for p in most_reviewed
            ],
            'best_value': [
                {'id': p.id, 'name': p.name, 'brand': p.brand, 'rating': float(p.rating),
                 'review_count': p.review_count, 'price': float(p.price),
                 'discounted_price': float(p.discounted_price), 'category': p.category,
                 'confidence': _confidence(p.review_count)}
                for p in highest_value
            ],
        }

    def _confidence_breakdown(self, products, total) -> List[Dict]:
        result = []
        for tier in CONFIDENCE_TIERS:
            if tier['min'] == 0:
                matched = [p for p in products if p.review_count == 0]
            else:
                next_threshold = CONFIDENCE_TIERS[CONFIDENCE_TIERS.index(tier) - 1]['min'] if CONFIDENCE_TIERS.index(tier) > 0 else 99999
                matched = [p for p in products if tier['min'] <= p.review_count < next_threshold]
            pct = round(len(matched) / total * 100) if total else 0
            result.append({
                'tier': tier['label'],
                'color': tier['color'],
                'count': len(matched),
                'percentage': pct,
                'threshold': f"{tier['min']}+ reviews" if tier['min'] > 0 else "0 reviews",
            })
        return result
