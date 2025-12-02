import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import xarray as xr
import matplotlib.colors as mcolors
import matplotlib.cm as cmx

def get_colormap(num_lines: int, should_reverse: bool=False, cmap_type='viridis') -> np.ndarray:
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

def AnalysisPlotting_Footprint(self, in_footprint_xarray:xr.Dataset, ax:plt.Axes=None, color_by_idx:int=0)->None:
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
    elif color_by_idx==1:
        cmap = get_colormap(in_footprint_xarray.wvln.values.shape[0])  
    else:
        cmap = get_colormap(in_footprint_xarray.fld.values.shape[0])  
    for cnfidx in in_footprint_xarray.conf.values:
        if color_by_idx==0: edgecolor=cmap[cnfidx]
        for wvidx in in_footprint_xarray.wvln.values:
            if color_by_idx==1: edgecolor=cmap[wvidx]
            for fldidx in in_footprint_xarray.fld.values:
                if color_by_idx==2: edgecolor=cmap[fldidx]
                at_settings = in_footprint_xarray.isel(conf=cnfidx).isel(wvln=wvidx).isel(fld=fldidx)
                ellipse = Ellipse(xy=(at_settings.x_cntr.item(), at_settings.y_cntr.item()), width=np.abs(at_settings.x_max.item() - at_settings.x_min.item()), height=np.abs(at_settings.y_max.item() - at_settings.y_min.item()),edgecolor=edgecolor, fc='None', lw=2)
                ax.add_patch(ellipse)
    ax.set_xlim((in_footprint_xarray.x_min.min().item(), in_footprint_xarray.x_max.max().item()))
    ax.set_ylim((in_footprint_xarray.y_min.min().item(), in_footprint_xarray.y_max.max().item()))

def AnalysesPlotting_LinePlotByField(self, X_data: np.ndarray, 
                                     Y_data:np.ndarray,
                                     in_ax=None,
                                     line_style_label:str='',
                                     line_style:str='-',
                                     make_legend_labels:bool=True,
                                     line_colors:list=['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan'])->None:
    """
    Line plotting function for some set of data x-y data which is separated by field.

    If number of fields in data is more than the system fields, assumes the first index is diffraction limited data.

    :param X_data: x_axis data [angular fields, x_data]
    :type X_data: np.ndarray
    :param Y_data: x_axis data [angular fields, y_data]
    :type Y_data: np.ndarray
    :param in_ax: plotting axis (will make one if not given), defaults to None
    :type in_ax: _type_, optional
    :param line_style_label: if len(line_style_label)>0, will make label for type of line style, defaults to ''
    :type line_style_label: str, optional
    :param line_style: line style of plotted lines, defaults to '-'
    :type line_style: str, optional
    :param make_legend_labels: if will make any labels for a legend, defaults to True
    :type make_legend_labels: bool, optional
    :param line_colors: line colors for each field angle, defaults to ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    :type line_colors: _type_, optional
    """

    if in_ax is None:
        plt.figure()
        in_ax = plt.gca()
    extra_fields =  self.Fields_GetNumberOfFields() < X_data.shape[0]
    if extra_fields: # Move extra field(s) to last
        X_data = np.roll(X_data, self.Fields_GetNumberOfFields() - X_data.shape[0], axis=0)
        Y_data = np.roll(Y_data, self.Fields_GetNumberOfFields() - Y_data.shape[0], axis=0)
        if make_legend_labels:# Make label now to look nicer
            in_ax.plot([],[], line_style, color=line_colors[self.Fields_GetNumberOfFields()], label=r"Diff. Limited")
    for fieldidx in range(X_data.shape[0]):
        in_ax.plot(X_data[fieldidx, :], Y_data[fieldidx,:], line_style, color=line_colors[fieldidx])
        if make_legend_labels:
            if fieldidx < self.Fields_GetNumberOfFields():
                fld = self.Field_GetField(fieldidx+1)#index from 1 in Zemax
                in_ax.plot([],[], line_style, color=line_colors[fieldidx], label=r"X=%0.2f$^\circ$, Y=%0.2f$^\circ$" % (fld.get_X(), fld.get_Y()))
    if len(line_style_label)>0:
        in_ax.plot([],[], 'k'+line_style, label=line_style_label)

def AnalysesPlotting_FFTMTF(self, fftmtf_X, fftmtf_Y, in_ax=None, title:str=None)->None:
    """
    Just calls :func:`AnalysesPlotting_LinePlotByField` with explicit formatting for FFTMTF plot.

    :param fftmtf_X: x-data of MTF analysis
    :type fftmtf_X: _type_
    :param fftmtf_Y: y-data of MTF analysis
    :type fftmtf_Y: _type_
    :param in_ax: plotting axis (will make one if not given), defaults to None
    :type in_ax: _type_, optional
    :param title: Title of plot, defaults to None
    :type title: str, optional
    """

    if in_ax is None:
        plt.figure()
        in_ax = plt.gca()
    self.AnalysesPlotting_LinePlotByField(X_data                  = fftmtf_X,
                                              Y_data              = fftmtf_Y[:,:,0],
                                              in_ax               = in_ax,
                                              line_style_label    = 'Tangential',
                                              line_style          = '-',
                                              make_legend_labels  = True)
    self.AnalysesPlotting_LinePlotByField(X_data                  = fftmtf_X,
                                              Y_data              = fftmtf_Y[:,:,1],
                                              in_ax               = in_ax,
                                              line_style_label    = 'Sagittal',
                                              line_style          = '--',
                                              make_legend_labels  = False)
    in_ax.legend()
    in_ax.grid(True)
    in_ax.set_xlim((0, np.max(fftmtf_X)))
    in_ax.set_ylim((0, 1))
    in_ax.set_xlabel('Spatial Frequency in cycles per mm')
    in_ax.set_ylabel('Modulus of the OTF')
    if title is not None:
        in_ax.set_title(title)
