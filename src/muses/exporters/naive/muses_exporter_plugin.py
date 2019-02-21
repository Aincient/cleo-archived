import os
import re

from django.conf import settings

from muses.base import BaseExporter, exporter_registry
from muses.search_index.documents.collection_item import CollectionItemDocument
from muses.naive_classification.definitions import classes, synonyms, exclude
from muses.cifar10_helpers import write_batch

__all__ = (
    'NaiveExporter',
)

'''
The exporter uses the class and synonym lists from the definitions in naive_classification and matches those with
object titles and object types. If a synonym is present, it classifies the item as that class.
If multiple class synonyms appear in a single image, it counts how often synonyms of a class name appear in object
text and title, and classifies the item as the class with the highest count. If word counts are equal, it looks at the
longest word, mainly because it deals with more specific terms that contain a less specific term (e.g. 'heart scarab'
and 'scarab').
For some classes, the synonyms are only matched to the object type, because the word occurs in item titles too often.

After categorizing all items in this way, it exports a maximum of 3000 images of each class, to prevent a huge data
imbalance. The exporter also distributes examples of each class proportionally over training and test data (so 1/5 of
the examples of each class end up in the test data).
'''


class NaiveExporter(BaseExporter):
    """Naive exporter"""
    uid = 'naive'
    name = "Naive"
    dataset_dir = os.path.join(
        settings.BASE_DIR,
        '..',
        'datasets',
        'naive'
    )

    categories = classes

    def word_match(self, syn, object_text, max_key, key_count, hit):
        """Determine if a synonym for a class occurs in a text, and count how much synonyms are present in the text
        If synonyms of other classes are also present, determine which class is most likely

        :param syn: synonym
        :param object_text: text to find the synonym in
        :param max_key:
        :param key_count:
        :param hit: current longest single word
        :return:
        """
        if re.search(r"\b" + re.escape(syn) + r"\b", object_text, flags=re.I):
            key_count += 1
            newhit = syn
            if key_count > max_key:
                return True
            elif key_count == max_key:
                if len(newhit) > len(hit):
                    return True
        return False

    def category_match(self, key, max_key, hit, model_field):
        key_count = 0
        category = None
        for syn in synonyms[key]:
            if ';' in syn:
                model_string = "; ".join(model_field)
                if self.word_match(syn, model_string, max_key, key_count, hit):
                    hit = key
                    key_count += 1
                    category = self.reversed_categories[key]

            else:
                for model_string in model_field:
                    if self.word_match(syn, model_string, max_key, key_count, hit):
                        hit = key
                        key_count += 1
                        category = self.reversed_categories[key]
        return category

    def get_item_categories(self, item):
        """Get item data for classifier.
        Try to find (synonyms) of a class name in the object title or object types.
        If there are multiple occurences, determine the most relevant one.
        Return the item class if there is one

        :param item:
        :return:
        """

        category = None
        object_types = ""
        object_title = ""
        hit = ""

        if item.object_type_en:
            object_types = item.object_type_en
        if item.title_en:
            object_title = item.title_en

        max_key = 0
        if object_types:
            for key in synonyms.keys():
                key_count = 0
                move_on = False
                for ex in exclude[key]:
                    for object_type in object_types:
                        if self.word_match(ex, object_type, max_key, key_count, hit):
                            move_on = True
                if not move_on:
                    match = self.category_match(key, max_key, hit, object_types)
                    if match:
                        category = match

        if object_title and not category:
            for key in synonyms.keys():
                key_count = 0
                move_on = False
                for ex in exclude[key]:
                    for title in object_title:
                        if self.word_match(ex, title, max_key, key_count, hit):
                            move_on = True

                # We are omitting scarab and mummy,
                # because the word occurs in too much examples of items that are not from those classes
                if key not in ['scarab', 'mummy'] and not move_on:
                    match = self.category_match(key, max_key, hit, object_title)
                    if match:
                        category = match

        return category

    def get_export_filename(self):
        """Get export filename.

        :return:
        """
        return os.path.join(
            settings.MEDIA_ROOT,
            'datasets',
            'naive',
            'data_batch_1'
        )

    def do_export(self):
        """Import.

        :return:
        """
        images = []
        # The maximum amount of images that can be added for a single class.
        # Necessary to prevent data imbalance to some degree
        max_images = 2500
        total_items = 0
        categorized_items = 0
        categorized_images = 0
        counts = {}
        for i in range(0, len(classes)):
            counts[str(i)] = 0

        collection_items = CollectionItemDocument.search().scan()
        for item in collection_items:
            total_items += 1
            category = self.get_item_categories(item)
            if category:
                categorized_items += 1
                for image in item.images:
                    if counts[category]<max_images:
                        counts[category] += 1
                        categorized_images += 1
                        images.append(
                            (image, category)
                        )

        # Display how often each class occured
        count_names = {}
        for key in counts.keys():
            count_names[classes[key]] = counts[key]
        print('Categorized {} of {} items and added {} images'.format(
            categorized_items,
            total_items,
            categorized_images
        ))
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
        for key in classes.keys():
            class_list = [item for item in data if item[1] == key]

            number_of_items = len(class_list)

            number_of_test_items = int(number_of_items / 6)
            number_of_data_items = number_of_items - number_of_test_items

            train_items = class_list[0:number_of_data_items]
            test_items.extend(class_list[number_of_data_items:])

            # Oversampling
            while len(train_items) < 800:
                if len(train_items) > 400:
                    diff = 800 - len(train_items)
                    train_items.extend(train_items[:diff])
                else:
                    train_items.extend(train_items[:])

            data_items.extend(train_items)

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

exporter_registry.register(NaiveExporter)
