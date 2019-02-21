import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import PAYMENT_STATUS_CHOICES, DEFAULT_PAYMENT_STATUS

__all__ = (
    'Product',
    'Order',
)


class Product(models.Model):
    """Product."""

    code = models.CharField(
        _("Code"),
        max_length=20,
        help_text=_(
            "Codes must be unique. Allows identifying the subscription."
        ),
        unique=True
    )
    num_requests = models.IntegerField(
        _("Number of requests")
    )
    price = models.DecimalField(
        _('Price'),
        max_digits=10,
        decimal_places=2,
    )

    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    # ************************ Translated fields **************************
    # English
    title_en = models.CharField(
        _("Title (EN)"),
        max_length=200
    )
    description_en = models.TextField(
        _("Description (EN)"),
        null=True,
        blank=True
    )

    # Dutch
    title_nl = models.CharField(
        _("Title (NL)"),
        max_length=200
    )
    description_nl = models.TextField(
        _("Description (NL)"),
        null=True,
        blank=True
    )
    # ************************ /Translated fields **************************

    class Meta(object):

        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.title_en


class Order(models.Model):
    """Order."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="user_orders",
        verbose_name=_("User"),
    )
    product = models.ForeignKey(
        'payments_subscriptions.Product',
        on_delete=models.PROTECT,
        related_name="user_products",
        verbose_name=_("Product")
    )
    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default=DEFAULT_PAYMENT_STATUS,
        verbose_name=_("Status")
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2,
    )

    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    currency = models.CharField(max_length=10)
    billing_first_name = models.CharField(max_length=256, blank=True)
    billing_last_name = models.CharField(max_length=256, blank=True)
    billing_address_1 = models.CharField(max_length=256, blank=True)
    billing_address_2 = models.CharField(max_length=256, blank=True)
    billing_city = models.CharField(max_length=256, blank=True)
    billing_postcode = models.CharField(max_length=256, blank=True)
    billing_country_code = models.CharField(max_length=2, blank=True)
    billing_country_area = models.CharField(max_length=256, blank=True)
    billing_email = models.EmailField(blank=True)

    class Meta(object):

        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return str(self.id)
