from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from six import python_2_unicode_compatible

__all__ = (
    'ThesauriTranslation',
)


@python_2_unicode_compatible
class ThesauriTranslation(models.Model):
    """Translation item."""

    original = models.TextField(
        verbose_name=_("Original"),
        # db_index=True
    )
    translation = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Translated")
    )
    source_language = models.CharField(
        max_length=255,
        verbose_name=_("Source language")
    )
    target_language = models.CharField(
        max_length=255,
        verbose_name=_("Target language")
    )
    translation_exists = models.BooleanField(
        default=False,
        verbose_name=_("Translation exists")
    )
    supervised = models.BooleanField(
        default=False,
        verbose_name=_("Translation is supervised")
    )
    disregard = models.BooleanField(
        default=False,
        verbose_name=_("Disregard the translation")
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta(object):
        """Meta options."""

        ordering = ["id"]
        unique_together = (
            (
                'original',
                'source_language',
                'target_language',
            ),
        )

    def __str__(self):
        return self.original
