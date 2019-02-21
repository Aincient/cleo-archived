from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from ..models.translation_fix import TranslationFix


__all__ = ('TranslationFixAdmin',)


@admin.register(TranslationFix)
class TranslationFixAdmin(admin.ModelAdmin):
    """Translation fix admin."""

    list_display = (
        'id',
        'original',
        'replacement',
        'field',
        'language',
        'exact_match',
        'created',
        'updated',
    )
    list_filter = (
        'field',
        'language',
    )
    search_fields = (
        'original',
        'replacement',
        'id',
    )
