from __future__ import absolute_import, unicode_literals

import logging

from django.db.models import Q
from django.core.management.base import BaseCommand

from muses.collection.models import Item

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Fill the missing `api_url` fields."""

    help = "Fill the missing `api_url` fields."

    requires_system_checks = False

    def handle(self, *args, **options):
        """Handle.

        :param args:
        :param options:
        :return:
        """
        items = Item \
            .objects \
            .filter(importer_uid='brooklynmuseum_org') \
            .filter(Q(api_url__isnull=True) | Q(api_url=''))

        for item in items:
            item.api_url = 'https://www.brooklynmuseum.org/' \
                           'opencollection/objects/' \
                           '{}'.format(item.record_number)
            item.save()
