import pytest
import numpy as np
import segyio
import xarray.testing
import numpy.testing
import lasio

from subsurface import curve
from subsurface import units


# @pytest.fixture(scope="module")
# def curve():
#     data = np.arange(100)
#     coords = np.linspace(0, 10, data.size)
#     return curve.Curve(data, coords)


def test_curve():
    """Test creating Curve instance."""
    data = np.arange(100)
    coords = np.linspace(0, 10, data.size)
    c = curve.Curve(data, coords)
    assert isinstance(c, curve.Curve)
    assert isinstance(c[2:4], curve.Curve)


def test_from_lasio():
    """Test creating Curve instance from lasio curve."""
    l = lasio.read("tests/data/test.las")
    c = curve.from_lasio(l.curves['GR'], basis=l.curves['DEPT'])
    assert isinstance(c, curve.Curve)

    # Can also pass an array-like as the basis.
    c = curve.from_lasio(l.curves['GR'], basis=list(l.curves['DEPT'].data))
    assert isinstance(c, curve.Curve)
