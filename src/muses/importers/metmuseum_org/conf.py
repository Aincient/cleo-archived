import os

from django.conf import settings

__all__ = (
    'MUSES_IMPORTERS_METMUSEUM_ORG_IMAGES_BASE_PATH',
    'MUSES_IMPORTERS_METMUSEUM_ORG_IMAGES_BASE_URL',
)

MUSES_IMPORTERS_METMUSEUM_ORG_IMAGES_BASE_PATH = getattr(
    settings,
    'MUSES_IMPORTERS_METMUSEUM_ORG_IMAGES_BASE_PATH',
    os.path.join(settings.MEDIA_ROOT, 'collection', 'metmuseum_org')
)

MUSES_IMPORTERS_METMUSEUM_ORG_IMAGES_BASE_URL = getattr(
    settings,
    'MUSES_IMPORTERS_METMUSEUM_ORG_IMAGES_BASE_URL',
    os.path.join(settings.MEDIA_URL, 'collection', 'metmuseum_org')
)
