from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from six import python_2_unicode_compatible

__all__ = (
    'Translation',
)


@python_2_unicode_compatible
class Translation(models.Model):
    """Translation item.

    ``original``, ``source_language`` and ``target_language`` fields are made
    unique in the migration ``0006_add_unique_index_md5_20180502_1638.py``.
    """

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
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta(object):
        """Meta options."""

        ordering = ["id"]
        # original, source_language and target_language are made unique
        # in the migration `0006_add_unique_index_md5_20180502_1638.py`.
        # unique_together = (
        #     (
        #         'original',
        #         'source_language',
        #         'target_language',
        #     ),
        # )

    def __str__(self):
        return self.original
