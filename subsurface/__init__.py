# -*- coding: utf-8 -*-
from .curve import Curve
from .seismic import Seismic
from .units import units


__all__ = [
           'Curve',
           'Seismic',
           'units',
           'xarray',
          ]


__version__ = "unknown"
try:
    from ._version import __version__
except ImportError:
    pass
