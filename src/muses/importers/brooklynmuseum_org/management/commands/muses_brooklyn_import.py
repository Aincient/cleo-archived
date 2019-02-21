from __future__ import absolute_import, unicode_literals

import logging

from django.core.management.base import BaseCommand

from ...helpers import BrooklynClient

LOGGER = logging.getLogger(__name__)

ACTION_OBJECTS = 'objects'
ACTION_IMAGES = 'images'
ACTION_GEO_LOCATIONS = 'locations'
DEFAULT_ACTION = ACTION_OBJECTS
ACTIONS = (
    ACTION_OBJECTS,
    ACTION_IMAGES,
    ACTION_GEO_LOCATIONS,
)


class Command(BaseCommand):
    """Import data from booklynmuseum.org."""

    help = "Translate."

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('--action',
                            type=str,
                            dest='action',
                            help="Action to perform. Choose between: "
                                 "objects, images, locations.")
        parser.add_argument('--offset',
                            type=int,
                            dest='offset',
                            default=0,
                            help="Initial offset value.")
        parser.add_argument('--cache-results',
                            action='store_true',
                            dest='cache_results',
                            default=True,
                            help="Store results in cache.")

        parser.add_argument('--update-existing',
                            action='store_true',
                            dest='update_existing',
                            default=False,
                            help="Update existing translations.")

    def handle(self, *args, **options):
        """Handle.

        :param args:
        :param options:
        :return:
        """
        action = str(options['action'])
        offset = int(options['offset'])

        if action not in ACTIONS:
            print("No action specified.")

        client = BrooklynClient()
        client.configure_from_settings()

        res = None

        if action == ACTION_OBJECTS:
            res = client.get_object_list(offset=offset)

        elif action == ACTION_IMAGES:
            res = client.get_object_list_images_from_json_cache()

        elif action == ACTION_GEO_LOCATIONS:
            res = client.get_geographical_location_list()

        print(res)
