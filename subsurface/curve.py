# -*- coding: utf 8 -*-
"""
Python installation file.
"""
import warnings

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


class CurveError:
    pass


class Curve(object):

    def __init__(self, data, basis=None):
        """Seismic data object based on xarray.DataArray.

        Args:
            data (Array): np.ndarray of the log curve.
        """
        self._xarray = xr.DataArray(data, coords=[basis], dims=['depth'], name='data')
        return

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._xarray, attr)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._xarray._getitem_coord(item)

        # Preserve coordinates.
        cp = list(self._xarray.coords.items())  # parent coordinates
        coords = [(cp[i]) for i, it in enumerate(item) if not type(it) == int]
        return Curve(self._xarray[item].data, coords=coords)

    def _repr_html_(self):
        """
        Jupyter Notebook magic repr function.
        """
        if self.size < 10:
            return np.ndarray.__repr__(self)
        attribs = self.__dict__.copy()

        # Header.
        row1 = '<tr><th style="text-align:center;" colspan="2">{} [{{}}]</th></tr>'
        rows = row1.format(attribs.pop('mnemonic'))
        rows = rows.format(attribs.pop('units', '&ndash;'))
        row2 = '<tr><td style="text-align:center;" colspan="2">{:.4f} : {:.4f} : {:.4f}</td></tr>'
        rows += row2.format(attribs.pop('start'), self.stop, attribs.pop('step'))

        # Curve attributes.
        s = '<tr><td><strong>{k}</strong></td><td>{v}</td></tr>'
        for k, v in attribs.items():
            rows += s.format(k=k, v=v)

        # Curve stats.
        rows += '<tr><th style="border-top: 2px solid #000; text-align:center;" colspan="2"><strong>Stats</strong></th></tr>'
        stats = self.get_stats()
        s = '<tr><td><strong>samples (NaNs)</strong></td><td>{samples} ({nulls})</td></tr>'
        s += '<tr><td><strong><sub>min</sub> mean <sup>max</sup></strong></td>'
        s += '<td><sub>{min:.2f}</sub> {mean:.3f} <sup>{max:.2f}</sup></td></tr>'
        rows += s.format(**stats)

        # Curve preview.
        s = '<tr><th style="border-top: 2px solid #000;">Depth</th><th style="border-top: 2px solid #000;">Value</th></tr>'
        rows += s.format(self.start, self[0])
        s = '<tr><td>{:.4f}</td><td>{:.4f}</td></tr>'
        for depth, value in zip(self.basis[:3], self[:3]):
            rows += s.format(depth, value)
        rows += '<tr><td>⋮</td><td>⋮</td></tr>'
        for depth, value in zip(self.basis[-3:], self[-3:]):
            rows += s.format(depth, value)

        # Footer.
        # ...

        # End.
        html = '<table>{}</table>'.format(rows)
        return html

    def plot(self, ax=None, **kwargs):
        """
        Plot a curve.

        Args:
            ax (ax): A matplotlib axis.
            return_fig (bool): whether to return the matplotlib figure.
                Default False.
            kwargs: Arguments for ``ax.set()``

        Returns:
            ax. If you passed in an ax, otherwise None.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(2, 10))
            return_ax = False
        else:
            return_ax = True

        ax.plot(self, self.basis, **kwargs)
        ax.set_title(self.mnemonic)  # no longer needed
        ax.set_xlabel(self.units)

        labels = ax.get_xticklabels()
        for label in labels:
            label.set_rotation(90)

        ax.set_ylim([self.stop, self.start])
        ax.grid('on', color='k', alpha=0.33, lw=0.33, linestyle='-')

        if return_ax:
            return ax
        else:
            return None


def from_las():
    """
    Instantiate a Curve object from a SEG-Y file.
    """
    pass


def from_lasio_curve(cls, curve,
                     depth=None,
                     basis=None,
                     start=None,
                     stop=None,
                     step=0.1524,
                     run=-1,
                     null=-999.25,
                     service_company=None,
                     date=None):
    """
    Makes a curve object from a lasio curve object and either a depth
    basis or start and step information.

    Args:
        curve (ndarray)
        depth (ndarray)
        basis (ndarray)
        start (float)
        stop (float)
        step (float): default: 0.1524
        run (int): default: -1
        null (float): default: -999.25
        service_company (str): Optional.
        data (str): Optional.

    Returns:
        Curve. An instance of the class.
    """
    data = curve.data
    unit = curve.unit

    # See if we have uneven sampling.
    if depth is not None:
        d = np.diff(depth)
        if not np.allclose(d - np.mean(d), np.zeros_like(d)):
            # Sampling is uneven.
            m = "Irregular sampling in depth is not supported. "
            m += "Interpolating to regular basis."
            warnings.warn(m)
            step = np.nanmedian(d)
            start, stop = depth[0], depth[-1]+0.00001  # adjustment
            basis = np.arange(start, stop, step)
            data = np.interp(basis, depth, data)
        else:
            step = np.nanmedian(d)
            start = depth[0]

    # Carry on with easier situations.
    if start is None:
        if basis is not None:
            start = basis[0]
            step = basis[1] - basis[0]
        else:
            raise CurveError("You must provide a basis or a start depth.")

    if step == 0:
        if stop is None:
            raise CurveError("You must provide a step or a stop depth.")
        else:
            step = (stop - start) / (curve.data.shape[0] - 1)

    params = {}
    params['mnemonic'] = curve.mnemonic
    params['description'] = curve.descr
    params['start'] = start
    params['step'] = step
    params['units'] = unit
    params['run'] = run
    params['null'] = null
    params['service_company'] = service_company
    params['date'] = date
    params['code'] = curve.API_code

    return cls(data, params=params)
