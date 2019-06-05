# -*- coding: utf-8 -*-
"""
A seismic object and data loading functions.
"""
import segyio
import xarray as xr
import pint

from .xarray import *
from .units import units


class SeismicError(Exception):
    """
    Seismic exception.
    """
    pass


class Seismic(object):
    def __init__(self, data, units='dimensionless', *args, **kwargs):
        """Seismic data object based on xarray.DataArray.

        Args:
            data (Array): np.ndarray of the seismic cube / section.

        TODO
            Figure out how to use pint's `dimensionless` unit, instead of the
            string `"dimensionless"`.
        """
        self._xarray = xr.DataArray(data, *args, **kwargs)
        self._units = self._xarray.attrs.get('units', units)

        return

    def set_units(self, units):
        self._units = units
        return

    def convert_units(self, units):
        self._units = self._units.to(units)
        return

    @property
    def units(self):
        return self._units

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._xarray, attr)

    # def __getitem__(self, item):
    #     if isinstance(item, str):
    #         return self._xarray._getitem_coord(item)

    #     # Preserve coordinates.
    #     cp = list(self._xarray.coords.items())  # parent coordinates
    #     coords = [(cp[i]) for i, it in enumerate(item) if not type(it) == int]
    #     nits = self._units
    #     return Seismic(self._xarray[item].data, coords=coords, units=nits)

    def __getitem__(self, item):
        """
        Get items with keys.

        TODO
            We are probably going to pay for this in memory.
        """
        arr = self.__copy__()
        arr._xarray = arr._xarray.__getitem__(item)
        return arr

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __repr__(self):
        return f"Seismic(shape={self.shape}, units={self.units})"

    @property
    def n_shp(self):
        return len(self._xarray.data.shape)

    def to_segy(self, filepath: str) -> None:
        """Write given Seismic to SEGY file using segyio.tools.from_array().

        Args:
            filepath (str): Filepath for SEGY file.
        """
        segyio.tools.from_array(filepath, self._xarray.data)


def from_segy(filepath:str, coords=None, units='dimensionless'):
    """Create a Seismic data object from a SEGY file.

    Args:
        filepath (str): Filepath to the SEGY file.

    Returns:
        Seismic: Seismic data object based on xarray.DataArray.
    """
    with segyio.open(filepath) as sf:
        sf.mmap()  # memory mapping
        xlines = sf.xlines
        ilines = sf.ilines
        samples = sf.samples
        header = sf.bin

    if not coords:
        coords = [
            ("ilines", ilines), 
            ("xlines", xlines),
            ("samples", samples)
        ]

    cube = segyio.tools.cube(filepath)
    seismic = Seismic(cube, coords=coords, units=units)
    seismic.header = header
    return seismic
