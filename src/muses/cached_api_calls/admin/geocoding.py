from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from ..models.geocoding import GeoCoding


__all__ = ('GeoCodingAdmin',)


@admin.register(GeoCoding)
class GeoCodingAdmin(admin.ModelAdmin):
    """GeoCoding admin."""

    list_display = (
        'id',
        'name',
        'raw_response',
        'geo_location',
        'created',
        'updated',
    )
    search_fields = (
        'name',
        'raw_response',
    )
