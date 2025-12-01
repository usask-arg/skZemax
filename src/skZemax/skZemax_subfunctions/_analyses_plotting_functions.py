import numpy as np
import matplotlib.pyplot as plt

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
