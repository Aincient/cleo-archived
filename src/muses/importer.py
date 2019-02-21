from .base import get_registered_importer_plugins_uids, importer_registry
from .exceptions import ImporterDoesNotExist, ImporterError

__all__ = (
    'do_import',
    'do_update',
)


def do_import(importer_uid=None, options=None):
    """Import data.

    :param importer_uid:
    :type importer_uid: str
    :return:
    """
    counter = 0
    importer_plugins_uids = get_registered_importer_plugins_uids()
    if importer_uid:
        if importer_uid in importer_plugins_uids:
            importer_cls = importer_registry.get(importer_uid)
            importer = importer_cls(options=options)
            number_of_items = len(importer.run())
            if number_of_items:
                counter += number_of_items
            importer.teardown()
        else:
            raise ImporterDoesNotExist("{} does not exist".format(importer_uid))
    else:
        for importer_uid in importer_plugins_uids:
            importer_cls = importer_registry.get(importer_uid)
            importer = importer_cls(options=options)
            number_of_items = len(importer.run())
            if number_of_items:
                counter += number_of_items
            importer.teardown()
    return counter


def do_update(importer_uid, options=None, fields=None):
    """Update existing import data.

    :param importer_uid:
    :type importer_uid: str
    :return:
    """
    if not fields:
        raise ImporterError("No fields provided.")

    counter = 0
    importer_plugins_uids = get_registered_importer_plugins_uids()

    if importer_uid in importer_plugins_uids:
        importer_cls = importer_registry.get(importer_uid)
        importer = importer_cls(options=options)
        number_of_items = len(importer.do_update(fields=fields))
        if number_of_items:
            counter += number_of_items
        importer.teardown()
    else:
        raise ImporterDoesNotExist("{} does not exist".format(importer_uid))

    return counter
