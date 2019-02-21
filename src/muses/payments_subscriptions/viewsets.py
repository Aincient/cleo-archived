import Mollie
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import ugettext

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)


from .models import Product, Order
from .serializers import (
    ProductSerializer,
    OrderSerializer,
)

__all__ = (
    'ProductViewSet',
    'OrderViewSet',
)


class ProductViewSet(ReadOnlyModelViewSet):
    """Product view set."""

    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()

    def get_queryset(self):
        """"""
        return Product.objects.all()


class OrderViewSet(ModelViewSet):
    """Order view set."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all()

    def get_queryset(self):
        """"""
        return Order.objects.filter(user=self.request.user)

    @list_route(methods=['POST'])
    def checkout(self, request, *args, **kwargs):
        """
        Create a new order, send order to mollie and redirect user to mollie
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_data = request.data.copy()
        request_data['user'] = request.user.id
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)

        order = Order(**serializer.validated_data)
        order.user = request.user
        order.amount = order.product.price
        order.save()

        mollie = Mollie.API.Client()
        mollie.setApiKey(settings.MOLLIE_API_KEY)

        description = order.product.description_nl \
            if order.product.description_nl \
            else ugettext("Payment for {}").format(order.product.title_nl)

        payment = mollie.payments.create({
            'amount': float(order.product.price),
            'description': description,
            'redirectUrl': '{0}/order/{1}/'.format(
                settings.SITE_DOMAIN, order.id),
            'webhookUrl': '{0}/mollie-webhook/'.format(settings.SITE_DOMAIN),
            'metadata': {
                'order_nr': str(order.id)
            },
        })
        order.status = payment['status']
        order.save()
        return JsonResponse({'redirect': payment.getPaymentUrl()})
