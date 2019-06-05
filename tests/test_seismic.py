import pytest
import xarray.testing
import numpy.testing
import numpy as np
import segyio

import subsurface
from subsurface import seismic
from subsurface import units


@pytest.fixture(scope="module")
def seismic_cube():
    """Benchmark Seismic object."""
    # coords = [{"x": np.arange(10)}, {"y": np.arange(10)}, {"z": np.arange(100)}]
    coords = [("x", np.arange(10)), ("y", np.arange(10)), ("z", np.arange(100))]
    cube = segyio.tools.cube("tests/data/test.segy")
    # seis = from_segy("tests/data/test.segy")
    return seismic.Seismic(cube, coords=coords)


def test_from_segy():
    """Test creating Seismic instance from SEGY file."""
    s = seismic.from_segy("tests/data/test.segy")
    assert type(s) == seismic.Seismic
    assert type(s[0]) == seismic.Seismic
    assert str(s) == "Seismic(shape=(10, 10, 100), units=dimensionless)"


def test_getitem(seismic_cube):
    # assert type(s[0]) == seismic.Seismic  # Fails here for some reason
    assert seismic_cube.loc[:, :, 50].shape == (10, 10)
    assert seismic_cube.loc[:, :, 10:19].shape == (10, 10, 10)


def test_seismic_units(seismic_cube):
    """Test creating Seismic instance from SEGY file."""
    assert seismic_cube.units == 'dimensionless'  # Would rather check for units.dimensionless
    seismic_cube.set_units(units.km/units.s)
    assert seismic_cube.units == units.km/units.s

# def test_seismic_unit_conversion():
#     """Test creating Seismic instance from SEGY file."""
#     seismic = from_segy("tests/data/test.segy")
#     seismic_mod = from_segy("tests/data/test.segy")
#     seismic.set_units(units.km/units.s)
#     seismic_mod.set_units(units.km/units.s)
#     #assert xarray.testing.assert_equal(seismic, seismic_mod)
#     numpy.testing.assert_array_equal(seismic.values,seismic_mod.values)
#     seismic_mod.convert_units(units.m / units.s)
#     a, b = seismic.values.copy(), seismic_mod.values.copy()
#     b /= 1e3
#     numpy.testing.assert_allclose(a, b, rtol=1e-6)
#     seismic_mod.convert_units(units.km / units.s)
#     b = seismic_mod.values.copy()
#     numpy.testing.assert_allclose(a, b, rtol=1e-6)
