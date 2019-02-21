"""
Making sure the `cached_api_calls.Translation.original` field values are
unique in combination with `source_language` and `target_language` fields from
the same model.
"""
from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cached_api_calls', '0005_auto_20180502_0937'),
    ]

    if 'postgres' in settings.DATABASES['default']['ENGINE']:
        operations = [
            migrations.RunSQL(
                r"""
                CREATE UNIQUE INDEX unique_translation
                ON cached_api_calls_translation (md5(original), source_language, target_language);
                """
            ),
        ]
    else:
        operations = []
