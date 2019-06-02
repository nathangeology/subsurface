# -*- coding: utf 8 -*-
"""
Python installation file.
"""
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


class CurveError(Exception):
    """
    Curve exception.
    """
    pass


class Curve(object):
    """
    Class representing a single log curve, such as a gamma-ray log.

    Stored internally as an xarray.DataArray, with the depth or time ('basis')
    as the coords of the xarray.
    """
    def __init__(self,
                 data,
                 basis,
                 domain='MD',
                 mnemonic='CURVE',
                 params=None,
                 ):
        """
        Curve instantiation.

        Args:
            data (ndarray): np.ndarray of the log curve.
            basis (ndarray): 1D array-like representing the locations (e.g. the
                depths) of the data samples.
            domain (str): the domain of the data, must be one of 'MD', 'TVD',
                'TVDSS', 'TVDKB', 'TWT', 'OWT'.
            mnemonic (str): the name of the log, usually called a 'mnemonic',
                used as the `name` of the `xarray.DataArray`.
            params (dict): More attributes of the curve. Can include 'units',
                'run', 'null', 'service_company', 'date', 'code'.
        """
        self.domain = domain
        self.units = params.get('units', None)
        self.run = params.get('run', 0)
        self.null = params.get('null', -999.25)
        self.service_company = params.get('service_company', None)
        self.date = params.get('date', None)
        self.code = params.get('code', None)

        self._xarray = xr.DataArray(data,
                                    name=mnemonic,
                                    coords=np.atleast_2d(basis),
                                    dims=[domain],
                                    )
        return

    def __getattr__(self, attr):
        """
        Passes attributes through to the xarray.DataArray object.
        """
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._xarray, attr)

    def __getitem__(self, item):
        """
        Get items with keys.
        """
        arr = self.__copy__()
        arr._xarray = arr._xarray.__getitem__(item)
        return arr

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def describe(self):
        """
        Return basic statistics about the curve.
        """
        stats = {}
        stats['samples'] = self.shape[0]
        stats['nulls'] = self[np.isnan(self)].shape[0]
        stats['mean'] = float(np.nanmean(self.real))
        stats['min'] = float(np.nanmin(self.real))
        stats['max'] = float(np.nanmax(self.real))
        return stats

    def __repr__(self):
        return f"Curve({self.mnemonic}, {self.size} samples, start={self.start})"

    def _repr_html_(self):
        """
        Jupyter Notebook magic repr function.
        """
        if self.size < 10:
            return np.ndarray.__repr__(self)

        attribs = self.__dict__.copy()

        # Header.
        row1 = '<tr><th style="text-align:center;" colspan="2">{} [{{}}]</th></tr>'
        rows = row1.format(self.mnemonic)
        rows = rows.format(attribs.pop('units', '&ndash;'))
        row2 = '<tr><td style="text-align:center;" colspan="2">{:.4f} : {:.4f} : {:.4f}</td></tr>'
        rows += row2.format(self.start, self.stop, self.step)

        # Curve attributes.
        s = '<tr><td><strong>{k}</strong></td><td>{v}</td></tr>'
        for k, v in attribs.items():
            if k == "_xarray": continue
            rows += s.format(k=k, v=v)

        # Curve stats.
        rows += '<tr><th style="border-top: 2px solid #000; text-align:center;" colspan="2"><strong>Stats</strong></th></tr>'
        stats = self.describe()
        s = '<tr><td><strong>samples (NaNs)</strong></td><td>{samples} ({nulls})</td></tr>'
        s += '<tr><td><strong><sub>min</sub> mean <sup>max</sup></strong></td>'
        s += '<td><sub>{min:.2f}</sub> {mean:.3f} <sup>{max:.2f}</sup></td></tr>'
        rows += s.format(**stats)

        # Curve preview.
        s = '<tr><th style="border-top: 2px solid #000;">Depth</th><th style="border-top: 2px solid #000;">Value</th></tr>'
        rows += s.format(self.start, self[0])
        s = '<tr><td>{:.4f}</td><td>{:.4f}</td></tr>'
        for depth, value in zip(self.basis[:3], self.values[:3]):
            rows += s.format(depth, value)
        rows += '<tr><td>⋮</td><td>⋮</td></tr>'
        for depth, value in zip(self.basis[-3:], self.values[-3:]):
            rows += s.format(depth, value)

        # Footer.
        # ...

        # End.
        html = '<table>{}</table>'.format(rows)
        return html

    @property
    def mnemonic(self):
        return self.name

    @property
    def basis(self):
        return self.coords[self.domain].values

    @property
    def start(self):
        return self.basis[0]

    @property
    def step(self):
        try:
            step = self.get_step(self.basis)
        except CurveError:
            step = None
        return step

    @property
    def stop(self):
        return self.basis[-1]

    @staticmethod
    def get_step(arr):
        diffs = np.diff(arr)
        if np.allclose(diffs[0], diffs):
            return np.asscalar(diffs[0])
        else:
            raise(CurveError("The step sizes are not equal."))

    def plot(self, ax=None, return_fig=False, **kwargs):
        """
        Plot a curve.

        Args:
            ax (Axes): A matplotlib Axes object.
            return_fig (bool): whether to return the matplotlib figure.
                Default False.
            kwargs: Arguments for ``ax.set()``

        Returns:
            ax. If you passed in an ax, otherwise None.
        """
        if ax is None:
            fig = plt.figure(figsize=(2, 10))
            ax = fig.add_subplot(111)
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
        elif return_fig:
            return fig
        else:
            return None


def from_lasio(curve,
               basis=None,
               start=None,
               stop=None,
               step=0.1524,
               run=-1,
               null=-999.25,
               service_company=None,
               date=None,
               ):
    """
    Makes a curve object from a lasio curve object and either a depth
    basis or start and step information.

    Args:
        curve (lasio CurveItem)
        basis (ndarray)
        start (float)
        stop (float)
        step (float)
        run (int): default: -1
        null (float): default: -999.25
        service_company (str): Optional.
        data (str): Optional.

    Returns:
        Curve. An instance of the class.
    """
    if basis is None:
        if start is not None and stop is not None:
            basis = np.arange(start, stop, step)
        else:
            m = "You must provide a basis, or a start and stop depth."
            raise CurveError(m)
    else:
        basis = np.array(basis)
        start = basis[0]
        stop = basis[-1]
        try:
            step = Curve.get_step(basis)
        except CurveError:
            step = None
        if curve.data.shape[0] != basis.size:
            step = None

    params = {}
    params['description'] = curve.descr
    params['units'] = curve.unit
    params['run'] = run
    params['null'] = null
    params['service_company'] = service_company
    params['date'] = date
    params['code'] = curve.API_code

    return Curve(curve.data, basis, mnemonic=curve.mnemonic, params=params)
