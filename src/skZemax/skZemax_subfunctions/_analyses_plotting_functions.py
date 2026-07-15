from __future__ import annotations

import matplotlib.cm as cmx
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.patches import Ellipse


def get_colormap(
    num_lines: int, should_reverse: bool = False, cmap_type="viridis"
) -> np.ndarray:
    """
    Gets an array of color values for plotting based on a colormap.

    :param num_lines:      number of lines you plan to plot
    :param should_reverse: If true will return the color map in inverse order
    :return:               colormap array
    """
    cNorm = mcolors.Normalize(vmin=0, vmax=num_lines - 1)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=plt.get_cmap(cmap_type))
    cmap = np.array([scalarMap.to_rgba(x) for x in range(num_lines)])
    if should_reverse:
        cmap = np.flipud(cmap)
    return cmap


def AnalysisPlotting_Footprint(
    self, in_footprint_xarray: xr.Dataset, ax: plt.Axes = None, color_by_idx: int = 0
) -> None:
    """
    This function reproduces a footprint plot using the output of :func:`Analyses_Footprint`

        Note that this footprint information does not capture any footprint descriptions beyond plotting an ellipse.
        Any more realistic ray-tracing is lost through the ZOS-API and needs to be examined directly in Zemax.

    :param in_footprint_xarray: Output of :func:`Analyses_Footprint`.
    :type in_footprint_xarray: xr.Dataset
    :param ax: axis to put the footprint plot on, defaults to None (makes a new plot)
    :type ax: plt.Axes, optional
    :param color_by_idx: How to color the footprint plot. 0=configuration, 1=wavelength, 2=field, defaults to 0
    :type color_by_idx: int, optional
    """
    if ax is None:
        plt.figure()
        ax = plt.gca()
    if color_by_idx == 0:
        cmap = get_colormap(in_footprint_xarray.conf.values.shape[0])
    elif color_by_idx == 1:
        cmap = get_colormap(in_footprint_xarray.wvln.values.shape[0])
    else:
        cmap = get_colormap(in_footprint_xarray.fld.values.shape[0])
    for cnfidx in in_footprint_xarray.conf.values:
        if color_by_idx == 0:
            edgecolor = cmap[cnfidx]
        for wvidx in in_footprint_xarray.wvln.values:
            if color_by_idx == 1:
                edgecolor = cmap[wvidx]
            for fldidx in in_footprint_xarray.fld.values:
                if color_by_idx == 2:
                    edgecolor = cmap[fldidx]
                at_settings = (
                    in_footprint_xarray.isel(conf=cnfidx)
                    .isel(wvln=wvidx)
                    .isel(fld=fldidx)
                )
                ellipse = Ellipse(
                    xy=(at_settings.x_cntr.item(), at_settings.y_cntr.item()),
                    width=np.abs(at_settings.x_max.item() - at_settings.x_min.item()),
                    height=np.abs(at_settings.y_max.item() - at_settings.y_min.item()),
                    edgecolor=edgecolor,
                    fc="None",
                    lw=2,
                )
                ax.add_patch(ellipse)
    ax.set_xlim(
        (in_footprint_xarray.x_min.min().item(), in_footprint_xarray.x_max.max().item())
    )
    ax.set_ylim(
        (in_footprint_xarray.y_min.min().item(), in_footprint_xarray.y_max.max().item())
    )
