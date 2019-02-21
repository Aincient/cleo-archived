import os

from django.conf import settings

from ...base import BaseExporter, exporter_registry
from ...search_index.documents.collection_item import CollectionItemDocument
from muses.generate_dataset import write_batch

__all__ = (
    'AllExporter',
)


class AllExporter(BaseExporter):
    """All exporter"""

    uid = 'all'
    name = "All"
    dataset_dir = os.path.join(
        settings.BASE_DIR,
        '..',
        'datasets',
        'all'
    )
    # categories = {
    #     0: 'amulet',
    #     1: 'zegel',
    #     2: 'scherf',
    #     3: 'bron',
    #     4: 'munt',
    #     5: 'handschrift',
    #     6: 'oesjebti',
    #     7: 'fragment',
    #     8: 'bekleedsel',
    #     9: 'votiefbeeld',
    # }
    categories = {
        0: 'amulet',
        1: 'zegel',
        2: 'scherf',
        3: 'munt',
        4: 'oesjebti',
        5: 'fragment',
        6: 'bekleedsel',
        7: 'votiefbeeld',
    }

    def get_item_categories(self, item):
        """Get item data for classifier.

        :param item:
        :return:
        """
        return self.reversed_categories.get(item.primary_object_type_en)

    def get_export_filename(self):
        """Get export filename.

        :return:
        """
        return os.path.join(
            settings.MEDIA_ROOT,
            'datasets',
            'all',
            'data_batch_1'
        )

    def do_export(self):
        """Import.

        :return:
        """
        images = set([])
        items = CollectionItemDocument.search().scan()
        for item in items:
            item_category = self.get_item_categories(item)

            if item_category is None:
                item_category = 0

            for image in item.images:
                images.add(
                    (image, self.get_item_categories(item))
                )

        return list(images)


exporter_registry.register(AllExporter)
