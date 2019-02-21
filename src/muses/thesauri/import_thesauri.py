import re
import json
import requests
from django.db import IntegrityError
from muses.search_index.documents.collection_item import CollectionItemDocument
from muses.thesauri import ThesauriClient
from muses.cached_api_calls.models import ThesauriTranslation
from muses.collection.models import Period
from .constants import key_list, API_START_PATTERN, API_END_PATTERN

__all__ = (
    'import_thesauri',
)


def import_thesauri_from_database(source_language, target_language, keys=key_list, update_existing=False):
    """Import Thesauri translations of words in a collection

    :param source_language: ISO code of language to translate from
    :param target_language: ISO code of language to translate to
    :param keys: Which fields in the collection should be translated
    :type target_language: str
    :type source_language: str
    :type keys: list
    :return:
    """
    client = ThesauriClient()
    word_list = []

    print('Generating unique word list')
    for item in CollectionItemDocument().search().scan():
        for key in keys:
            if item[key]:
                for text in item[key]:
                    for word in text.split(' '):
                        word_list.append(re.sub(r'[^a-zA-Z\-]', '', word))

    word_list = list(set(word_list))

    print('Translating {} words'.format(len(word_list)))
    for idx, word in enumerate(word_list):
        print('Translated {} of {} words'.format(idx, len(word_list)))
        try:
            ThesauriTranslation.objects.get(
                original=word.lower(),
                source_language=source_language,
                target_language=target_language
            )
        except ThesauriTranslation.DoesNotExist:
            result = client.translate(
                source_language=source_language,
                target_language=target_language,
                term=word,
                use_cache=False
            )
            if result:
                try:
                    ThesauriTranslation.objects.create(
                        original=word.lower(),
                        translation=result,
                        source_language=source_language,
                        target_language=target_language,
                        translation_exists=True
                    )
                    print('Translated {} to {}'.format(word, result))
                except IntegrityError:
                    pass


def import_thesauri_from_list(input_list, target_language, update_existing=False):
    """Get all translations from a structured list of known Thesauri concepts.
    Recursively go through all concepts in the list.

    :param input_list: a list of known Thesauri concepts
    :param target_language: ISO code of language to translate to
    :param update_existing:
    :type input_list: list
    :type target_language: str
    :return:
    """
    client = ThesauriClient()

    for concept in input_list:
        if concept['id']:
            title = concept['title']
            if title:
                source_language = concept['lang']
                result = client.translate_from_key(target_language, concept['id']).strip()

                if result:
                    try:
                        ThesauriTranslation.objects.create(
                            original=title.lower(),
                            translation=result,
                            source_language=source_language,
                            target_language=target_language,
                            translation_exists=True
                        )
                        print('Translated {} to {}'.format(title.lower(), result))
                    except IntegrityError:
                        if update_existing:
                            translation_source = ThesauriTranslation.objects.get(
                                original=title.lower(),
                                source_language=source_language,
                                target_language=target_language,
                            )
                            # We do not want to update supervised translations
                            if not translation_source.supervised:
                                translation_source.translation = result
                                translation_source.translation_exists = True
                                translation_source.save()

                    try:
                        ThesauriTranslation.objects.create(
                            original=result,
                            translation=title.lower(),
                            source_language=target_language,
                            target_language=source_language,
                            translation_exists=True
                        )
                        print('Translated {} to {}'.format(title.lower(), result))
                    except IntegrityError:
                        if update_existing:
                            translation_reverse = ThesauriTranslation.objects.get(
                                original=result,
                                source_language=target_language,
                                target_language=source_language,
                            )
                            # We do not want to update supervised translations
                            if not translation_reverse.supervised:
                                translation_reverse.translation = title.lower()
                                translation_reverse.translation_exists = True
                                translation_reverse.save()

            if 'children' in concept:
                import_thesauri_from_list(concept['children'], target_language, update_existing)


def generate_period_tree(filename, update_existing=False):
    """Generate a period tree based on Thesauri period data.
    The tree is generated from the root node of the file.
    Currently stores English and Dutch names of the period.
    Requires the user to store a json version with Thesauri data.
    Can be found at http://thot.philo.ulg.ac.be/api/json/thesaurus/dating
    It is important that you only take the 'period' branch of that file, and not
    'dating and dating methods'.

    :param filename: filename where json file is stored
    :type filename: str
    :return:
    """
    with open(filename) as f:
        period_list = json.load(f)

    if not isinstance(period_list, (list, tuple)):
        period_list = [period_list]

    root_node = generate_period_tree_layer(period_list, None, update_existing)
    # We manually add a node for Coptic Period, since it is not in THOT
    try:
        coptic = Period.objects.create(
            name_en='Coptic Period',
            name_nl='Koptische Periode',
            parent=root_node
        )
        coptic.refresh_from_db()
        root_node.refresh_from_db()
        coptic.move_to(root_node, position='last-child')
        coptic.save()
    except IntegrityError:
        pass


def generate_period_tree_layer(input_list, parent, update_existing):
    """Recursively build up a tree layer by layer

    :param input_list:
    :param parent: parent of current layer of periods
    :type input_list: list
    :type parent: Period object
    :return:
    """
    client = ThesauriClient()

    for concept in input_list:
        if concept['title']:
            name_en = concept['title'].rstrip()
            try:
                if parent:
                    period = Period.objects.create(
                        name_en=name_en,
                        parent=parent
                    )
                else:
                    period = Period.objects.create(
                        name_en=name_en
                    )
                name_nl = client.translate_from_key('nl', concept['id'])
                if name_nl:
                    setattr(period, 'name_nl', name_nl)

                date_start_response = requests.get(
                    API_START_PATTERN.format(concept['id']),
                )
                if (
                        date_start_response.ok and
                        date_start_response.text != 'This concept has no date range attached to it'
                ):
                    date_begin = int(date_start_response.text)
                    setattr(period, 'date_begin_en', date_begin)

                date_end_response = requests.get(
                    API_END_PATTERN.format(concept['id']),
                )
                if (
                        date_end_response.ok and
                        date_end_response.text != 'This concept has no date range attached to it'
                ):
                    date_end = int(date_end_response.text)
                    setattr(period, 'date_end_en', date_end)
                if parent:
                    parent.refresh_from_db()
                    period.refresh_from_db()
                    period.move_to(parent, position='last-child')
                period.save()

            except IntegrityError:
                period = Period.objects.get(
                    name_en=name_en,
                )
                if update_existing:
                    name_nl = client.translate_from_key('nl', concept['id'])
                    if name_nl:
                        setattr(period, 'name_nl', name_nl)

                    date_start_response = requests.get(
                        API_START_PATTERN.format(concept['id']),
                    )
                    if (
                        date_start_response.ok and
                            date_start_response.text != 'This concept has no date range attached to it'
                    ):
                        date_begin = int(date_start_response.text)
                        setattr(period, 'date_begin_en', date_begin)

                    date_end_response = requests.get(
                        API_END_PATTERN.format(concept['id']),
                    )
                    if (
                        date_end_response.ok and
                            date_end_response.text != 'This concept has no date range attached to it'
                    ):
                        date_end = int(date_end_response.text)
                        setattr(period, 'date_end_en', date_end)
                    if parent:
                        try:
                            parent.refresh_from_db()
                            period.refresh_from_db()
                            period.move_to(parent, position='last-child')
                        except:
                            pass
                    period.save()
            if 'children' in concept and concept['children']:
                generate_period_tree_layer(concept['children'], period, update_existing)
            if period and period.is_root_node():
                return period

