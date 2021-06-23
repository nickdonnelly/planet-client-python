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
import datetime
import logging

import pytest

from planet import filters

LOGGER = logging.getLogger(__name__)


def test_geometry_filter(geom_geojson, feature_geojson):
    gf = filters.geometry_filter(geom_geojson)
    expected = {'type': 'GeometryFilter',
                'field_name': 'geometry',
                'config': geom_geojson
                }
    assert gf == expected

    ff = filters.geometry_filter(feature_geojson)
    assert ff == expected


def test_date_filter():
    pst = datetime.timezone(datetime.timedelta(hours=-8))
    df = filters.date_filter(
        'acquired',
        gt='2017-01-01T00:00:00Z',
        gte='2017',
        lt=datetime.datetime(2017, 1, 1),
        lte=datetime.datetime(2017, 1, 1, tzinfo=pst)
    )
    expected = {
        'config': {
            'gt': '2017-01-01T00:00:00+00:00',
            'gte': '2017-01-01T00:00:00+00:00',
            'lt': '2017-01-01T00:00:00+00:00',
            'lte': '2017-01-01T00:00:00-08:00',
        },
        'field_name': 'acquired',
        'type': 'DateRangeFilter'
    }
    assert df == expected

    with pytest.raises(filters.FiltersException):
        _ = filters.date_filter('acquired')


def test_update_filter():
    uf = filters.update_filter(
        'ground_control',
        gt='2017',
        gte=datetime.datetime(2017, 1, 1),
    )
    expected = {
        'config': {
            'gt': '2017-01-01T00:00:00+00:00',
            'gte': '2017-01-01T00:00:00+00:00',
        },
        'field_name': 'ground_control',
        'type': 'UpdateFilter'
    }
    assert uf == expected


def test_range_filter():
    rf = filters.range_filter(
        'cloud_cover',
        gt=0.1,
        gte=0.2,
        lt=0.9,
        lte=0.8
    )
    expected = {
        'config': {
            'gt': 0.1,
            'gte': 0.2,
            'lt': 0.9,
            'lte': 0.8,
        },
        'field_name': 'cloud_cover',
        'type': 'RangeFilter'
    }
    assert rf == expected


def test_number_in_filter():
    nf = filters.number_in_filter('gsd', [3, 4])
    expected = {
        'config': [3, 4],
        'field_name': 'gsd',
        'type': 'NumberInFilter'
    }
    assert nf == expected


def test_string_in_filter():
    sf = filters.string_in_filter('quality_category', ['standard', 'beta'])
    expected = {
        'config': ['standard', 'beta'],
        'field_name': 'quality_category',
        'type': 'StringInFilter'
    }
    assert sf == expected


def test_asset_filter():
    af = filters.asset_filter(['analytic_sr', 'udm2'])
    expected = {
        'config': ['analytic_sr', 'udm2'],
        'type': 'AssetFilter'
    }
    assert af == expected


def test_permission_filter():
    pf = filters.permission_filter()
    expected = {
        'config': ['assets:download'],
        'type': 'PermissionFilter'
    }
    assert pf == expected


def test_or_filter():
    f1 = {
        'config': [3, 4],
        'field_name': 'gsd',
        'type': 'NumberInFilter'
    }
    f2 = {
        'config': ['standard', 'beta'],
        'field_name': 'quality_category',
        'type': 'StringInFilter'
    }
    of = filters.or_filter([f1, f2])
    expected = {
        'config': [f1, f2],
        'type': 'OrFilter'
    }
    assert of == expected


def test_and_filter():
    f1 = {
        'config': [3, 4],
        'field_name': 'gsd',
        'type': 'NumberInFilter'
    }
    f2 = {
        'config': ['standard', 'beta'],
        'field_name': 'quality_category',
        'type': 'StringInFilter'
    }
    af = filters.and_filter([f1, f2])
    expected = {
        'config': [f1, f2],
        'type': 'AndFilter'
    }
    assert af == expected


def test_not_filter():
    f1 = {
        'config': [3, 4],
        'field_name': 'gsd',
        'type': 'NumberInFilter'
    }
    nf = filters.not_filter(f1)
    expected = {
        'config': f1,
        'type': 'NotFilter'
    }
    assert nf == expected
