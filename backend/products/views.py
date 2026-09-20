from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer, ProductListSerializer


@api_view(['GET'])
def product_list(request):
    """
    List products with optional filtering and search.

    Query parameters:
      - category   : filter by category (e.g. ?category=skincare)
      - skin_type  : filter by skin type (e.g. ?skin_type=oily)
      - min_price  : minimum price (inclusive)
      - max_price  : maximum price (inclusive)
      - search     : free-text search across name, brand, description, ingredients
      - concern    : filter by concern tag (substring match)
      - bestseller : if "true", only bestsellers
      - new        : if "true", only new arrivals
      - ordering   : sort field (price, -price, rating, -rating, name, -name)
    """
    queryset = Product.objects.all()

    # ── Category filter ──────────────────────────────────────────
    category = request.query_params.get('category')
    if category:
        queryset = queryset.filter(category__iexact=category)

    # ── Skin-type filter ─────────────────────────────────────────
    skin_type = request.query_params.get('skin_type')
    if skin_type:
        queryset = queryset.filter(
            Q(skin_type__iexact=skin_type) | Q(skin_type='all')
        )

    # ── Price range ──────────────────────────────────────────────
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    if min_price:
        try:
            queryset = queryset.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            return Response(
                {'error': 'min_price must be a valid number.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    if max_price:
        try:
            queryset = queryset.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            return Response(
                {'error': 'max_price must be a valid number.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # ── Free-text search ─────────────────────────────────────────
    search = request.query_params.get('search', '').strip()
    if search:
        # Normalize category synonyms e.g. "body care" -> "bodycare", "skin care" -> "skincare", "hair care" -> "haircare"
        normalized_search = (
            search.lower()
            .replace('body care', 'bodycare')
            .replace('skin care', 'skincare')
            .replace('hair care', 'haircare')
            .replace('nail care', 'nailcare')
        )

        words = [w for w in search.split() if len(w) >= 2]
        norm_words = [w for w in normalized_search.split() if len(w) >= 2]
        all_terms = list(dict.fromkeys([search, normalized_search] + words + norm_words))

        search_filter = Q()
        for term in all_terms:
            search_filter |= (
                Q(name__icontains=term)
                | Q(brand__icontains=term)
                | Q(category__icontains=term)
                | Q(description__icontains=term)
                | Q(key_ingredients__icontains=term)
                | Q(full_ingredients__icontains=term)
                | Q(concern_tags__icontains=term)
                | Q(skin_type__icontains=term)
            )
        queryset = queryset.filter(search_filter)

    # ── Concern-tag filter ───────────────────────────────────────
    concern = request.query_params.get('concern')
    if concern:
        queryset = queryset.filter(concern_tags__icontains=concern)

    # ── Boolean flags ────────────────────────────────────────────
    if request.query_params.get('bestseller', '').lower() == 'true':
        queryset = queryset.filter(is_bestseller=True)
    if request.query_params.get('new', '').lower() == 'true':
        queryset = queryset.filter(is_new_arrival=True)

    # ── Ordering ─────────────────────────────────────────────────
    ALLOWED_ORDERING = {'price', '-price', 'rating', '-rating', 'name', '-name'}
    ordering = request.query_params.get('ordering')
    if ordering and ordering in ALLOWED_ORDERING:
        queryset = queryset.order_by(ordering)

    serializer = ProductListSerializer(queryset, many=True)
    return Response({
        'count': queryset.count(),
        'results': serializer.data,
    })


@api_view(['GET'])
def product_detail(request, pk):
    """
    Retrieve a single product by primary key (ID).
    Returns a 404-style JSON error if the product does not exist.
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(
            {'error': f'Product with id {pk} not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(['GET'])
def category_list(request):
    """
    Return all available categories with product counts.
    Useful for building frontend filter dropdowns.
    """
    categories = (
        Product.objects
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )
    result = []
    for cat in categories:
        label = dict(Product.CATEGORY_CHOICES).get(cat, cat)
        count = Product.objects.filter(category=cat).count()
        result.append({'value': cat, 'label': label, 'count': count})

    return Response(result)


@api_view(['POST'])
def recommend_products(request):
    """
    POST endpoint for personalized product discovery quiz.
    Uses strict rule-based scoring matching against SQLite catalog.
    
    Expected JSON payload:
      - category (optional, string)
      - skin_type (optional, string)
      - concern (optional, string)
      - preference (optional, string)
      - budget_max (optional, number)
      - preferred_ingredients (optional, list of strings)
    """
    data = request.data
    if not isinstance(data, dict):
        return Response(
            {'error': 'Invalid request body. Expected JSON object with quiz answers.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate budget if present
    budget_raw = data.get('budget_max')
    if budget_raw is not None and budget_raw != '':
        try:
            budget_val = float(budget_raw)
            if budget_val < 0:
                return Response(
                    {'error': 'budget_max cannot be negative.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'budget_max must be a valid number.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    from .services.recommender import RuleBasedRecommender
    recommender = RuleBasedRecommender(data)
    result = recommender.get_recommendations()

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
def faq_query(request):
    """
    POST endpoint for the Product FAQ Assistant.
    Resolves customer questions using SQLite product attributes & verified FAQ base.

    Expected JSON payload:
      - question: string (required)
      - product_id: integer (optional, active PDP context)
      - context_product_id: integer (optional, previous conversational turn context)
    """
    data = request.data
    if not isinstance(data, dict):
        return Response(
            {'error': 'Invalid request body. Expected JSON object with a question string.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    question = data.get('question', '')
    if not isinstance(question, str) or not question.strip():
        return Response(
            {'error': 'The question field is required and must be a non-empty string.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product_id = data.get('product_id')
    if product_id is not None:
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            product_id = None

    context_product_id = data.get('context_product_id')
    if context_product_id is not None:
        try:
            context_product_id = int(context_product_id)
        except (ValueError, TypeError):
            context_product_id = None

    from .services.faq_assistant import ProductFaqAssistant
    assistant = ProductFaqAssistant(
        question=question,
        product_id=product_id,
        context_product_id=context_product_id
    )
    response_data = assistant.answer_query()

    return Response(response_data, status=status.HTTP_200_OK)

