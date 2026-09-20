from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer


@api_view(['GET'])
def health_check(request):
    """
    Simple health-check endpoint.
    Returns OK status and project name to verify the backend is running
    and the frontend can communicate with it.
    """
    return Response({
        'status': 'ok',
        'project': 'Joyory SmartMatch',
        'message': 'Backend is running successfully!',
    })


@api_view(['GET'])
def product_list(request):
    """
    Return all products.
    Used by the frontend to verify the full DRF + ORM pipeline.
    """
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
