from __future__ import absolute_import, unicode_literals

import importlib
import logging

from django.db.models import Q
from django.core.management.base import BaseCommand

from muses.collection.helpers import clean_met_images
from muses.collection.models import Image as ItemImage

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Download images."""

    help = "Crop MET images."

    requires_system_checks = False

    def add_arguments(self, parser):
        # parser.add_argument('--cache-results',
        #                     action='store_true',
        #                     dest='cache_results',
        #                     default=True,
        #                     help="Store results in cache.")

        parser.add_argument('--re-crop-existing',
                            action='store_true',
                            dest='re_crop_existing',
                            default=False,
                            help="Re-crop existing active images.")

    def handle(self, *args, **options):
        """Handle.

        :param args:
        :param options:
        :return:
        """

        recrop = bool(options['re_crop_existing'])
        queryset = ItemImage.objects.exclude(
            Q(image__isnull=True) | Q(image__exact=''),
        ).filter(
            Q(api_url__contains='https://images.metmuseum.org')
        )
        if not recrop:
            queryset = queryset.exclude(
                Q(trimmed=True)
            )

        counter = clean_met_images(
            queryset=queryset
        )
        LOGGER.info("{} images cleaned".format(counter))
