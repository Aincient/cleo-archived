import os

from django.conf import settings

__all__ = (
    'MUSES_IMPORTERS_RMO_NL_IMAGES_BASE_PATH',
    'MUSES_IMPORTERS_RMO_NL_IMAGES_BASE_URL',
)

MUSES_IMPORTERS_RMO_NL_IMAGES_BASE_PATH = getattr(
    settings,
    'MUSES_IMPORTERS_RMO_NL_IMAGES_BASE_PATH',
    os.path.join(settings.MEDIA_ROOT, 'collection', 'rmo_nl')
)

MUSES_IMPORTERS_RMO_NL_IMAGES_BASE_URL = getattr(
    settings,
    'MUSES_IMPORTERS_RMO_NL_IMAGES_BASE_URL',
    os.path.join(settings.MEDIA_URL, 'collection', 'rmo_nl')
)
