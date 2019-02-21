"""
Reset REST api usage counts.
"""

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from rest_framework.settings import api_settings

__all__ = (
    'Command',
)


class Command(BaseCommand):
    """Reset REST api usage counts."""

    help = "Reset REST api usage counts."

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('--group',
                            dest='group',
                            action='store',
                            type=str,
                            help="Group ID.")
        parser.add_argument('--user',
                            dest='user',
                            action='store',
                            type=str,
                            default=None,
                            help="User ID.")

    def handle(self, *args, **options):
        groups = set(api_settings.DEFAULT_THROTTLE_RATES.keys())
        group = options['group']
        user_id = options['user']

        if not group:
            raise Exception(
                "You should provide a --group option. "
                "Allowed values are: {}".format(
                    ", ".join(list(groups))
                )
            )

        if group not in groups:
            raise Exception(
                "Invalid group name. Allowed values are: {}".format(
                    ", ".join(list(groups))
                )
            )

        key_pattern = "throttle_{}_{}"
        if user_id:
            user_ids = [user_id]
        else:
            user_ids = User.objects.values_list('id', flat=True)

        for _user_id in user_ids:
            key = key_pattern.format(group, _user_id)
            cache.delete(key)
