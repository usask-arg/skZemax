import numpy as np
from typing import Union
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import __LowLevelZemaxStringCheck__, _CheckIfStringValidInDir_, _SetAttrByStringIfValid_
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

    If more than one catalog could match the specified string, the first one sorted by ascending length, then alphabet, is taken

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
    This is only applicable in Sequential mode.

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
    Sets the system aperture in Zemax. This is only applicable in Sequential mode. 
    Properties are:
        - "ApertureType": The type of aperture to use. See 2.1.1.1. Aperture (System Explorer). 
        - "ApertureValue": The system aperture value meaning depends upon the system aperture type selected. See 2.1.1.1. Aperture (System Explorer). 
        - "ApodizationType": The type of anodization to apply. See 2.1.1.1. Aperture (System Explorer). 
        - "ApodizationFactor": The apodization factor determines how fast the amplitude decays in the pupil. Used only for Gaussian apodization.
        - "AFocalImageSpace": If this box is checked, Zemax will perform most analysis features in a manner appropriate for optical systems with output beams in image space that are nominally collimated.
        - "FastSemiDiameters": computes "automatic" clear semi-diameter or semi-diameters to estimate the clear aperture required on each surface to pass all rays at all field points and wavelengths. 
        - "CheckGRINApertures": If True, this setting instructs Zemax to check all gradient index ray traces for surface aperture vignetting.
        - "SemiDiameterMargin": The clear semi-diameter or semi-diameter of every surface in "automatic" mode, is computed to be the radial aperture required to pass all rays without clipping.
        - "SemiDiameterMarginPct": This semi diameter margin control allows specification of an additional amount of radial aperture as a percentage.
        - "TelecentricObjectSpace": If True,Zemax will assume the entrance pupil is located at infinity, regardless of the location of the stop surface.
        - "IterateSolvesWhenUpdating": Solves placed on parameters in the Lens Data Editor sometimes require iteration to compute accurately. 

    See 2.1.1.1. Aperture (System Explorer) in the help pdf for more detail.

    :param apertureProperty: The name of the aperture property to set, defaults to "ApertureValue"
    :type apertureProperty: str, optional
    :param apertureValue: The value to set the property to, defaults to 10.0
    :type apertureValue: Union[float,int,str,bool], optional
    """

    if isinstance(apertureValue, str):
        # If value is a sting, check to see if it can be looked up in a Zemax enum.
        # i.e. if apertureProperty="ApertureType", see if apertureValue matches something
        # in self.ZOSAPI.SystemData.ZemaxApertureType.
        try:
            value = self._CheckIfStringValidInDir_(eval("self.ZOSAPI.SystemData.Zemax" + str(apertureProperty.replace(' ', ''))), apertureValue)
        except Exception as e:
            cp('!@ly!@System_SetApertureProperty :: Raised Exception of [!@lm!@{}!@ly!@]. You likely did not supply a known apertureProperty.'.format(e))
    else:
        value = apertureValue
    self._SetAttrByStringIfValid_(self.TheSystem.SystemData.Aperture, apertureProperty, value)

def System_SetGlobalCoordinateReferenceSurface(self, reference_surface:Union[int,str]=1)->None:
    """
    Sets the Global Coordinate Reference Surface. This is a special property under the Aperture properties.
    Local coordinate systems are defined (with rotation and translation matrices) from this global reference surface.

    This is only applicable in Sequential mode.

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

def System_SetEnvironmentProperty(self, environmentProperty:str="AdjustIndexToEnvironment", environmentValue:Union[float,int,bool]=False)->None:
    """
    Sets if the index of refractions are adjusted to the environment (temperature and pressure).
    This should work for both Sequential and Non-Sequential modes.

    Properties are:
        - "AdjustIndexToEnvironment": Enables/disables the adjustment to the environment properties
        - "Temperature": If adjust_index_data_to_environment, then this is the temperature in celsius to use
        - "Pressure": If adjust_index_data_to_environment, then this is the pressure in atmospheres to use

    :param environmentProperty: The property of the environment to set. Options are: "AdjustIndexToEnvironment", "Temperature" (in degrees C), and "Pressure" (in ATM), defaults to "AdjustIndexToEnvironment"
    :type environmentProperty: str, optional
    :param environmentValue: Value to set the environment property to, defaults to False
    :type environmentValue: Union[float,int,bool], optional
    """
    _SetAttrByStringIfValid_(self, self.TheSystem.SystemData.Environment, environmentProperty, environmentValue)

def System_SetPolarizationProperty(self, polarizationProperty:str="ConvertThinFilmPhaseToRayEquivalent", polarizationValue:Union[float,int,str,bool]=True)->True:
    """
    The default input polarization state for many Sequential analysis computations which use polarization ray tracing.
    For Non-Sequential mode, most polarization settings are controlled by the sources, but two settings can still be controlled here.

        Sequential and Non-Sequential Mode:
            - "ConvertThinFilmPhaseToRayEquivalent": converts the polarization phase computed using thin film conventions to phase along the ray. If unselected, the ray coefficients will not be converted from the field coefficients. The recommended and default setting is to convert the field thin film phase to ray phase.
            - "Method": selects the method used to determine the S and P vectors based on the ray vector. Values are:
                - "XAxis": The P vector is determined from K cross X, and S = P cross K. This method is the default.
                - "YAxis": The S vector is determined from Y cross K, and P = K cross S
                - "ZAxis": The S vector is determined from K cross Z, and P = K cross S

        Sequential Mode Only:
            - "Unpolarized": If True, then the polarization values Jx, Jy, X-Phase, and Y-Phase are ignored, and an unpolarized computation is done.
            - If Unpolarized == False:
                - "Jx": the magnitude of the electric field in X
                - "Jy": the magnitude of the electric field in Y
                - "XPhase": the phase X angle in degrees
                - "YPhase": the phase Y angle in degrees

    One should read 2.1.1.5.7. Defining the Initial Polarization of the Zemax help pdf file for more information.

    :param polarizationProperty: The name of the polarization property to set, defaults to "ConvertThinFilmPhaseToRayEquivalent"
    :type polarizationProperty: str, optional
    :param polarizationValue: The value to set the property to, defaults to True
    :type polarizationValue: Union[float,int,str,bool], optional
    """

    if isinstance(polarizationValue, str):
        # If value is a sting, check to see if it can be looked up in a Zemax enum.
        # i.e. if polarizationProperty="Method", see if polarizationValue matches something.
        try:
            value = self._CheckIfStringValidInDir_(eval("self.ZOSAPI.SystemData.Polarization" + str(polarizationProperty.lower().replace(' ', '').replace('_', '').replace('Reference', 'Method')).title()), polarizationValue)
        except Exception as e:
            cp('!@ly!@System_SetPolarizationProperty :: Raised Exception of [!@lm!@{}!@ly!@]. You likely did not supply a known polarizationProperty.'.format(e))
    else:
        value = polarizationValue
    _SetAttrByStringIfValid_(self, self.TheSystem.SystemData.Polarization, polarizationProperty, value)

def System_SetAdvancedProperty(self, advancedProperty:str="ReferenceOPD", advancedValue:Union[float,int,str,bool]="ExitPupil")->True:
    """
    This function sets any advanced system properties. 
    This is mostly applicable to Sequential mode, but there are some options for Non-Sequential mode which can be set here too.

        Sequential and Non-Sequential Mode:
            - "TurnOffThreading": If True will not split calculations into multiple threads of execution. The only reason to turn off threading is if insufficient memory exists to break calculations into separate threads.
            - "IncludeCalculatedDataInSessionFile": If True, then calculated data for all open analysis windows (sequential mode) and/or all detectors (non-sequential mode) will be cached in the current session file.
            - "IncludeToleranceDataInSessionFile": If True, then tolerance data will be cached in the current session file. 
        
        Sequential Mode Only:
            - "ReferenceOPD":  the OPD represents the phase error of the wavefront forming an image. Any deviations from zero OPD contribute to a degradation of the diffraction image formed by the optical system. Options are:
                - "ExitPupil": (Zemax default) OPD is computed for a given ray, the ray is traced through the optical system, all the way to the image surface, and then is traced backward to the "reference sphere" which lies in the exit pupil.
                - "Infinity": The reference to "Infinity" makes the assumption that the exit pupil is very far away and that the OPD correction term is given strictly by the angular error in the ray.
                - "Absolute": The reference to "Absolute" and "Absolute 2" means that OpticStudio does not add any correction term to the OPD computation: the OPD is the difference of optical path length up to a reference plane between the chief ray and the ray being considered.
                - "Absolute2": Very similar to "Absolute", see Zemax help pdf for detail.
            - "ParaxialRays":
                - "IgnoreCoordinateBreaks": (Zemax default) By ignoring tilts and decenters, OpticStudio can compute the paraxial properties of an equivalent centered system, which is generally the correct approach even for systems without symmetry.
                - "ConsiderCoordinateBreaks":  For ray tracing through gratings, coordinate breaks may be required even for paraxial rays, otherwise, the rays may not be able to satisfy the grating equation. Ray tracing through non-sequential objects may also require that paraxial rays consider coordinate breaks.
            - "FNumMethod":
                - "TracingRays": (Zemax default) computes the paraxial and working F/# of a system using ray tracing.
                - "PupilSizePosition": The preferred method of modeling systems with very large F/#s is to use afocal mode. 
            - "HuygensIntegralMethod": The selection for this option determines what phase reference is used in the exit pupil for computing the Huygens Integral
                - "Auto": (Zemax default) Allow Zemax to control which phase reference is used to compute the Huygens Integral.
                - "Planar": always use a planar phase reference.
                - "Spherical": always use a spherical phase reference.
            - "DontPrintCoordinateBreakData": If True, selected data will not be printed for coordinate break surfaces. 
            - "OPDModulo2PI": If True, all OPD data will be computed as the fractional part of the total OPD. All OPD computations will return results that are between -π and +π, or -0.5 and +0.5 waves. 

    One should read 2.1.1.6. Advanced Options (System Explorer) of the Zemax help pdf file for more information on all of the above.

    :param polarizationProperty: The name of the polarization property to set, defaults to "ReferenceOPD"
    :type polarizationProperty: str, optional
    :param polarizationValue: The value to set the property to, defaults to "ExitPupil"
    :type polarizationValue: Union[float,int,str,bool], optional
    """

    if isinstance(advancedValue, str):
        # If value is a sting, check to see if it can be looked up in a Zemax enum.
        # Formatting strings to avoid case sensitivity / do auto-formatting for user
        if (('opd' in advancedProperty.lower() and 'mod' not in advancedProperty.lower()) or 
            ('opd' in advancedProperty.lower() and 'pi' in advancedProperty.lower()) or 
            'reference' in advancedProperty.lower()):
            advancedProperty = "ReferenceOPD"
        elif 'ray' in advancedProperty.lower() or 'paraxial' in advancedProperty.lower():
            advancedProperty = "ParaxialRays"
        elif ('method' in advancedProperty.lower() and 'huy' not in advancedProperty.lower()) or ('fnum' in advancedProperty.lower()):
            advancedProperty = "FNumMethod"
        elif 'huy' in advancedProperty.lower():
            advancedProperty = "HuygensIntegralMethod"
        elif 'mod' in advancedProperty.lower() or 'pi' in advancedProperty.lower():
            advancedProperty = "OPDModulo2PI"
        elif 'coord' in advancedProperty.lower():
            advancedProperty = "DontPrintCoordinateBreakData"
        elif 'thread' in advancedProperty.lower():
            advancedProperty = "TurnOffThreading"
        elif 'calc' in advancedProperty.lower() and 'session' in advancedProperty.lower():
            advancedProperty = "IncludeCalculatedDataInSessionFile"
        elif 'toler' in advancedProperty.lower() and 'session' in advancedProperty.lower():
            advancedProperty = "IncludeToleranceDataInSessionFile"
        else:
            cp('!@ly!@System_SetAdvancedProperty :: Do not understand property of [!@lm!@{}!@ly!@].'.format(advancedProperty))

        if "FNumMethod" not in advancedProperty and "HuygensIntegralMethod" not in advancedProperty:
            value = self._CheckIfStringValidInDir_(eval("self.ZOSAPI.SystemData." + advancedProperty + 'Setting'), advancedValue)
        elif "HuygensIntegralMethod" in advancedProperty:
            # ZOSAPI includes a "s" on "settings" for Huygens
            value = self._CheckIfStringValidInDir_(eval("self.ZOSAPI.SystemData." + str(advancedProperty.replace('Method', '')) + 'Settings'), advancedValue)
        else:
            # ZOSAPI module calls FNumMethod FNumberComputationType
            value = self._CheckIfStringValidInDir_(eval("self.ZOSAPI.SystemData." + str(advancedProperty.replace('Num','Number').replace('Method', '')) + 'ComputationType'), advancedValue)
    else:
        value = advancedValue
    _SetAttrByStringIfValid_(self, self.TheSystem.SystemData.Advanced, advancedProperty, value)

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