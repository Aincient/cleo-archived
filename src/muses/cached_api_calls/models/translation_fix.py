from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from six import python_2_unicode_compatible

__all__ = (
    'TranslationFix',
)

FIELD_CHOICES = (
    ('all', 'all'),
    ('city', 'city'),
    ('country', 'country'),
    ('title', 'title'),
    ('description', 'description'),
)

LANGUAGE_CHOICES = (
    ('en', 'English'),
    ('nl', 'Nederlands'),
)


@python_2_unicode_compatible
class TranslationFix(models.Model):
    """Correction for wrong translations."""

    original = models.TextField(
        verbose_name=_("Original (wrong) translation"),
        # db_index=True
    )
    replacement = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Fixed translation")
    )
    field = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        verbose_name=_("The field in which the faulty translation occurs"),
        choices=FIELD_CHOICES,
        default='all',
    )
    language = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        verbose_name=_("Language of the wrong translation"),
        choices=LANGUAGE_CHOICES,
        default='English'
    )
    exact_match = models.BooleanField(
        default=False,
        verbose_name=_("Match should be exact")
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta(object):
        """Meta options."""

        ordering = ["id"]
        unique_together = (
            (
                'original',
                'field',
                'language',
            ),
        )
        verbose_name_plural = "translation fixes"

    def field_name(self):
        return '{}_{}'.format(self.field, self.language)

    def __str__(self):
        return self.original
