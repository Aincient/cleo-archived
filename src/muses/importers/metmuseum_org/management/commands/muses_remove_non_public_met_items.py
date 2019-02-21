from __future__ import absolute_import, unicode_literals

import logging

from django.core.management.base import BaseCommand

from muses.collection.models import Item
from muses.importers.metmuseum_org.helpers import MetropolitanClient


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Remove non-public MET items.."""

    help = "Remove non-public MET items."

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('--dry-run',
                            action='store_true',
                            dest='dry_run',
                            default=False,
                            help="Dry-run (don't delete, only show which "
                                 "ones are going to be removed).")

    def handle(self, *args, **options):
        """Handle.

        :param args:
        :param options:
        :return:
        """
        dry_run = bool(options['dry_run'])
        client = MetropolitanClient()
        client.configure_from_settings()
        cached_items = client.load_objects_from_json_cache()
        public_domain = set([])
        non_public_domain = set([])
        for n, item in cached_items.items():
            if item['Is Public Domain'] == 'True':
                public_domain.add(item['Object ID'])
            else:
                non_public_domain.add(item['Object ID'])

        non_public_domain_items = Item.objects.filter(
            importer_uid='metmuseum_org',
            record_number__in=non_public_domain
        )
        if dry_run:
            LOGGER.info(
                "\n{} public domain items have been found in cache."
                "\n{} non-public domain items have been found in cache."
                "\n{} non-public domain items to be removed from database"
                "".format(
                    len(public_domain),
                    len(non_public_domain),
                    non_public_domain_items.count()
                )
            )
        else:
            non_public_domain_items.delete()
            LOGGER.info(
                "\n{} public domain items have been found in cache."
                "\n{} non-public domain items have been found in cache."
                "\n{} non-public domain items removed from database"
                "".format(
                    len(public_domain),
                    len(non_public_domain),
                    non_public_domain_items.count()
                )
            )
