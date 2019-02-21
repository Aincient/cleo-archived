from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    ProductViewSet,
    OrderViewSet,
)


router = DefaultRouter()

orders = router.register(
    r'orders',
    OrderViewSet,
    base_name='order'
)

products = router.register(
    r'products',
    ProductViewSet,
    base_name='product'
)


urlpatterns = [
    url(r'^', include(router.urls)),
]
