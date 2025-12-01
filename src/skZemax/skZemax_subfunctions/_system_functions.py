import numpy as np
from typing import Union
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import __LowLevelZemaxStringCheck__, _CheckIfStringValidInDir_
from skZemax.skZemax_subfunctions._c_print import c_print as cp
from skZemax.skZemax_subfunctions._LDE_functions import _convert_raw_surface_input_, LDE_GetNumberOfSurfaces, ZOSAPI_Editors_LDE_ILDERow


def System_GetNamesOfAllMaterialCatalogs(self, print_to_console:bool=False)->list:
    """
    This function builds a list of all the material catalogs that Zemax is aware of.
    This can be useful to look up what one may want to code as input to functions like :func:`System_AddMaterialCatalog`.

    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :return: A list of the names of all catalogs the ZOS-API knows.
    :rtype: list
    """
    available_catalogs = list(self.TheSystem.SystemData.MaterialCatalogs.GetAvailableCatalogs())
    if print_to_console:
        cp('\n!@lg!@System_GetNamesOfAllMaterialCatalogs :: Names of all Catalogs:')
        [cp('   !@lm!@' + str(x)) for x in available_catalogs]
        cp('\n')
    return available_catalogs

def System_AddMaterialCatalog(self, catalog:str='SCHOTT')->None:
    """
    Adds a catalog to the current Zemax system.

    See :func:`System_GetNamesOfAllMaterialCatalogs` to extract the names in python.

    If more than one catalog could match the specified string, the first one in the ZOS-API list is taken.

    :param catalog: Name of a catalog to add, defaults to 'SCHOTT'
    :type catalog: str, optional
    """
    available_catalogs = self.System_GetNamesOfAllMaterialCatalogs(print_to_console=False)
    bool_mask = [str(catalog).lower() in x.lower() for x in available_catalogs]
    if np.any(bool_mask):
        self.TheSystem.SystemData.MaterialCatalogs.AddCatalog(str(available_catalogs[int(np.where(bool_mask)[0][0])]))
    else:
        cp('!@ly!@System_AddMaterialCatalog :: Material catalog [!@lm!@{}!@ly!@] not found.'.format(catalog))

def System_GetNamesOfAllApertureSettings(self, print_to_console:bool=False)->list:
    """
    This function builds a list of all the system aperture settings in Zemax.
    This can be useful to look up what one may want to code as input to functions like :func:`System_SetApertureProperty`.

    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :return: A list of the names of all system apertures in Zemax.
    :rtype: list
    """
    available_apertures = [x for x in __LowLevelZemaxStringCheck__(self, in_obj=self.TheSystem.SystemData.Aperture, extra_exclude_filter='_') if 'GCRS' not in x]
    if print_to_console:
        cp('\n!@lg!@System_GetNamesOfAllApertureSettings ::Names of all Aperture Settings:')
        [cp('   !@lm!@' + str(x)) for x in available_apertures]
        cp('\n')
    return available_apertures


def System_SetApertureProperty(self, apertureProperty:str="ApertureValue", apertureValue:Union[float,int,str,bool]=10.0)->None:
    """
    Sets the system aperture in Zemax.

    :param apertureProperty: _description_, defaults to "ApertureValue"
    :type apertureProperty: str, optional
    :param apertureValue: _description_, defaults to 10.0
    :type apertureValue: Union[float,int,str,bool], optional
    """

    if isinstance(apertureValue, str):
        # If value is a sting, check to see if it can be looked up in a Zemax enum.
        # i.e. if apertureProperty="ApertureType", see if apertureValue matches something
        # in self.ZOSAPI.SystemData.ZemaxApertureType.
        value = self._CheckIfStringValidInDir_(eval("self.ZOSAPI.SystemData.Zemax" + str(apertureProperty)), apertureValue)
    else:
        value = apertureValue
    self._SetAttrByStringIfValid_(self.TheSystem.SystemData.Aperture, apertureProperty, value)

def System_SetGlobalCoordinateReferenceSurface(self, reference_surface:Union[int,str]=1)->None:
    """
    Sets the Global Coordinate Reference Surface. This is a special property under the Aperture properties.
    Local coordinate systems are defined (with rotation and translation matrices) from this global reference surface.

    Usually this is specified with an index indicating the surface of either your sequential or non-sequential system. 
    However, Zemax supports some general default options:

        - Image
        - Object
        - Stop

    These can be given as strings to specify one of these as the global reference.
        
    :param reference_surface: The surface to set as the global - either an index or a string as described above., defaults to 1
    :type reference_surface: Union[int,str], optional
    """

    if not isinstance(reference_surface, str):
        if (int(reference_surface) >= self.TheSystem.SystemData.Aperture.GCRS.FirstAllowedSurface) and (int(reference_surface) <= self.TheSystem.SystemData.Aperture.GCRS.LastAllowedSurface):
            self.TheSystem.SystemData.Aperture.GCRS.SetSelectedSurface(int(reference_surface))
        else:
            cp('!@ly!@System_SetGlobalCoordinateReferenceSurface :: Index [!@lm!@{}!@ly!@] not allowed. Must be between  [!@lm!@{}!@ly!@ and !@lm!@{}!@ly!@]'.format(reference_surface,
                                                                                                                                                                     self.TheSystem.SystemData.Aperture.GCRS.FirstAllowedSurface,
                                                                                                                                                                     self.TheSystem.SystemData.Aperture.GCRS.LastAllowedSurface))
    else:
        # Just formatting to allow inputs to have "use" or "surface" in the str as well.
        reference_surface = reference_surface.lower().strip("use").strip("surface")
        try:
            eval("self.TheSystem.SystemData.Aperture.GCRS.Use" + reference_surface.title() + "Surface()")
        except:
            cp('!@ly!@System_SetGlobalCoordinateReferenceSurface :: Surface type of [!@lm!@{}!@ly!@] not found. Expected one of: "Image", "Object", or "Stop"'.format(reference_surface))

def System_GetMode(self)->str:
    """
    Checks if in Sequential or Non-Sequential mode. returns the name of the mode.

    :return: A string of "Sequential" or "NonSequential" indicating the current mode.
    :rtype: str
    """
    return str(self.TheSystem.Mode)

def System_GetIfInSequentialMode(self)->bool:
    """
    Checks if the system is in Sequential mode.

    :return: if True the system is in Sequential mode.
    :rtype: bool
    """
    return int(self.TheSystem.Mode) == 0

def System_GetIfInNonSequentialMode(self)->bool:
    """
    Checks if the system is in Non-Sequential mode.

    :return: if True the system is in Non-Sequential mode.
    :rtype: bool
    """
    return int(self.TheSystem.Mode) == 1

def System_SetSequentialMode(self)->bool:
    """
    Sets/ensures the current system to be in Sequential mode.

    :return: An error checking boolean. True if the mode was set correctly.
    :rtype: bool
    """
 
    if self.System_GetIfInNonSequentialMode() and self._verbose: cp('!@lg!@System_SetSequentialMode :: Switching from Non-Sequential mode to Sequential.')
    ok = self.TheSystem.MakeSequential()
    if ok and self._verbose: cp('!@lg!@System_SetSequentialMode :: Sequential mode is set.')
    elif not ok and self._verbose: cp('!@lr!@System_SetSequentialMode :: Sequential mode was not set correctly.')
    return ok

def System_SetNonSequentialMode(self)->bool:
    """
    Sets/ensures the current system to be in Non-Sequential mode.

    :return: An error checking boolean. True if the mode was set correctly.
    :rtype: bool
    """
    if self.System_GetIfInSequentialMode() and self._verbose: cp('!@lg!@System_SetNonSequentialMode :: Switching from Sequential mode to Non-Sequential.')
    ok = self.TheSystem.MakeNonSequential()
    if ok and self._verbose: cp('!@lg!@System_SetNonSequentialMode :: Non-Sequential mode is set.')
    elif not ok and self._verbose: cp('!@lr!@System_SetNonSequentialMode :: Non-Sequential mode was not set correctly.')
    return ok

def System_Lockdown(self,
                    decimalPrecision:int=None,
                    excludePickups:bool=None,
                    usePrecisionRounding:bool=None,
                    fixModelGlasses:bool=None,
                    convertSDtoMaxApertures:bool=None,
                    )->None:
    """
    Runs the system lock-down tool to fix diameters, remove solves, and validating a sequential design prior to manufacturing or conversion to non-sequential, etc.

    :param decimalPrecision: Controls how many decimal places are included when UsePrecisionRounding is turned on, defaults to None
    :type decimalPrecision: int, optional
    :param excludePickups: If true, pickup solves will be retained in the converted system; otherwise all solves will be removed including pickups, defaults to None
    :type excludePickups: bool, optional
    :param usePrecisionRounding: Controls whether or not editor values will be rounded in the output system, defaults to None
    :type usePrecisionRounding: bool, optional
    :param fixModelGlasses: Controls whether any model glass solves will be converted to the nearest material in the selected catalogs, defaults to None
    :type fixModelGlasses: bool, optional
    :param convertSDtoMaxApertures: Controls whether floating semi-diameters will be treating as if they have a Maximum solve attached, defaults to None
    :type convertSDtoMaxApertures: bool, optional
    """

    if self._verbose: cp('!@lg!@System_Lockdown :: Locking system down...')
    LockdownTool = self.TheSystem.Tools.OpenDesignLockdown()
    if decimalPrecision is not None:
        LockdownTool.DecimalPrecision = int(decimalPrecision)
    if excludePickups is not None:
        LockdownTool.ExcludePickups = bool(excludePickups)
    if usePrecisionRounding is not None:
        LockdownTool.UsePrecisionRounding = bool(usePrecisionRounding)
    if fixModelGlasses is not None:
        LockdownTool.FixModelGlasses  = bool(fixModelGlasses)
    if convertSDtoMaxApertures is not None:
        LockdownTool.ConvertSDToMaxApertures = bool(convertSDtoMaxApertures)
    LockdownTool.RunAndWaitForCompletion()
    LockdownTool.Close()
    if self._verbose: cp('!@lg!@System_Lockdown :: Done locking system down.')


def System_ConvertSequentialToNonSequential(self, 
                                            first_surface:Union[int, ZOSAPI_Editors_LDE_ILDERow]=1, 
                                            last_surface:Union[int, ZOSAPI_Editors_LDE_ILDERow]=None,
                                            ignore_errors:bool=True,
                                            create_source_and_detector:bool=False,
                                            convert_global_coordinates:bool=False,
                                            convert_stop_to_nsc_aperture:bool=True,
                                            stop_mechanical_half_width:float=None,
                                            high_fidelity_conversion:bool=True,
                                            high_fidelity_resolution:int=65):
    """
    Converts a sequential Zemax file to a non-sequential Zemax file.

        It is recommended that you also consider running :func:`System_Lockdown` before running this function.

    :param first_surface: The location of the first surface to convert. Specified by either an index or a surface object, defaults to 1
    :type first_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], optional
    :param last_surface:  The location of the last surface to convert. Specified by either an index or a surface object, defaults to None (last/image surface)
    :type last_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], optional
    :param ignore_errors: If conversion should try to ignore errors, defaults to True
    :type ignore_errors: bool, optional
    :param create_source_and_detector: Ignores surface indices and converts the whole system - attempting to make source and image objects too, defaults to False
    :type create_source_and_detector: bool, optional
    :param convert_global_coordinates: If should convert to global coordinates, defaults to False
    :type convert_global_coordinates: bool, optional
    :param convert_stop_to_nsc_aperture: If should convert the stop to an non-sequential aperture, defaults to True
    :type convert_stop_to_nsc_aperture: bool, optional
    :param stop_mechanical_half_width: The mechanical half width of the stop, defaults to None (uses sequential mode value)
    :type stop_mechanical_half_width: float, optional
    :param high_fidelity_conversion: If true, any sequential surfaces that convert to grid sag representations will use bicubic interpolation instead of linear and the resolution will be set to the value specified in high_fidelity_resolution, defaults to True
    :type high_fidelity_conversion: bool, optional
    :param high_fidelity_resolution: IF high_fidelity_conversion is set to true, this sets the resolution used in the Grid Sag surface after conversion. Input is treated as ##x## with ## being one of: '33', '65', '129', '257', '513', '1025', '2049', '4097', '8193', defaults to None
    :type high_fidelity_resolution: str, optional
    """
    if self.System_GetIfInSequentialMode():
        if self._verbose: cp('!@lg!@System_ConvertSequentialToNonSequential :: Converting system to Non-Sequential...')
        converter                             = self.TheSystem.Tools.OpenConvertToNSCGroup()
        converter.ConvertFileToNSC            = True
        converter.IgnoreErrors                = bool(ignore_errors)
        converter.CreateSourcesAndDetectors   = bool(create_source_and_detector)
        converter.ConvertToGlobalCoordinates  = bool(convert_global_coordinates)
        converter.ConvertStopToNSCAperture    = bool(convert_stop_to_nsc_aperture)
        converter.HighFidelityConversion      = bool(high_fidelity_conversion)
        if not create_source_and_detector:
            converter.FirstSurface = _convert_raw_surface_input_(self, first_surface, return_index=True)
            if last_surface is None:
                last_surface = self.LDE_GetNumberOfSurfaces()
            converter.FirstSurface = _convert_raw_surface_input_(self, first_surface, return_index=True)
            converter.LastSurface  = _convert_raw_surface_input_(self, last_surface, return_index=True)
        else:
            converter.FirstSurface = 1
            converter.LastSurface  = self.LDE_GetNumberOfSurfaces()
        if stop_mechanical_half_width is not None:
            converter.StopMechanicalHalfWidth   = float(stop_mechanical_half_width)
            converter.HighFidelityResolution    = self._CheckIfStringValidInDir_(self.ZOSAPI.Analysis.SampleSizes_Pow2Plus1_X , 'S_{}x{}'.format(int(high_fidelity_resolution), int(high_fidelity_resolution)))
        converter.RunAndWaitForCompletion()
        converter.Close();
        if self._verbose: cp('!@lg!@System_ConvertSequentialToNonSequential :: Done converting system to Non-Sequential.')
    else:
         if self._verbose: cp('!@lg!@System_ConvertSequentialToNonSequential :: System is already Non-Sequential.')