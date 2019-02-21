from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Order, Product


__all__ = (
    'ProductAdmin',
    'OrderAdmin',
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Item admin."""

    list_display = (
        'id',
        'code',
        'num_requests',
        'price',
        'title_en',
        'description_en',
        'title_nl',
        'description_nl',
        'created',
        'modified',
    )
    search_fields = (
        'id',
        'code',
        'title_en',
        'description_en',
    )
    readonly_fields = (
        'created',
        'modified',
    )

    fieldsets = (
        (None, {
            'fields': (
                'code',
                'num_requests',
                'price',
            )
        }),
        (_('English'), {
            'classes': ('collapse',),
            'fields': (
                'title_en',
                'description_en',
            ),
        }),
        (_('Dutch'), {
            'classes': ('collapse',),
            'fields': (
                'title_nl',
                'description_nl',
            ),
        }),
        (_('Dates'), {
            'classes': ('collapse',),
            'fields': (
                'created',
                'modified',
            )
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Item admin."""

    list_display = (
        'id',
        'user',
        'product',
        'status',
        'amount',
        'created',
        'modified',
        'billing_email',
        'billing_first_name',
        'billing_last_name',
    )
    list_filter = (
        'status',
    )
    search_fields = (
        'id',
        'user__email',
        'billing_email',
        'billing_first_name',
        'billing_last_name',
    )
    readonly_fields = (
        'created',
        'modified',
    )
