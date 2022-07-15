from ..utilities import *
from ....imports import *

__all__ = ["plot_median_lightcurve"]


def plot_median_lightcurve(self, **kw):
    """
    Plot the weighted median lightcurve as a function of time.

    Parameters
    ----------
    **kw : dict
        Additional keywords will be passed onward to the helper
        function `._scatter_timelike_or_wavelike`. Please see its
        docstrings for options about plot appearance and layout.
    """
    y = self.get_median_lightcurve()
    self._scatter_timelike_or_wavelike(
        x=self.time,
        y=y,
        ylabel=f"Flux ({_get_unit_string(y)})",
        **kw,
    )
