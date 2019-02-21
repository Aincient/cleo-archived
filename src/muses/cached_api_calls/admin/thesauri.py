from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from ..models.thesauri import ThesauriTranslation


__all__ = ('ThesauriAdmin',)


@admin.register(ThesauriTranslation)
class ThesauriAdmin(admin.ModelAdmin):
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
        'supervised',
    )
    search_fields = (
        'original',
        'translation',
    )
