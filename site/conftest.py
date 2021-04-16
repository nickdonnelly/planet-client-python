# fixtures for doctests
import pytest
import respx

import planet


TEST_URL = 'http://MockNotRealURL/'


@pytest.fixture
def ttt():
    return 'hi'


@pytest.fixture
def TestOrdersClient(sess):
    with respx.mock:
        yield planet.OrdersClient(sess, base_url=TEST_URL)
