import numpy as np
import os
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import _CheckIfStringValidInDir_, __LowLevelZemaxStringCheck__
from skZemax.skZemax_subfunctions._utility_functions import Utilities_ConfigFilesDir
from skZemax.skZemax_subfunctions._system_functions import System_GetMode
from skZemax.skZemax_subfunctions._c_print import c_print as cp
from typing import Union
from skZemax.skZemax_subfunctions._LDE_functions import ZOSAPI_Editors_LDE_ILDERow, _convert_raw_surface_input_
from pathlib import Path

type ZOSAPI_Analysis_Data_IA  = object #<- ZOSAPI.Analysis.IA_ # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Analysis_Data_IAR = object #<- ZOSAPI.Analysis.Data.IAR_ # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Analysis_Data_IAS = object #<- ZOSAPI.Analysis.Settings.IAS_ # The actual module is referenced by the base PythonStandaloneApplication class.

def _Analyses_GetZOSObjectAndSettings_(self, analysis:str)->tuple[ZOSAPI_Analysis_Data_IA, ZOSAPI_Analysis_Data_IAS, str]:
    """
    Worker function which looks up the specified analysis object and settings - which some condition checking. 
    A tuple of None values is returned if the analysis is not recognized, or not applicable to the type of sequential mode.

    :param analysis: The name of the analysis to perform. See output of :func:`Analyses_GetNamesOfAllAnalyses` for names.
    :type analysis: str
    :return: OSAPI.Analysis.Data object, the ZOSAPI.Analysis.Settings object, and the ZOS-API name of the specified analysis.
    :rtype: tuple[ZOSAPI_Analysis_Data_IA, ZOSAPI_Analysis_Data_IAS, str]
    """
    analysis_enum = _CheckIfStringValidInDir_(self, self.ZOSAPI.Analysis.AnalysisIDM, analysis)
    if analysis_enum is None:
        return None, None, None
    analysis_obj            = self.TheSystem.Analyses.New_Analysis(analysis_enum)
    if analysis_obj is None:
        if self._verbose: cp('!@ly!@_Analyses_GetZOSObjectAndSettings_ :: Analysis [!@lm!@{}!@ly!@] is not applicable to [!@lm!@{}!@ly!@] mode.'.format(str(analysis_enum), self.System_GetMode()))
        return None, None, None
    analysis_settings_obj   = analysis_obj.GetSettings()
    if analysis_settings_obj is None:
        del analysis_obj
        analysis_obj = None
        if self._verbose: cp('!@ly!@_Analyses_GetZOSObjectAndSettings_ :: Analysis [!@lm!@{}!@ly!@] is not applicable to [!@lm!@{}!@ly!@] mode.'.format(str(analysis_enum), self.System_GetMode()))
        return None, None, None
    return analysis_obj, analysis_settings_obj, str(analysis_enum)

def _Analysis_SetZOSObjectSettingsByDict_(self, analysis_settings:dict, analysis_settings_obj:ZOSAPI_Analysis_Data_IAS, analysis_enum:str)->None:
    """
    A worker function which will set analysis settings through the ModifySettings() scheme documented in Section 10.2.14.92. MODIFYSETTINGS (keywords).
    This is done by making, configuring, and then loading a configuration file. This config file method seems to be the only robust way to configure analysis settings.

    :param analysis_settings: A python dictatory to adjust settings of the analysis. Formatted as dict[MODIFYSETTINGS KEYWORD] = str(value), defaults to None
    :type analysis_settings: dict
    :param analysis_settings_obj: Analysis settings object
    :type analysis_settings_obj: ZOSAPI_Analysis_Data_IAS
    :param analysis_enum: the ZOS-API name of the specified analysis
    :type analysis_enum: str
    """
    if analysis_settings is not None:
        # Set all settings through the configuration file "ModifySettings()" function.
        cfgFile = self.Utilities_ConfigFilesDir() + os.sep + analysis_enum + '.CFG'
        analysis_settings_obj.SaveTo(cfgFile)
        [analysis_settings_obj.ModifySettings(cfgFile, x, str(analysis_settings[x])) for x in analysis_settings.keys()]
        analysis_settings_obj.LoadFrom(cfgFile)

def _Analysis_SetZOSObjectSettingsByBinaryAlteration_(self, analysis_settings:np.ndarray, analysis_settings_obj:ZOSAPI_Analysis_Data_IAS, analysis_enum:str)->None:
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
        cfgFile = self.Utilities_ConfigFilesDir() + os.sep + str(analysis_enum) + '.CFG'
        analysis_settings_obj.SaveTo(cfgFile)
        cfgFile_path = Path(cfgFile)
        settings_bytestring = cfgFile_path.read_bytes()
        settings_bytearray = bytearray(settings_bytestring)
        # I believe byte indices 0-19 is effectively header information. Analysis settings begin at index 20 and increments by 4 per option.
        for idx, binidx in enumerate(np.arange(20, 20 + analysis_settings.shape[0]*4, 4)):
            settings_bytearray[binidx] = analysis_settings[idx]
        cfgFile_path.write_bytes(settings_bytearray)
        del cfgFile_path
        cfgFile_path = None
        analysis_settings_obj.LoadFrom(cfgFile)

def Analyses_GetNamesOfAllAnalyses(self, print_to_console:bool=False)->list:
    """
    This function is simply for user convenance to look up the ZOS-API names of all analysis types.
    This can be useful to look up what one may want to code as input to functions like :func:`Analyses_RunAnalysesAndGetResults`.


    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :return: A list of the names of all analyses types the ZOS-API knows.
    :rtype: list
    """
    analyses_types = __LowLevelZemaxStringCheck__(self, in_obj=self.ZOSAPI.Analysis.AnalysisIDM)
    if print_to_console:
        cp('\n!@lg!@Analyses_GetNamesOfAllAnalyses :: Names of Analyses:')
        [cp('   !@lm!@' + str(x)) for x in analyses_types]
        cp('\n')
    return analyses_types

def Analyses_RunAnalysesAndGetResults(self, analysis:str, analysis_settings:Union[dict, np.ndarray[int]]=None)->ZOSAPI_Analysis_Data_IAR:
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
    analysis_obj, analysis_settings_obj, analysis_enum = self._Analyses_GetZOSObjectAndSettings_(analysis=analysis)
    if analysis_obj is None or analysis_settings_obj is None:
        return None
    if analysis_settings is not None and isinstance(analysis_settings, dict):
        self._Analysis_SetZOSObjectSettingsByDict_(analysis_settings=analysis_settings, analysis_settings_obj=analysis_settings_obj, analysis_enum=analysis_enum)
    elif analysis_settings is not None and isinstance(analysis_settings, np.ndarray):
        self._Analysis_SetZOSObjectSettingsByBinaryAlteration_(analysis_settings=analysis_settings, analysis_settings_obj=analysis_settings_obj, analysis_enum=analysis_enum)
    elif analysis_settings is not None:
        if self._verbose: cp('!@ly!@Analyses_RunAnalysesAndGetResults :: WARNING :: Settings supplied but format not recognized. Nothing configured.')
    if self._verbose: cp('!@lg!@Analyses_RunAnalysesAndGetResults :: Running analysis [!@lm!@{}!@lg!@] ...'.format(str(analysis_enum)))
    analysis_obj.ApplyAndWaitForCompletion()
    if self._verbose: cp('!@lg!@Analyses_RunAnalysesAndGetResults :: Done.')
    return analysis_obj.GetResults()
            
def Analyses_ReportSystemPrescription(self, save_textfile_path:str=None)->list:
    """
     Constructs the prescription report of the optical system. This is returned as text information which can be saved in a .txt file.

    :param save_textfile_path:save_textfile_path: Full absolute .txt file path to save prescription data text file, defaults to None (no custom saving)
    :type save_textfile_path: str, optional
    :return: A list where each element is a line of the prescription report.
    :rtype: list
    """
    if save_textfile_path is None:
        save_path = self.Utilities_AnalysesFilesDir() + os.sep + 'PrescriptionDataSettings.txt'
    else:
        if not save_textfile_path[-4::] == '.txt':
            save_textfile_path += '.txt'
        save_path = save_textfile_path
    result = self.Analyses_RunAnalysesAndGetResults(analysis='PrescriptionDataSettings')
    result.GetTextFile(save_path)
    with open(save_path, 'r') as file:
        content = file.read()
    system_prescription = [x for x in content.replace('\x00', '').strip('ÿþ').split('\n') if len(x)>0]
    return system_prescription

def Analyses_ReportSurfacePrescription(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], save_textfile_path:str=None)->list:
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
        save_path = self.Utilities_AnalysesFilesDir() + os.sep + 'SurfaceDataSetting.txt'
    else:
        if not save_textfile_path[-4::] == '.txt':
            save_textfile_path += '.txt'
        save_path = save_textfile_path
    result = self.Analyses_RunAnalysesAndGetResults(analysis='SurfaceDataSetting', analysis_settings=np.array([self._convert_raw_surface_input_(in_Surface, return_index=True)]))
    result.GetTextFile(save_path)
    with open(save_path, 'r') as file:
        content = file.read()
    return [x for x in content.replace('\x00', '').strip('ÿþ').split('\n') if len(x)>0]

def Analyses_FFTMTF(self,
                       wavelength_index:int=0,
                       field_index:int=0,
                       surface_index:int=0,
                       MTF_type:str='mod',
                       sampleSize:str='256x256',
                       maxFreq:float=0,
                       ShowDiffractionLimit:bool=True,
                       UseDashes:bool=True,
                       UsePolarization:bool=True)->tuple[np.ndarray, np.ndarray]:
    """
    Get FFTMTF of the system.

    :param wavelength_index: System wavelength index to do the MTF on. 0 is for all wavelengths, Defaults to 0.
    :type wavelength_index: int, optional
    :param field_index: System field index to do the MTF on. 0 is for all fields, defaults to 0
    :type field_index: int, optional
    :param surface_index: System surface index to do the MTF on. 0 is for image surface, defaults to 0
    :type surface_index: int, optional
    :param MTF_type: Type of MTF to report: 'modulation', 'real', 'imaginary', 'phase', 'square wave', defaults to 'mod'
    :type MTF_type: str, optional
    :param sampleSize: '1024x1024', '128x128', '16384x16384', '2048x2048', '256x256', '32x32', '4096x4096', '512x512', '64x64', '8192x8192', defaults to '256x256'
    :type sampleSize: str, optional
    :param maxFreq: Max frequency of the analysis, 0 to default, defaults to 0
    :type maxFreq: float, optional
    :param ShowDiffractionLimit: Include diffraction limited curves, defaults to True
    :type ShowDiffractionLimit: bool, optional
    :param UseDashes: Use dashes, defaults to True
    :type UseDashes: bool, optional
    :param UsePolarization: Use polarization, defaults to True
    :type UsePolarization: bool, optional
    :return: The x and y data of the FFTMTF analysis.
    :rtype: tuple[np.ndarray, np.ndarray] 
    """

    if '.CFG' not in CFG_filename:
        CFG_filename += '.CFG'
    newMTF            = self.TheSystem.Analyses.New_FftMtf()
    # Settings. Example API calls for it do not work. Found a work around through configuration files.
    # MODIFYSETTINGS are defined in the ZPL help files: The Programming Tab > About the ZPL > Keywords
    SampSizeIdx       = self._CheckIfStringValidInDir_(self.ZOSAPI.Analysis.SampleSizes, sampleSize, extra_include_filter='S_')
    TypeIdx           = int(self._CheckIfStringValidInDir_(self.ZOSAPI.Analysis.Settings.Mtf.MtfTypes, MTF_type))
    newMTF_Settings   = newMTF.GetSettings()
    cfgFile           = self.Utilities_ConfigFilesDir() + os.sep + CFG_filename
    newMTF_Settings.SaveTo(cfgFile)
    newMTF_Settings.ModifySettings(cfgFile, "MTF_SAMP", str(int(SampSizeIdx)))
    newMTF_Settings.ModifySettings(cfgFile, "MTF_WAVE", str(int(wavelength_index)))
    newMTF_Settings.ModifySettings(cfgFile, "MTF_FIELD", str(int(field_index)))
    newMTF_Settings.ModifySettings(cfgFile, "MTF_TYPE", str(int(TypeIdx)))
    newMTF_Settings.ModifySettings(cfgFile, "MTF_SURF", str(int(surface_index)))
    newMTF_Settings.ModifySettings(cfgFile, "MTF_MAXF", '0' if float(maxFreq) <= 0 else str(float(maxFreq)))
    newMTF_Settings.ModifySettings(cfgFile, "MTF_SDLI", "1" if ShowDiffractionLimit else "0")
    newMTF_Settings.ModifySettings(cfgFile, "MTF_POLAR", "1" if UsePolarization else "0")
    newMTF_Settings.ModifySettings(cfgFile, "MTF_DASH", "1" if UseDashes else "0")
    newMTF_Settings.LoadFrom(cfgFile)
    # Get
    cp('!@lg!@Analyses_getFFTMTF :: Calculating FFT MTF...')
    newMTF.ApplyAndWaitForCompletion()
    results = newMTF.GetResults()
    xar = []
    yar = []
    for seriesNum in range(results.NumberOfDataSeries):
        data = results.GetDataSeries(seriesNum)
        xRaw = data.XData.Data
        yRaw = data.YData.Data
        xar.append(np.array(tuple(xRaw)))
        try:
            yar.append(np.array(np.asarray(tuple(yRaw)).reshape(data.YData.Data.GetLength(0), data.YData.Data.GetLength(1))))
        except:
            yar.append(np.array(np.asarray(tuple(yRaw))))
    cp('!@lg!@Analyses_getFFTMTF :: Done Calculating FFT MTF.')
    return np.array(xar), np.array(yar)
