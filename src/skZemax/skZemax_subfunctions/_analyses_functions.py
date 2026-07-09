from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import xarray as xr
from box import Box

from skZemax.skZemax_subfunctions._c_print import c_print as cp
from skZemax.skZemax_subfunctions._LDE_functions import (
    ZOSAPI_Editors_LDE_ILDERow,
    _convert_raw_surface_input_,
)
from skZemax.skZemax_subfunctions._wavelength_functions import (
    ZOSAPI_SystemData_IWavelength,
    _convert_raw_wavelength_input_,
)
from skZemax.skZemax_subfunctions._field_functions import (
    ZOSAPI_SystemData_IField,
    _convert_raw_field_input_,
)
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import (
    __LowLevelZemaxStringCheck__,
    _CheckIfStringValidInDir_,
)

type ZOSAPI_Analysis_Data_IA = object  # <- ZOSAPI.Analysis.IA_ # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Analysis_Data_IAR = object  # <- ZOSAPI.Analysis.Data.IAR_ # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Analysis_Data_IAS = object  # <- ZOSAPI.Analysis.Settings.IAS_ # The actual module is referenced by the base PythonStandaloneApplication class.

def _Analysis_GeneralDataSeriesReader_(self, results:ZOSAPI_Analysis_Data_IAR):
    """Germanized worker for reading X and Y data from data series returned from an analysis GetResults() call.

    :param results: The return of an analysis GetResults() call.
    :type results: ZOSAPI_Analysis_Data_IAR
    """
    xar = []
    yar = []
    for seriesNum in range(results.NumberOfDataSeries):
        data = results.GetDataSeries(seriesNum)
        xRaw = data.XData.Data
        yRaw = data.YData.Data
        xar.append(np.array(tuple(xRaw)))
        try:
            yar.append(
                np.array(
                    np.asarray(tuple(yRaw)).reshape(
                        data.YData.Data.GetLength(0), data.YData.Data.GetLength(1)
                    )
                )
            )
        except Exception:
            yar.append(np.array(np.asarray(tuple(yRaw))))
    return np.array(xar), np.array(yar)

def _Analysis_GeneralDataGridReader_(self, results:ZOSAPI_Analysis_Data_IAR):
    """Germanized worker for reading grid data from data returned from an analysis GetResults() call.

    :param results: The return of an analysis GetResults() call.
    :type results: ZOSAPI_Analysis_Data_IAR
    """
    gar = []
    xar = []
    yar = []
    for gridNum in range(results.NumberOfDataGrids):
        data = results.GetDataGrid(gridNum)
        gRaw = data.Values
        dx = data.Dx
        dy = data.Dy
        xmin = data.MinX
        ymin = data.MinY
        xar.append(xmin + np.arange(data.Nx) * dx)
        yar.append(ymin + np.arange(data.Ny) * dy)
        gar.append(np.array(tuple(gRaw)).reshape(data.Ny, data.Nx))
    return np.array(gar), np.array(xar), np.array(yar)

def _Analysis_GetZOSObjectAndSettings_(
    self, analysis: str
) -> tuple[ZOSAPI_Analysis_Data_IA, ZOSAPI_Analysis_Data_IAS, str]:
    """
    Worker function which looks up the specified analysis object and settings - which some condition checking.
    A tuple of None values is returned if the analysis is not recognized, or not applicable to the type of sequential mode.

    :param analysis: The name of the analysis to perform. See output of :func:`Analyses_GetNamesOfAllAnalyses` for names.
    :type analysis: str
    :return: OSAPI.Analysis.Data object, the ZOSAPI.Analysis.Settings object, and the ZOS-API name of the specified analysis.
    :rtype: tuple[ZOSAPI_Analysis_Data_IA, ZOSAPI_Analysis_Data_IAS, str]
    """
    analysis_enum = _CheckIfStringValidInDir_(
        self, self.ZOSAPI.Analysis.AnalysisIDM, analysis
    )
    if analysis_enum is None:
        return None, None, None
    analysis_obj = self.TheSystem.Analyses.New_Analysis(analysis_enum)
    if analysis_obj is None:
        if self._verbose:
            cp(
                f"!@ly!@_Analysis_GetZOSObjectAndSettings_ :: Analysis [!@lm!@{analysis_enum!s}!@ly!@] is not applicable to [!@lm!@{self.System_GetMode()}!@ly!@] mode."
            )
        return None, None, None
    analysis_settings_obj = analysis_obj.GetSettings()
    if analysis_settings_obj is None:
        del analysis_obj
        analysis_obj = None
        if self._verbose:
            cp(
                f"!@ly!@_Analysis_GetZOSObjectAndSettings_ :: Analysis [!@lm!@{analysis_enum!s}!@ly!@] is not applicable to [!@lm!@{self.System_GetMode()}!@ly!@] mode."
            )
        return None, None, None
    return analysis_obj, analysis_settings_obj, str(analysis_enum)


def _Analysis_SetZOSObjectSettingsByDict_(
    self,
    analysis_settings: dict|Box,
    analysis_settings_obj: ZOSAPI_Analysis_Data_IAS,
    analysis_enum: str,
) -> None:
    """
    A worker function which will set analysis settings through the ModifySettings() scheme documented in Section 10.2.14.92. MODIFYSETTINGS (keywords).
    This is done by making, configuring, and then loading a configuration file. This config file method seems to be the only robust way to configure analysis settings.

    :param analysis_settings: A python dictatory to adjust settings of the analysis. Formatted as dict[MODIFYSETTINGS KEYWORD] = str(value), defaults to None
    :type analysis_settings: dict|Box
    :param analysis_settings_obj: Analysis settings object
    :type analysis_settings_obj: ZOSAPI_Analysis_Data_IAS
    :param analysis_enum: the ZOS-API name of the specified analysis
    :type analysis_enum: str
    """
    if analysis_settings is not None:
        # Set all settings through the configuration file "ModifySettings()" function.
        cfgFile = self.Utilities_ConfigFilesDir() + os.sep + analysis_enum + ".CFG"
        analysis_settings_obj.SaveTo(cfgFile)
        [
            analysis_settings_obj.ModifySettings(cfgFile, x, str(analysis_settings[x]))
            for x in analysis_settings
        ]
        analysis_settings_obj.LoadFrom(cfgFile)


def _Analysis_SetZOSObjectSettingsByBinaryAlteration_(
    self,
    analysis_settings: np.ndarray,
    analysis_settings_obj: ZOSAPI_Analysis_Data_IAS,
    analysis_enum: str,
) -> None:
    """
    A worker function to set a analysis configuration file through direct modification.

    Disclaimer: I worked out this hack thanks to seeing it in ZOSpy.

    :param analysis_settings: An integer array of analysis settings. See descriptions of :func:`Analyses_RunAnalysesAndGetResults`.
    :type analysis_settings: np.ndarray
    :param analysis_settings_obj: The settings object of the analysis.
    :type analysis_settings_obj: ZOSAPI_Analysis_Data_IAS
    :param analysis_enum: the ZOS-API name of the specified analysis
    :type analysis_enum: str
    """
    if analysis_settings is not None:
        cfgFile = self.Utilities_ConfigFilesDir() + os.sep + str(analysis_enum) + ".CFG"
        analysis_settings_obj.SaveTo(cfgFile)
        cfgFile_path = Path(cfgFile)
        settings_bytestring = cfgFile_path.read_bytes()
        settings_bytearray = bytearray(settings_bytestring)
        # I believe byte indices 0-19 is effectively header information. Analysis settings begin at index 20 and increments by 4 per option.
        for idx, binidx in enumerate(
            np.arange(20, 20 + analysis_settings.shape[0] * 4, 4)
        ):
            settings_bytearray[binidx] = analysis_settings[idx]
        cfgFile_path.write_bytes(settings_bytearray)
        del cfgFile_path
        cfgFile_path = None
        analysis_settings_obj.LoadFrom(cfgFile)


def Analyses_GetNamesOfAllAnalyses(self, print_to_console: bool = False) -> list:
    """
    This function is simply for user convenance to look up the ZOS-API names of all analysis types.
    This can be useful to look up what one may want to code as input to functions like :func:`Analyses_RunAnalysesAndGetResults`.


    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :return: A list of the names of all analyses types the ZOS-API knows.
    :rtype: list
    """
    analyses_types = __LowLevelZemaxStringCheck__(
        self, in_obj=self.ZOSAPI.Analysis.AnalysisIDM
    )
    if print_to_console:
        cp("\n!@lg!@Analyses_GetNamesOfAllAnalyses :: Names of Analyses:")
        [cp("   !@lm!@" + str(x)) for x in analyses_types]
        cp("\n")
    return analyses_types


def Analyses_RunAnalysesAndGetResults(
    self, analysis: str, analysis_settings: dict | Box | np.ndarray[int] = None
) -> ZOSAPI_Analysis_Data_IAR:
    """
    This is a generalized function to run a Zemax analysis on the optical system.
    It is intended to facilitate users - with some familiarity with the ZOS-API - to support their own analysis code
    if a wrapper function for the analysis doesn't exist, or if the user would like more direct access to the results.
    User ZOS-API familiarity is expected to be on the topics of the analysis setting documentation, and processing
    the output of a `GetResults()` call for the analysis (which differs based on the type of analysis being done).

        It is recommended to use a wrapper function, such as :func:`Analyses_FFTMTF`, for robustness and ease of use.

    Note that this function will adjust all settings through analysis configuration (.CFG) files rather than direct property assignment.
    The reason for this is that much of the direct assignment through the ZOS-API does not work or was never supported to begin with.

    Analysis settings are intended by ZOI-API to be adjusted through a configuration file with a `ModifySettings()` function call.
    If analysis settings are provided to this function as a python dictionary formatted as `dict[MODIFYSETTINGS KEYWORD] = str(value)`, this method is attempted.

        Documentation on the analysis settings - and the keys to provide in the settings dictionary - can be found in the pdf help file
        in Section 10.2.14.92. MODIFYSETTINGS (keywords).

    There are analysis settings which are either simply not documented by ZOI-API within Section 10.2.14.92, or support for them simply doesn't exist through the ZOS-API.
    In this case it is possible to directly adjust the binary values of the configuration file to implement the settings you want.

        In this case supply a numpy array of integer values for these settings. Since these are undocumented it may take some trial and error will to work out what to enter.
        However, a fairly reliable way is to look at the settings interface for the analysis in the typical Zemax application user interface.

        The order of the settings to enter into the np.ndarray will *typically* be the order of the options in the settings menu - starting with each option in the left most column of settings,
        then each in the next column, and so on all the way to the right most column.

        Values are (*typically*) 1 meaning enabled and 0 meaning disabled - or in the case of multiple options, an integer value selecting the item in the user interface's drop down menu for that option.

        As an example: For the Cardinal Point Data Analysis the settings menu in the typical Zemax application user interface looks like:

        +========================+============+
        | First Surface   | Wavelength        |
        +------------------------+------------+
        | Last Surface    | Orientation       |
        +========================+============+

        Where applicable, the menu options are sorted by index. Other (such as orientation here) have the options as: [Y-Z, X-Y]. Therefore, for settings

        - First Surface = second in the system
        - Last Surface  = fourth in the system
        - Wavelength    = third in the system
        - Orientation   = 'Y-Z'

        The array this function wants will be: [2, 4, 3, 1].

        ... and yes, I know this sucks ... one of the reasons for the wrapper functions in skZemax.

    :param analysis: The name of the analysis to perform. See output of :func:`Analyses_GetNamesOfAllAnalyses` for names.
    :type analysis: str
    :param analysis_settings: User settings of the analysis. See descriptions above, defaults to None
    :type analysis_settings: Union[dict, np.ndarray[int]], optional
    :return: The output of the analysis `GetResults()` function call.
    :rtype: ZOSAPI_Analysis_Data_IAR
    """
    analysis_obj, analysis_settings_obj, analysis_enum = (
        self._Analysis_GetZOSObjectAndSettings_(analysis=analysis)
    )
    if analysis_obj is None or analysis_settings_obj is None:
        return None
    if analysis_settings is not None and isinstance(analysis_settings, dict):
        self._Analysis_SetZOSObjectSettingsByDict_(
            analysis_settings=analysis_settings,
            analysis_settings_obj=analysis_settings_obj,
            analysis_enum=analysis_enum,
        )
    elif analysis_settings is not None and isinstance(analysis_settings, np.ndarray):
        self._Analysis_SetZOSObjectSettingsByBinaryAlteration_(
            analysis_settings=analysis_settings,
            analysis_settings_obj=analysis_settings_obj,
            analysis_enum=analysis_enum,
        )
    elif analysis_settings is not None:
        if self._verbose:
            cp(
                "!@ly!@Analyses_RunAnalysesAndGetResults :: WARNING :: Settings supplied but format not recognized. Nothing configured."
            )
    if self._verbose:
        cp(
            f"!@lg!@Analyses_RunAnalysesAndGetResults :: Running analysis [!@lm!@{analysis_enum!s}!@lg!@] ..."
        )
    analysis_obj.ApplyAndWaitForCompletion()
    if self._verbose:
        cp("!@lg!@Analyses_RunAnalysesAndGetResults :: Done.")
    return analysis_obj.GetResults()


def Analyses_ReportSystemPrescription(
    self, save_textfile_path: str | None = None
) -> list:
    """
     Constructs the prescription report of the optical system. This is returned as text information which can be saved in a .txt file.

    :param save_textfile_path:save_textfile_path: Full absolute .txt file path to save prescription data text file, defaults to None (no custom saving)
    :type save_textfile_path: str, optional
    :return: A list where each element is a line of the prescription report.
    :rtype: list
    """
    if save_textfile_path is None:
        save_path = (
            self.Utilities_AnalysesFilesDir() + os.sep + "PrescriptionDataSettings.txt"
        )
    else:
        if save_textfile_path[-4:] != ".txt":
            save_textfile_path += ".txt"
        save_path = save_textfile_path
    result = self.Analyses_RunAnalysesAndGetResults(analysis="PrescriptionDataSettings")
    result.GetTextFile(save_path)
    with open(save_path, errors="replace") as file:
        content = file.read()
    return [
        x for x in content.replace("\x00", "").strip("ÿþ").split("\n") if len(x) > 0
    ]


def Analyses_ReportSurfacePrescription(
    self,
    in_Surface: int | ZOSAPI_Editors_LDE_ILDERow,
    save_textfile_path: str | None = None,
) -> list:
    """
    Constructs the prescription report of a sequential (LDE) surface in optical system. This is returned as text information which can be saved in a .txt file.

    :param in_Surface: The surface to analyze as an LDE surface object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param save_textfile_path: Full absolute .txt file path to save prescription data text file, defaults to None (no custom saving)
    :type save_textfile_path: str, optional
    :return: A list where each element is a line of the prescription report.
    :rtype: list
    """
    if save_textfile_path is None:
        save_path = (
            self.Utilities_AnalysesFilesDir() + os.sep + "SurfaceDataSetting.txt"
        )
    else:
        if save_textfile_path[-4:] != ".txt":
            save_textfile_path += ".txt"
        save_path = save_textfile_path
    result = self.Analyses_RunAnalysesAndGetResults(
        analysis="SurfaceDataSetting",
        analysis_settings=np.array(
            [self._convert_raw_surface_input_(in_Surface, return_index=True)]
        ),
    )
    result.GetTextFile(save_path)
    with open(save_path, errors="replace") as file:
        content = file.read()
    return [
        x for x in content.replace("\x00", "").strip("ÿþ").split("\n") if len(x) > 0
    ]


@staticmethod
def Analyses_ExtractSectionOfTextFile(
    in_file: list | str, start_marker: str | None = None, end_marker: str | None = None
) -> list:
    """
    This is just a convince function which will extract only a section of a text file.
    Typically these text files are the output made by skZemax Analyses function (but this function is agnostic to where the text file came form).
    For instance, this can be useful for selection of only a part of an optical prescription.

    See Example 03.

    :param in_file: Can be a list where each element is a line of a loaded text file, or a string to a path to load the text file.
    :type in_file: Union[list, str]
    :param start_marker: The starting marker denoting when to begin selecting a part of the text, defaults to None (start at the beginning)
    :type start_marker: str, optional
    :param end_marker: The ending marker denoting when to stop selecting a part of the text, defaults to None (goes to the end)
    :type end_marker: str, optional
    :return: a list where each element is a line of the (sectioned) text file.
    :rtype: list
    """
    if isinstance(in_file, str):
        with open(in_file, errors="replace") as file:
            content = file.read()
        in_file = [
            x for x in content.replace("\x00", "").strip("ÿþ").split("\n") if len(x) > 0
        ]
    section = []
    inside = start_marker is None
    for line in in_file:
        if start_marker.lower() in line.lower():
            inside = True
            continue
        if inside and end_marker is not None and end_marker.lower() in line.lower():
            break
        if inside:
            section.append(line)
    return section


def Analyses_Footprint(
    self, in_Surface: int | ZOSAPI_Editors_LDE_ILDERow, delete_vignetted: bool = False
) -> xr.Dataset:
    """
    Produces a footprint diagram.

    ZOI-API interface for the footprint analysis is extremely limited. Data is only saved to a textfile of:
    - Ray X Minimum
    - Ray X Maximum
    - Ray Y Minimum
    - Ray Y Maximum
    - Maximum Radius
    - Ray X Center
    - Ray Y Center
    - Ray X Half Width
    - Ray Y Half Width
    - Wavelength
    as an aggregate of all the wavelengths/fields/configurations being looked at.

    Note that this information does not capture any footprint descriptions beyond plotting an ellipse.
    Any more realistic ray-tracing is lost through the ZOS-API and needs to be examined directly in Zemax - or run your own ray trace using functions like :func:`LDE_RunRayTrace`.

    This function loops through all fields/wavelengths/configurations individually and records the above information in an xarray for user analysis.
    See :func:`AnalysisPlotting_Footprint`.

    :param in_Surface: The surface to study. Can be an index or LDE surface object.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param delete_vignetted: If True wil delete vignetted ray, defaults to False
    :type delete_vignetted: bool, optional
    """
    CURRENT_VERBOSE = bool(self._verbose)
    self._verbose = False
    CURRENT_CONFIG = int(self.MCE_GetCurrentConfig())
    save_path = self.Utilities_AnalysesFilesDir() + os.sep + "Footprint.txt"
    blank_array = (
        np.ones(
            (
                self.MCE_GetNumberOfConfigs(),
                self.Wavelength_GetNumberOfWavelengths(),
                self.Fields_GetNumberOfFields(),
            )
        )
        * np.nan
    )
    out = xr.Dataset(
        {
            "x_min": (("conf", "wvln", "fld"), np.copy(blank_array)),
            "x_max": (("conf", "wvln", "fld"), np.copy(blank_array)),
            "y_min": (("conf", "wvln", "fld"), np.copy(blank_array)),
            "y_max": (("conf", "wvln", "fld"), np.copy(blank_array)),
            "rad_max": (("conf", "wvln", "fld"), np.copy(blank_array)),
            "x_cntr": (("conf", "wvln", "fld"), np.copy(blank_array)),
            "y_cntr": (("conf", "wvln", "fld"), np.copy(blank_array)),
            "x_half": (("conf", "wvln", "fld"), np.copy(blank_array)),
            "y_half": (("conf", "wvln", "fld"), np.copy(blank_array)),
            "wavelength_um": (("conf", "wvln", "fld"), np.copy(blank_array)),
        },
        coords={
            "configuration_index": (
                "conf",
                np.array(np.arange(1, self.MCE_GetNumberOfConfigs() + 1, 1)),
            ),
            "wavelength_index": (
                "wvln",
                np.array(np.arange(1, self.Wavelength_GetNumberOfWavelengths() + 1, 1)),
            ),
            "field_index": (
                "fld",
                np.array(np.arange(1, self.Fields_GetNumberOfFields() + 1, 1)),
            ),
        },
    )
    out.attrs = {
        "Surface": _convert_raw_surface_input_(
            self, in_surface=in_Surface, return_index=True
        )
    }
    footprint_options = {}
    footprint_options["FOO_SURFACE"] = int(out.attrs["Surface"])
    footprint_options["FOO_RAYDENSITY"] = 0  # Ring pattern
    footprint_options["FOO_DELETEVIGNETTED"] = bool(delete_vignetted)
    if CURRENT_VERBOSE:
        cp(
            "!@lg!@Analyses_Footprint :: Running analysis [!@lm!@{}!@lg!@] ...".format(
                "FootprintSettings"
            )
        )
    for confidx in np.arange(1, self.MCE_GetNumberOfConfigs() + 1, 1):
        self.MCE_SetActiveConfig(int(confidx))
        for wvidx in np.arange(1, self.Wavelength_GetNumberOfWavelengths() + 1, 1):
            for fldidx in np.arange(1, self.Fields_GetNumberOfFields() + 1, 1):
                footprint_options["FOO_FIELD"] = fldidx
                footprint_options["FOO_WAVELENGTH"] = wvidx
                result = self.Analyses_RunAnalysesAndGetResults(
                    analysis="Footprint", analysis_settings=footprint_options
                )
                result.GetTextFile(save_path)
                with open(save_path) as file:
                    content = file.read()
                content = [
                    x
                    for x in content.replace("\x00", "").strip("ÿþ").split("\n")
                    if len(x) > 0
                ]
                try:
                    out.attrs["File"] = content[1]
                    out.attrs["Date"] = content[3]
                    out.x_min[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[6].split("\t")[-1].strip(" ")
                    )
                    out.x_max[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[7].split("\t")[-1].strip(" ")
                    )
                    out.y_min[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[8].split("\t")[-1].strip(" ")
                    )
                    out.y_max[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[9].split("\t")[-1].strip(" ")
                    )
                    out.rad_max[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[10].split("\t")[-1].strip(" ")
                    )
                    out.x_cntr[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[11].split("\t")[-1].strip(" ")
                    )
                    out.y_cntr[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[12].split("\t")[-1].strip(" ")
                    )
                    out.x_half[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[13].split("\t")[-1].strip(" ")
                    )
                    out.y_half[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[14].split("\t")[-1].strip(" ")
                    )
                    out.wavelength_um[confidx - 1, wvidx - 1, fldidx - 1] = float(
                        content[15].split("\t")[-1].strip(" ").split(" ")[0]
                    )
                except Exception:
                    pass
    if CURRENT_VERBOSE:
        cp("!@lg!@Analyses_Footprint :: Done.")
    # Reset to settings before loop
    self._verbose = CURRENT_VERBOSE
    self.MCE_SetActiveConfig(int(CURRENT_CONFIG))
    return out



def Analyses_FFTMTF(
    self,
    wavelength: int | float | ZOSAPI_SystemData_IWavelength = 0,
    field: int | ZOSAPI_SystemData_IField = 0,
    surface: int | ZOSAPI_Editors_LDE_ILDERow = 0,
    sample_size: str = "256x256",
    max_freq: float = 0,
    use_polarization: bool = True,
) -> xr.Dataset:
    """
    Get the (sequential) FFT MTF of the system.

    TODO: Support multipule MCE configurations

    :param wavelength: System wavelength (as index, microns, or object) to do the MTF on. An int of 0 selects all all wavelengths, Defaults to 0.
    :type wavelength: int | float | ZOSAPI_SystemData_IWavelength, optional
    :param field: System field (index of object) to do the MTF on.  An int of 0 selects all fields, defaults to 0
    :type field: int | ZOSAPI_SystemData_IField, optional
    :param surface: System surface (index or object) to do the MTF on. An int of 0 selects the image surface, defaults to 0
    :type surface: int, optional
    :param sample_size: '32x32', '64x64', '128x128', '256x256', '512x512', '1024x1024', '2048x2048',  '4096x4096',  '8192x8192', '16384x16384', defaults to '256x256'
    :type sample_size: str, optional
    :param max_freq: Max frequency of the analysis, 0 allows Zemax to select it, defaults to 0
    :type max_freq: float, optional
    :param use_polarization: Use polarization, defaults to True
    :type use_polarization: bool, optional
    :return: The x and y data of the FFTMTF analysis.
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    # convert wavelength/fields/surface
    if not (isinstance(wavelength, int) and wavelength == 0):
        wavelength = self._convert_raw_wavelength_input_(wavelength, return_index=True)
    if not (isinstance(field, int) and field == 0):
        field = self._convert_raw_field_input_(field, return_index=True)
    if not (isinstance(surface, int) and surface == 0):
        surface = self._convert_raw_field_input_(surface, return_index=True)
    def _do_mtf_mode_(MTF_type:str):
        # Settings. Example API calls for it do not work. Found a work around through configuration files.
        # MODIFYSETTINGS are defined in the ZPL help files: The Programming Tab > About the ZPL > Keywords
        SampSizeIdx = self._CheckIfStringValidInDir_(
            self.ZOSAPI.Analysis.SampleSizes, sample_size, extra_include_filter="S_"
        )
        TypeIdx = int(
            self._CheckIfStringValidInDir_(
                self.ZOSAPI.Analysis.Settings.Mtf.MtfTypes, MTF_type
            )
        )
        Settings                = {}
        Settings['MTF_SAMP']    = str(int(SampSizeIdx))
        Settings['MTF_WAVE']    = str(int(wavelength))
        Settings['MTF_FIELD']   = str(int(field))
        Settings['MTF_TYPE']    = str(int(TypeIdx))
        Settings['MTF_SURF']    = str(int(surface))
        Settings['MTF_MAXF']    = "0" if float(max_freq) <= 0 else str(float(max_freq))
        Settings['MTF_SDLI']    = "1" # Always show diffraction limit
        Settings['MTF_POLAR']   = "1" if use_polarization else "0"
        Settings['MTF_DASH']    = "1" # Dash line (for "classic mode" and does not matter here)
        cp("!@lg!@Analyses_FFTMTF :: Calculating FFT MTF [!@lm!@%s!@lg!@]." % MTF_type)
        xar, yar = self._Analysis_GeneralDataSeriesReader_(self.Analyses_RunAnalysesAndGetResults(analysis='FftMtf', analysis_settings=Settings))
        return xar, yar
    freq, mod_y   = _do_mtf_mode_('modulation')
    _, phase_y    = _do_mtf_mode_('phase')
    _, real_y     = _do_mtf_mode_('real')
    _, imag_y     = _do_mtf_mode_('imaginary')
    _, square_y   = _do_mtf_mode_('squarewave')
    if field != 0:
        fields        = [self.Field_GetField(field)]
    else:
        fields        = [self.Field_GetField(x+1) for x in range(self.Fields_GetNumberOfFields())]
    units         = self.Utilities_GetAllSystemUnits()
    freq_units    = str(units["MTFUnits"])
    cp("!@lg!@Analyses_FFTMTF :: Done Calculating FFT MTF.")
    out = xr.Dataset(
    {
        "modulation"                : (("field", freq_units, 'ray_type'), mod_y[1::].astype(float)),
        "phase"                     : (("field", freq_units, 'ray_type'), phase_y[1::].astype(float)),
        "real"                      : (("field", freq_units, 'ray_type'), real_y[1::].astype(float)),
        "imaginary"                 : (("field", freq_units, 'ray_type'), imag_y[1::].astype(float)),
        "square_wave"               : (("field", freq_units, 'ray_type'), square_y[1::].astype(float)),
        "modulation_diff_limited"   : ((freq_units, 'ray_type'), mod_y[0].astype(float)),
        "phase_diff_limited"        : ((freq_units, 'ray_type'), phase_y[0].astype(float)),
        "real_diff_limited"         : ((freq_units, 'ray_type'), real_y[0].astype(float)),
        "imaginary_diff_limited"    : ((freq_units, 'ray_type'), imag_y[0].astype(float)),
        "square_wave_diff_limited"  : ((freq_units, 'ray_type'), square_y[0].astype(float)),
    }, 
    coords={
        freq_units: (freq_units, freq[0].astype(float),),
        "field_x": ("field", np.array([x.X for x in fields]).astype(float),),
        "field_y": ("field", np.array([x.Y for x in fields]).astype(float),),
        "ray_type": ("ray_type", np.array(['sagittal_periodic_in_object_y', 'tangential_periodic_in_object_x']).astype(str),),
    },
    attrs={
        'Field_Type'    : str(self.Field_GetFieldType()),
        'Lens_Units'    : str(units["LensUnits"]),
    }
    )
    return out

def Analyses_FFTPSF(
    self,
    wavelength: int | float | ZOSAPI_SystemData_IWavelength = 0,
    field: int | ZOSAPI_SystemData_IField = 1,
    surface: int | ZOSAPI_Editors_LDE_ILDERow = 0,
    sample_size: str = "256x256",
    output_size: str = "512x512",
    image_delta_microns:int|float=0,
    use_polarization: bool = True,
    use_normalization: bool = True,
) -> xr.Dataset:
    """
    Get the (sequential) FFT MTF of the system.

    TODO: Support multipule MCE configurations

    :param wavelength: System wavelength (as index, microns, or object) to do the MTF on. An int of 0 selects all all wavelengths, Defaults to 0.
    :type wavelength: int | float | ZOSAPI_SystemData_IWavelength, optional
    :param field: System field (index of object) to do the MTF on.  An int of 0 selects all fields, defaults to 0
    :type field: int | ZOSAPI_SystemData_IField, optional
    :param surface: System surface (index or object) to do the MTF on. An int of 0 selects the image surface, defaults to 0
    :type surface: int, optional
    :param sample_size: Sampling of the PSF calulation. '32x32', '64x64', '128x128', '256x256', '512x512', '1024x1024', '2048x2048',  '4096x4096',  '8192x8192', '16384x16384', defaults to '256x256'
    :type sample_size: str, optional
    :param output_size: Size of the output grid (for display). '32x32', '64x64', '128x128', '256x256', '512x512', '1024x1024', '2048x2048',  '4096x4096',  '8192x8192', '16384x16384', defaults to '512x512'
    :type output_size: str, optional
    :param image_delta_microns: The distance in micrometers between points in the image grid. Use zero for the default grid spacing, defaults to 0
    :type image_delta: int|float, optional
    :param use_polarization: Use polarization, defaults to True
    :type use_polarization: bool, optional
    :param use_normalization: If should normalize the PSF or not, defaults to True
    :type use_normalization: bool, optional
    :return: The x and y data of the FFTMTF analysis.
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    # convert wavelength/fields/surface
    if not (isinstance(wavelength, int) and wavelength == 0):
        wavelength = self._convert_raw_wavelength_input_(wavelength, return_index=True)
    field = self._convert_raw_field_input_(field, return_index=True)
    if not (isinstance(surface, int) and surface == 0):
        surface = self._convert_raw_field_input_(surface, return_index=True)
    def _do_psf_mode_(PSF_type:str):
        # "OutputSize" is not docummented or seemignly accessable through what :func:`Analyses_RunAnalysesAndGetResults` would do.
        # This actually seems to be build on a "newer" version of the Zemax settings API which is much less abstractable it seems.
        # Doing manual assignmnet below through the use of `analysis_settings_obj.__implementation__`.
        analysis_obj, analysis_settings_obj, analysis_enum    = self._Analysis_GetZOSObjectAndSettings_(analysis='FftPsf')
        analysis_settings_obj                                 = analysis_settings_obj.__implementation__
        analysis_settings_obj.SampleSize                      = self._CheckIfStringValidInDir_(self.ZOSAPI.Analysis.Settings.Psf.PsfSampling, sample_size, extra_include_filter="S_")
        analysis_settings_obj.OutputSize                      = self._CheckIfStringValidInDir_(self.ZOSAPI.Analysis.Settings.Psf.PsfSampling, output_size, extra_include_filter="S_")
        analysis_settings_obj.Wavelength.SetWavelengthNumber(int(wavelength))
        analysis_settings_obj.Field.SetFieldNumber(int(field))
        analysis_settings_obj.Type                            = self._CheckIfStringValidInDir_(self.ZOSAPI.Analysis.Settings.Psf.FftPsfType, PSF_type)
        analysis_settings_obj.Surface.SetSurfaceNumber(int(surface))
        analysis_settings_obj.UsePolarization                 = use_polarization
        analysis_settings_obj.Normalize                       = use_normalization
        analysis_settings_obj.ImageDelta                      = float(image_delta_microns)
        cp("!@lg!@Analyses_FFTPSF :: Calculating FFT PSF [!@lm!@%s!@lg!@]..." % PSF_type)  
        analysis_obj.ApplyAndWaitForCompletion()
        gar, xar, yar = self._Analysis_GeneralDataGridReader_(analysis_obj.GetResults())
        return gar[0], xar[0], yar[0]
    ling, x, y   = _do_psf_mode_('linear')
    logg, _, _   = _do_psf_mode_('log')
    phaseg, _, _   = _do_psf_mode_('phase')
    realg, _, _   = _do_psf_mode_('real')
    imagg, _, _   = _do_psf_mode_('imaginary')
    units         = self.Utilities_GetAllSystemUnits()
    cp("!@lg!@Analyses_FFTPSF :: Done Calculating FFT PSF.")
    out = xr.Dataset(
    {
        "modulation"                : (("field", freq_units, 'ray_type'), mod_y[1::].astype(float)),
        "phase"                     : (("field", freq_units, 'ray_type'), phase_y[1::].astype(float)),
        "real"                      : (("field", freq_units, 'ray_type'), real_y[1::].astype(float)),
        "imaginary"                 : (("field", freq_units, 'ray_type'), imag_y[1::].astype(float)),
        "square_wave"               : (("field", freq_units, 'ray_type'), square_y[1::].astype(float)),
        "modulation_diff_limited"   : ((freq_units, 'ray_type'), mod_y[0].astype(float)),
        "phase_diff_limited"        : ((freq_units, 'ray_type'), phase_y[0].astype(float)),
        "real_diff_limited"         : ((freq_units, 'ray_type'), real_y[0].astype(float)),
        "imaginary_diff_limited"    : ((freq_units, 'ray_type'), imag_y[0].astype(float)),
        "square_wave_diff_limited"  : ((freq_units, 'ray_type'), square_y[0].astype(float)),
    }, 
    coords={
        freq_units: (freq_units, freq[0].astype(float),),
        "field_x": ("field", np.array([x.X for x in fields]).astype(float),),
        "field_y": ("field", np.array([x.Y for x in fields]).astype(float),),
        "ray_type": ("ray_type", np.array(['sagittal_periodic_in_object_y', 'tangential_periodic_in_object_x']).astype(str),),
    },
    attrs={
        'Field_Type'    : str(self.Field_GetFieldType()),
        'Lens_Units'    : str(units["LensUnits"]),
    }
    )
    return out


def Analyses_HuygensMTF(
    self,
    wavelength: int | float | ZOSAPI_SystemData_IWavelength = 0,
    field: int | ZOSAPI_SystemData_IField = 0,
    pupil_sample_size: str = "256x256",
    image_sample_size: str = "256x256",
    image_delta_microns:int|float=0,
    max_freq: float = 0,
    use_polarization: bool = True,
) -> xr.Dataset:
    """
    Get the Huygens MTF of the system.

    TODO: Support multipule MCE configurations
    
    :param wavelength: System wavelength (as index, microns, or object) to do the MTF on. An int of 0 selects all all wavelengths, Defaults to 0.
    :type wavelength: int | float | ZOSAPI_SystemData_IWavelength, optional
    :param field: System field (index of object) to do the MTF on.  An int of 0 selects all fields, defaults to 0
    :type field: int | ZOSAPI_SystemData_IField, optional
    :param pupil_sample_size:  Selects the size of the grid of rays to trace to perform the computation. Higher sampling densities yield more accurate results at the expense of longer computation times.
                               '32x32', '64x64', '128x128', '256x256', '512x512', '1024x1024', '2048x2048',  '4096x4096',  '8192x8192', '16384x16384', defaults to '256x256'
    :type pupil_sample_size: str, optional
    :param image_sample_size: The size of the grid of points on which to compute the diffraction image intensity. This number, combined with the image delta, determine the size of the area displayed. 
                              '32x32', '64x64', '128x128', '256x256', '512x512', '1024x1024', '2048x2048',  '4096x4096',  '8192x8192', '16384x16384', defaults to '256x256'
    :type image_sample_size: str, optional
    :param image_delta_microns: The distance in micrometers between points in the image grid. Use zero for the default grid spacing, defaults to 0
    :type image_delta: int|float, optional
    :param max_freq: Max frequency of the analysis, 0 allows Zemax to select it, defaults to 0
    :type max_freq: float, optional
    :param use_polarization: Use polarization, defaults to True
    :type use_polarization: bool, optional
    :return: The x and y data of the FFTMTF analysis.
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    # Code wise this is just an adapt of the FFT MTF
    # convert wavelength/fields/surface
    if not (isinstance(wavelength, int) and wavelength == 0):
        wavelength = self._convert_raw_wavelength_input_(wavelength, return_index=True)
    if not (isinstance(field, int) and field == 0):
        field = self._convert_raw_field_input_(field, return_index=True)
    PupilSampSizeIdx = self._CheckIfStringValidInDir_(
        self.ZOSAPI.Analysis.SampleSizes, pupil_sample_size, extra_include_filter="S_"
    )
    ImageSampSizeIdx = self._CheckIfStringValidInDir_(
        self.ZOSAPI.Analysis.SampleSizes, image_sample_size, extra_include_filter="S_"
    )
    Settings                    = {}
    Settings['HMF_PUPILSAMP']   = str(int(PupilSampSizeIdx))
    Settings['HMF_IMAGESAMP']   = str(int(ImageSampSizeIdx))
    if np.isclose(image_delta_microns, 0.0):
        Settings['HMF_IMAGEDELTA']    = str(int(0))
    else:
        Settings['HMF_IMAGEDELTA']    = str(float(image_delta_microns))
    Settings['HMF_CONFIG']    = str(int(0)) # TODO support configurations
    Settings['HMF_WAVE']      = str(int(wavelength))
    Settings['HMF_FIELD']     = str(int(field))
    Settings['HMF_TYPE']      = str(int(0)) # Only mode 0 = Modulation is supported by Zemax for Huygens
    Settings['HMF_MAXF']      = "0" if float(max_freq) <= 0 else str(float(max_freq))
    Settings['HMF_POLAR']     = "1" if use_polarization else "0"
    Settings['HMF_DASH']      = "1"
    freq, mod_y = self._Analysis_GeneralDataSeriesReader_(self.Analyses_RunAnalysesAndGetResults(analysis='HuygensMtf', analysis_settings=Settings))
    if field != 0:
        fields        = [self.Field_GetField(field)]
    else:
        fields        = [self.Field_GetField(x+1) for x in range(self.Fields_GetNumberOfFields())]
    units         = self.Utilities_GetAllSystemUnits()
    freq_units    = str(units["MTFUnits"])
    out = xr.Dataset(
    {
        "modulation"                : (("field", freq_units, 'ray_type'), mod_y.astype(float)),
    }, 
    coords={
        freq_units: (freq_units, freq[0].astype(float),),
        "field_x": ("field", np.array([x.X for x in fields]).astype(float),),
        "field_y": ("field", np.array([x.Y for x in fields]).astype(float),),
        "ray_type": ("ray_type", np.array(['sagittal_periodic_in_image_y', 'tangential_periodic_in_image_x']).astype(str),),
    },
    attrs={
        'Field_Type'    : str(self.Field_GetFieldType()),
        'Lens_Units'    : str(units["LensUnits"]),
    }
    )
    return out


