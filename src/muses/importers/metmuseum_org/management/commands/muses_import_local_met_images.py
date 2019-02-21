from __future__ import absolute_import, unicode_literals

import os
import logging
import shutil

from django.db import IntegrityError
from django.conf import settings
from django.core.management.base import BaseCommand

from muses.collection.models import Item, Image as ItemImage

from muses.importers.metmuseum_org.helpers import MetropolitanClient

LOGGER = logging.getLogger(__name__)


def get_media_path(path):
    """Get media path to be used as `image.name`.

    :param path:
    :return:
    """
    _path = path.replace(settings.MEDIA_ROOT, '')
    if _path.startswith('/'):
        _path = _path[1:]
    return _path


class Command(BaseCommand):
    """Import local MET images."""

    help = "Import local MET images."

    requires_system_checks = False

    def handle(self, *args, **options):
        """Handle.

        :param args:
        :param options:
        :return:
        """
        client = MetropolitanClient()
        client.configure_from_settings()

        images_json = client.load_object_images_from_json_cache()

        # Name of the directory to which the images are stored.
        import_dir = os.path.join(
            settings.MEDIA_ROOT,
            'import',
            'metmuseum_org'
        )

        counter = 0

        for item_id, item_images_data in images_json.items():
            for item_image_data in item_images_data:
                if 'local_filename' not in item_image_data:
                    continue

                item_image = ItemImage.objects.filter(
                    api_url=item_image_data['originalImageUrl'],
                    # item__record_number=item_id,
                    item__importer_uid='metmuseum_org'
                ).first()

                if not item_image:
                    try:
                        item_image = ItemImage.objects.create(
                            api_url=item_image_data['originalImageUrl']
                        )
                    except IntegrityError as err:
                        item_image = ItemImage.objects.filter(
                            api_url=item_image_data['originalImageUrl']
                        ).first()

                    item = Item.objects.get(
                        record_number=item_id,
                        importer_uid='metmuseum_org'
                    )
                    item.images.add(item_image)

                source_file = os.path.join(
                    import_dir,
                    os.path.basename(item_image_data['local_filename'])
                )
                dest_filename = os.path.basename(
                    item_image_data['local_filename']
                )
                dest_file = os.path.join(
                    settings.MEDIA_ROOT,
                    'collection_images',
                    dest_filename
                )

                try:
                    shutil.copyfile(source_file, dest_file)
                    item_image.active = True
                    item_image.image.name = get_media_path(dest_file)
                    item_image.save()

                    counter += 1
                except Exception as err:
                    LOGGER.error(err)
                    LOGGER.info(
                        "Failed copying file {} of image {} for item {}"
                        "".format(
                            item_image_data['local_filename'],
                            item_image_data['originalImageUrl'],
                            item_id
                        )
                    )

        LOGGER.info("{} images imported".format(counter))
