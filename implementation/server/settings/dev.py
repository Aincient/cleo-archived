import logging
from .base import *

MOLLIE_API_KEY = 'xxx'
SECRET_KEY = 'xxx'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'muses',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'postgres',
        'PORT': 5432,
    }
}

# Elasticsearch configuration
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200',
        'timeout': 30,
        # 'user': 'elastic',
        # 'password': 'changeme',
        # 'http_auth': 'elastic:changeme',
    },
}


logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# if LOGGING:
#     LOGGING['loggers'].update(
#         {
#             'django.db': {
#                 'handlers': ['console'],
#                 'level': 'DEBUG',
#                 'propagate': False,
#             }
#         }
#     )
WEBPACK_LOADER = {
     'DEFAULT': {
             'BUNDLE_DIR_NAME': '',
             'STATS_FILE': os.path.join('../..', 'webpack-stats.json'),
     }
 }

SITE_DOMAIN = 'http://8478c792.ngrok.io'
GOOGLE_API_KEY = 'xxx'


# ***********************************************************************
# ************************ muses/cleo (this app) ************************
# ***********************************************************************

# Muses config
MUSES_CONFIG = {
    'importers': {
        'rmo_nl': {
            'url': 'http://api.rmo.nl:17521/action=get&command=search&query=*egypt*&range=1-1000000&fields=*',  # NOQA
            'tmp_dir': PROJECT_DIR(
                os.path.join('..', '..', 'import', 'rmo_nl')
            ),
        },
        'brooklynmuseum_org': {
            'base_url': 'https://www.brooklynmuseum.org/',
            'object_list_url': '/api/v2/object/?collection_id=5&limit=35',
            'geographical_location_list_url': '/api/v2/geographical-location/'
                                              '?limit=35',
            'object_images_url': '/api/v2/object/{}/image/',
            'api_key': 'xxx',
            'tmp_dir': PROJECT_DIR(
                os.path.join('..', '..', 'import', 'brooklynmuseum_org')
            ),
        },
        'thewalters_org': {
            'base_url': 'http://api.thewalters.org/',
            'object_list_url': '/v1/objects.json?creator=Egyptian',
            'object_detail_url': '/v1/objects/{}.json',
            'object_images_url': '/v1/objects/{}/images.json',
            'api_key':
                '58fx6wTx46Z1Vu9Cll86k3YfjH6Xti9amdtWKR2WchjbwGvZgXAmlGZ1Z0Eoqw4L',
            'tmp_dir': PROJECT_DIR(
                os.path.join('..', '..', 'import', 'thewalters_org')
            ),
        },
        'metmuseum_org': {
            'object_list_url': 'https://github.com/metmuseum/openaccess/raw/master/MetObjects.csv',  # NOQA
            'object_images_url': 'http://www.metmuseum.org/api/Collection/additionalImages?crdId={}&page=1&perPage=10',  # NOQA
            'tmp_dir': PROJECT_DIR(
                os.path.join('..', '..', 'import', 'metmuseum_org')
            ),
        },
    },
    'classification': {
        'naive_classification': {
            'model_path': os.path.join(
                BASE_DIR,
                '..',
                '..',
                'src',
                'muses',
                'naive_classification',
                'models',
                'trained_model_new.h5'
            )
        },
    },
}

# Do not put any settings below this line
try:
    from .local_settings import *
except ImportError:
    pass
