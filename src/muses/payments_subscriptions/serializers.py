from rest_framework import serializers

from .models import Product, Order

__all__ = (
    'ProductSerializer',
    'OrderSerializer',
)


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer."""

    class Meta(object):
        """Meta options."""

        model = Product
        fields = (
            'url',
            'id',
            'code',
            'num_requests',
            'price',
            'title_en',
            'description_en',
            'title_nl',
            'description_nl',
        )
        # read_only_fields = fields[:]


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta(object):
        """Meta options."""

        model = Order
        fields = (
            'url',
            'id',
            'user',
            'product',
            'amount',
            'billing_email',
            'billing_first_name',
            'billing_last_name',
            'billing_address_1',
            'billing_address_2',
            'billing_city',
            'billing_postcode',
            'billing_country_code',
            'billing_country_area',
        )
        read_only_fields = (
            'status',
            'currency',
            'user',
        )
