import os
import re

from django.conf import settings

from muses.base import BaseExporter, exporter_registry
from muses.search_index.documents.collection_item import CollectionItemDocument
from muses.naive_classification.definitions import materials
from muses.cifar10_helpers import write_batch

__title__ = 'muses.exporters.coin.material'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'MaterialExporter',
)


class MaterialExporter(BaseExporter):
    """Naive exporter"""
    uid = 'material'
    name = "Material"
    dataset_dir = os.path.join(
        settings.BASE_DIR,
        '..',
        'datasets',
        'material'
    )

    categories = materials

    def get_item_categories(self, item):
        """Get item data for classifier.
        Try to find (synonyms) of a class name in the object title or object types.
        If there are multiple occurences, determine the most relevant one.
        Return the item class if there is one

        :param item:
        :return:
        """

        category = None
        object_materials = ""

        if item.material_en:
            object_materials = [mat.lower() for mat in item.material_en]

        if object_materials:
            for key in materials:
                if materials[key].lower() in object_materials:
                    category = key

        return category

    def get_export_filename(self):
        """Get export filename.

        :return:
        """
        return os.path.join(
            settings.MEDIA_ROOT,
            'datasets',
            'material',
            'data_batch_1'
        )

    def do_export(self):
        """Import.

        :return:
        """
        images = []
        # The maximum amount of images that can be added for a single class.
        # Necessary to prevent data imbalance to some degree
        max_images = 3000
        total_items = 0
        categorized_items = 0
        counts = {}
        for i in range(0, len(materials)):
            counts[str(i)] = 0

        collection_items = CollectionItemDocument.search().scan()
        for item in collection_items:
            total_items += 1
            category = self.get_item_categories(item)
            if category:
                categorized_items += 1
                for image in item.images:
                    if counts[category] < max_images:
                        counts[category] += 1
                        images.append(
                            (image, category)
                        )

        # Display how often each class occured
        count_names = {}
        for key in counts.keys():
            count_names[materials[key]] = counts[key]
        print('Categorized {} of {} items'.format(categorized_items, total_items))
        for key in count_names:
            print('{}: {}\n'.format(key, count_names[key]))
        return images

    def run(self):
        """Run.

        Overrides method in base exporter to make sure class examples are proportionally spread over training and
        test data

        :return:
        """
        data = self.do_export()
        data_items = []
        test_items = []

        # Make sure that class occurrences are proportionally spread over training and test data
        for key in materials.keys():
            class_list = [item for item in data if item[1] == key]

            number_of_items = len(class_list)
            number_of_test_items = int(number_of_items / 5)
            number_of_data_items = number_of_items - number_of_test_items

            data_items.extend(class_list[0:number_of_data_items])
            test_items.extend(class_list[number_of_data_items:])

        # Write test and training batch
        write_batch(
            images_list=data_items,
            dest_filename=os.path.join(self.dataset_dir, self.data_filename),
            text_labels=self.categories
        )

        write_batch(
            images_list=test_items,
            dest_filename=os.path.join(self.dataset_dir, self.test_filename),
            text_labels=self.categories
        )

        return data

exporter_registry.register(MaterialExporter)
