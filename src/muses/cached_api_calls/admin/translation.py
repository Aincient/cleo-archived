from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from ..models.translation import Translation


__all__ = ('TranslationAdmin',)


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    """Translation admin."""

    list_display = (
        'id',
        'original',
        'source_language',
        'translation',
        'target_language',
        'created',
        'updated',
    )
    list_filter = (
        'source_language',
        'target_language',
    )
    search_fields = (
        'original',
        'translation',
    )
