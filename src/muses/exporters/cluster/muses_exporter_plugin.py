import os

from django.conf import settings

from ...base import BaseExporter, exporter_registry
from ...search_index.documents.collection_item import CollectionItemDocument
from muses.generate_dataset import write_batch

__all__ = (
    'ClusterExporter',
)


class ClusterExporter(BaseExporter):
    """All exporter"""

    uid = 'cluster'
    name = "Cluster"
    dataset_dir = os.path.join(
        settings.BASE_DIR,
        '..',
        'datasets',
        'cluster'
    )

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

    def run(self):
        """Run.

        We pickle results and save them in pickle format in batches of
        10,000.00 per file.

        :return:
        """
        data = self.do_export()

        data_items = data

        write_batch(
            images_list=data_items,
            dest_filename=os.path.join(self.dataset_dir, self.data_filename),
            text_labels=self.categories
        )

        return data

    def do_export(self):
        """Import.

        :return:
        """
        images = set([])
        items = CollectionItemDocument.search().scan()
        for item in items:

            for image in item.images:
                images.add(
                    (image, None)
                )

        return list(images)


exporter_registry.register(ClusterExporter)
