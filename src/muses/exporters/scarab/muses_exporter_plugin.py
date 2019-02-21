import os

from django.conf import settings

from ...base import BaseExporter, exporter_registry
from ...search_index.documents.collection_item import CollectionItemDocument

__all__ = (
    'ScarabExporter',
)


class ScarabExporter(BaseExporter):
    """Scarab exporter"""

    uid = 'scarab'
    name = "Scarab"
    dataset_dir = os.path.join(
        settings.BASE_DIR,
        '..',
        'datasets',
        'scarab'
    )
    # TODO: change this to English variant once we switch
    categories = {
        0: 'koper',
        1: 'metaal',
        2: 'zilver',
    }

    def get_item_categories(self, item):
        """Get item data for classifier.

        :param item:
        :return:
        """
        categories = []
        for material in item.material:
            categories.append(self.reversed_categories.get(material))

        # TODO: Adding multiple categories results into an error. Debug
        # later. Fine for now.
        return categories[0] if categories else None

    def get_export_filename(self):
        """Get export filename.

        :return:
        """
        return os.path.join(
            settings.MEDIA_ROOT,
            'datasets',
            'scarab',
            'data_batch_1'
        )

    def do_export(self):
        """Import.

        :return:
        """
        images = []
        items = CollectionItemDocument.search().filter(
            'term',
            **{'primary_object_type.dutch': 'scarab'}
        ).scan()
        for item in items:
            for image in item.images:
                images.append(
                    (image, self.get_item_categories(item))
                )

        return images


exporter_registry.register(CoinExporter)
