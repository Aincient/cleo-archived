from __future__ import absolute_import, unicode_literals

from django.contrib.gis.db.models import PointField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from six import python_2_unicode_compatible

from ..constants import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, POINT_REGEX

__all__ = (
    'GeoCoding',
)


@python_2_unicode_compatible
class GeoCoding(models.Model):
    """GeoCoding item."""

    name = models.TextField(
        verbose_name=_("Location name"),
        db_index=True,
        unique=True,
    )
    raw_response = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Raw response")
    )
    geo_location = PointField(
        default='',
        blank=True,
        verbose_name=_("Geo coordinates"),
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta(object):
        """Meta options."""

        ordering = ["id"]

    def __str__(self):
        return self.name

    @property
    def coordinates(self):
        """Coordinates usable on the map."""
        if self.geo_location:
            lng, lat = POINT_REGEX.match(self.geo_location).groups()
            return lat, lng
        return None

    @property
    def coordinates_str(self):
        """Coordinates string."""
        lat, lng = self.coordinates
        if lat and lng:
            return "{0},{1}".format(lat, lng)

    @property
    def geolocation_indexing(self):
        """Location for indexing.
        Used in Elasticsearch indexing/tests of `geo_distance` native filter.
        """
        coordinates = self.coordinates
        lat, lon = DEFAULT_LATITUDE, DEFAULT_LONGITUDE
        if coordinates:
            lat, lon = coordinates
        return {
            'lat': lat,
            'lon': lon,
        }
