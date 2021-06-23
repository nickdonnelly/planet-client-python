# Copyright 2021 Planet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""Functionality for building and parsing data api search filters"""
import datetime
from dateutil import parser
import logging
import typing

from . import geojson

DateLike = typing.Union[datetime.datetime, str]

LOGGER = logging.getLogger(__name__)


class FiltersException(Exception):
    '''exceptions raised by the filters module'''
    pass


def _filter(
    filter_type: str,
    config: dict,
    field: str = None
) -> dict:
    data = {'type': filter_type, 'config': config}
    if field:
        data.update({'field_name': field})
    return data


def geometry_filter(
    geom: typing.Union[geojson.Geometry, dict]
) -> dict:
    '''Build a GeometryFilter.

    The GeometryFilter can be used to search for items with a footprint
    geometry which intersects with the specified geometry.

    Parameters:
        geom: Search for items that intersect given geometry.
    '''
    geom = geojson.Geometry(geom)
    return _filter('GeometryFilter', geom, field='geometry')


def _range_filter(
    name: str,
    field: str,
    gt: DateLike = None,
    gte: DateLike = None,
    lt: DateLike = None,
    lte: DateLike = None,
    callback: callable = None
) -> dict:
    fields = ['gt', 'gte', 'lt', 'lte']
    values = [gt, gte, lt, lte]
    if not any(values):
        raise FiltersException('Must specify one of gt, gte, lt, or lte.')

    if not callback:
        def callback(v): return v

    config = dict((k, callback(v)) for k, v in zip(fields, values) if v)
    return _filter(name, config, field=field)


def date_filter(
    field: str,
    gt: DateLike = None,
    gte: DateLike = None,
    lt: DateLike = None,
    lte: DateLike = None
) -> dict:
    '''Build a DateRangeFilter.

    The DateRangeFilter matches items with a specified timestamp property
    which falls within a specified range.

    Date parameters can be a str that is ISO-8601 format or a datetime.datetime
    object. If no timezone is provided, UTC is assumed for RFC 3339
    compatability. If no timezone is provided, UTC is assumed for RFC 3339
    compatability.

    Parameters:
        field: Property with a timestamp. Examples are `acquired`, `published`,
            and `updated`.
        gt: Filter to dates greater than value.
        gte: Filter to dates greater than or equal to value.
        lt: Filter to dates less than value.
        lte: Filter to dates less than or equal to value.

    Raises:
        FiltersException: If 'gt', 'gte', 'lt', and 'lte' are all empty or if
            'gt', 'gte', 'lt', or 'lte' is a string that is not ISO-8601
            format.
    '''
    return _range_filter(
        'DateRangeFilter',
        field,
        gt=gt,
        gte=gte,
        lt=lt,
        lte=lte,
        callback=_to_rfc3339
    )


def update_filter(
    field: str,
    gt: DateLike = None,
    gte: DateLike = None
) -> dict:
    '''Build an UpdateFilter.

    The UpdateFilter can be used to filter items by changes to a specified
    metadata field value made after a specified date, due to a republishing
    event. This feature allows you identify items which may have been
    republished with improvements or fixes, enabling you to keep your internal
    catalogs up-to-date and make more informed redownload decisions. The filter
    works for all items published on or after April 10, 2020.

    While any field name may be specified, the primary fields which may be
    impacted by quality, usability, or rectification improvements are geometry,
    quality_category, ground_control, and udm or udm2 fields (including
    visible_percent, clear_percent, cloud_percent, heavy_haze_percent,
    light_haze_percent, snow_ice_percent, shadow_percent, cloud_cover,
    black_fill, usable_data, and anomalous_pixels).


    Parameters:
        field: Property to filter on.
        gt: Filter to update dates greater than value.
        gte: Filter to update dates greater than or equal to value.

    Raises:
        FiltersException: If 'gt' and 'gte' are both empty or if they are
            a string that is not ISO-8601 format.
    '''
    try:
        filt = _range_filter(
            'UpdateFilter',
            field,
            gt=gt,
            gte=gte,
            callback=_to_rfc3339
        )
    except FiltersException:
        raise FiltersException('Must specify one of gt or gte.')
    return filt


def _to_rfc3339(
    date: DateLike
) -> str:
    '''Create RFC 3339 string from input.

    If no timezone is provided, UTC is assumed for RFC 3339 compatability.

    Parameters:
        date: A str that is ISO-8601 format or a datetime.datetime object.
            If no timezone is provided, UTC is assumed for RFC 3339
            compatability. If no timezone is provided, UTC is assumed for
            RFC 3339 compatability.

    Raises:
        FiltersException: If date is a string that is not ISO-8601 format.
    '''
    if not isinstance(date, datetime.datetime):
        date = parser.isoparse(date)

    if not date.tzinfo:
        date = date.replace(tzinfo=datetime.timezone.utc)

    return date.isoformat()


def range_filter(
    field: str,
    gt: DateLike = None,
    gte: DateLike = None,
    lt: DateLike = None,
    lte: DateLike = None
) -> dict:
    '''Build a RangeFilter.

    The RangeFilter can be used to search for items with numerical properties.
    It is useful for matching fields that have a continuous range of values
    such as cloud_cover or view_angle.

    Parameters:
        field: Property to filter on.
        gt: Filter to property values greater than specified value.
        gte: Filter to property values greater than or equal to specified
            value.
        lt: Filter to property values less than specified value.
        lte: Filter to property values less than or equal to specified value.

    Raises:
        FiltersException: If 'gt', 'gte', 'lt', and 'lte' are all empty.
    '''
    return _range_filter(
        'RangeFilter',
        field,
        gt=gt,
        gte=gte,
        lt=lt,
        lte=lte
    )


def number_in_filter(
    field: str,
    values: typing.List[int]
) -> dict:
    '''Build a NumberInFilter.

    The NumberInFilter can be used to search for items with numerical
    properties. It is useful for matching fields such as gsd.

    Parameters:
        field: Property to filter on.
        values: Filter to property values that contain specified numbers.
    '''
    return _filter('NumberInFilter', values, field=field)


def string_in_filter(
    field: str,
    values: typing.List[str]
) -> dict:
    '''Build a StringInFilter.

    The StringInFilter can be used to search for items with string properties
    such as instrument or quality_category. Boolean properties such as
    ground_control are also supported with the StringInFilter.

    Parameters:
        field: Property to filter on.
        values: Filter to property values that contain specified strings.
    '''
    return _filter('StringInFilter', values, field=field)


def asset_filter(asset_types: typing.List[str]) -> dict:
    '''Build an AssetFilter.

    The AssetFilter can be used to search for items which have published any of
    the specified specified asset_types.

    An AndFilter can be used to filter items by multiple asset types.

    Parameters:
        asset_types: Match at least one of these asset types.
    '''
    return _filter('AssetFilter', asset_types)


def permission_filter() -> dict:
    '''Build a PermissionFilter.

    The PermissionFilter can be used to limit results to items that a user has
    permission to download.
    '''
    return _filter('PermissionFilter', ['assets:download'])


def or_filter(filters: typing.List[dict]) -> dict:
    '''Build an OrFilter.

    The OrFilter can be used to match items with properties or permissions
    which match at least one of the nested filters.

    Parameters:
        filters: Match at least one of these nested filters.
    '''
    return _filter('OrFilter', filters)


def and_filter(filters: typing.List[dict]) -> dict:
    '''Build an AndFilter.

    The AndFilter can be used to limit results to items with properties or
    permissions which match all nested filters.

    It is most commonly used as a top-level filter to ensure criteria across
    all field and permission filters are met.

    Parameters:
        filters: Match all of these nested filters.
    '''
    return _filter('AndFilter', filters)


def not_filter(filt: dict) -> dict:
    '''Build a NotFilter.

    The NotFilter can be used to match items with properties or permissions
    which do not match the nested filters.

    Multiple NotFilters can be nested within an AndFilter to filter across
    multiple fields or permission values.

    Parameters:
        filters: Match all items that do not match this this nested filter.
    '''
    return _filter('NotFilter', filt)
