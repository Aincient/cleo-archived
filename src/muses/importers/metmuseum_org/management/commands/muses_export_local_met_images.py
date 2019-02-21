from __future__ import absolute_import, unicode_literals

from collections import defaultdict
import os
import logging
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from muses.collection.helpers import clean_met_images
from muses.collection.models import Item, Image as ItemImage

from muses.importers.metmuseum_org.helpers import MetropolitanClient

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Export local MET images."""

    help = "Export local MET images."

    requires_system_checks = False

    # def add_arguments(self, parser):
    #
    #     parser.add_argument('--re-crop-existing',
    #                         action='store_true',
    #                         dest='re_crop_existing',
    #                         default=False,
    #                         help="Re-crop existing active images.")

    def handle(self, *args, **options):
        """Handle.

        :param args:
        :param options:
        :return:
        """
        # Prepare the queryset. We're only interested in MET images that have
        # been successfully downloaded.
        queryset = Item.objects.exclude(
            Q(images__image__isnull=True) | Q(images__image__exact=''),
        ).filter(
            Q(importer_uid='metmuseum_org') & Q(images__active=True)
        ).prefetch_related('images')

        # We want to export all images to a separate directory and store
        # the links between images and correspondent item images in JSON cache.
        # We already do have a JSON cache for all imported images. What we
        # plan to do is to load all JSON cache records into one and add a
        # single field `original_image_url` to each image JSON data.
        client = MetropolitanClient()
        client.configure_from_settings()

        # Load all images from JSON cache into a single dict, where key is the
        # correspondent item `record_number` (local db) or `Object ID` (in JSON
        # cache).
        images_json = client.load_object_list_images_from_json_cache()
        # Name of the directory to which the images will be copied.
        export_dir = os.path.join(settings.MEDIA_ROOT, 'export')

        # Dict to contain all local images (copied to the `export_dir`).
        local_images = defaultdict(list)
        copied_images_set = set([])
        copied_images_set2 = set([])
        counter = 0

        # Iterate through the queryset
        for item in queryset:
            # We do not have a image reference (ID or something). What we
            # do have is the `originalImageUrl` data (in both JSON cache
            # and our database (`collection.Image`).
            item_id = item.record_number

            # If our initial JSON contains images for the given item...
            if item_id in images_json:
                # We loop through all images that we have saved locally...
                for item_image in item.images.all():
                    # ...and copy them to the given destination (`export_dir`).
                    # Results are stored in the `local_images` dict. Note, that
                    # we store the `api_url` (local database) or
                    # `originalImageUrl` (JSON cache) along in order to be
                    # able to match the exported images later.
                    source_file = item_image.image.path

                    if source_file in copied_images_set:
                        LOGGER.info(
                            "{} image for item {} has already been copied"
                            "".format(source_file, item_id)
                        )
                    copied_images_set.add(source_file)
                    if item_image.api_url in copied_images_set2:
                        LOGGER.info(
                            "{} image for item {} has already been copied"
                            "".format(item_image.api_url, item_id)
                        )
                    copied_images_set2.add(item_image.api_url)

                    dest_filename = os.path.basename(item_image.image.path)
                    dest_file = os.path.join(export_dir, dest_filename)
                    try:
                        shutil.copyfile(source_file, dest_file)
                    except Exception as err:
                        LOGGER.error(
                            "Could not copy file {} to {}"
                            "".format(source_file, dest_file)
                        )
                        LOGGER.error(err)

                    counter += 1
                    local_images[item_id].append(
                        {
                            'filename': dest_filename,
                            'original_image_url': item_image.api_url,
                        }
                    )

        # Now that we have all images exported to the `export_dir`, we can
        # loop through original `images_json` dict and add links to the
        # local files.

        # Loop through original JSON cache.
        for item_id, item_images_data in images_json.items():
            # If there have been images copied locally for the selected
            # item, try to find the references between images.
            if item_id in local_images:
                # Loop though all local images for the given item.
                for local_image in local_images[item_id]:
                    for _cnt, item_image_data in enumerate(item_images_data):
                        if (
                            item_image_data['originalImageUrl'] ==
                                local_image['original_image_url']
                        ):
                            item_image_data['local_filename'] \
                                = local_image['filename']
                            item_images_data[_cnt] = item_image_data
                            break

            images_json[item_id] = item_images_data

        # Write updated data into JSON cache (separate file).
        client.write_object_images_to_json_cache(images_json)

        LOGGER.info("{} images exported".format(counter))
        LOGGER.info("{} images exported (1st)".format(len(copied_images_set)))
        LOGGER.info("{} images exported (2nd)".format(len(copied_images_set2)))
