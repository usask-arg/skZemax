import numpy as np
from skZemax.skZemax_subfunctions._c_print import c_print as cp
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import _convert_raw_input_worker_, __LowLevelZemaxStringCheck__, _CheckIfStringValidInDir_, _ctype_to_numpy_
from skZemax.skZemax_subfunctions._field_functions import Field_GetNormalization
from skZemax.skZemax_subfunctions._wavelength_functions import Wavelength_GetNumberOfWavelengths, Wavelength_GetWavelength, _convert_raw_wavelength_input_, ZOSAPI_SystemData_IWavelength
from typing import Union
import xarray as xr
import clr

type ZOSAPI_Editors_LDE_ILDERow                 = object #<- ZOSAPI.Editors.LDE.ILDERow # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Editors_LDE_ISurfaceApertureType    = object #<- ZOSAPI.Editors.LDE.ISurfaceApertureType # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Editors_LDE_SurfaceColumn            = object #<- ZOSAPI.Editors.LDE.SurfaceColumn # The actual module is referenced by the base PythonStandaloneApplication class.

def _convert_raw_surface_input_(self, in_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], return_index:bool=True)->Union[int, ZOSAPI_Editors_LDE_ILDERow]:
    return _convert_raw_input_worker_(self, in_value=in_surface, object_type=self.ZOSAPI.Editors.LDE.ILDERow, return_index=return_index)

def LDE_GetNumberOfSurfaces(self)->int:
    """
    Gets the number of surfaces in the LDE

    :return: The total number of (sequential) surfaces in the lens data editor (LDE)
    :rtype: int
    """

    return int(self.TheSystem.LDE.get_NumberOfSurfaces())

def LDE_GetSurface(self, SurfaceNum: int)->ZOSAPI_Editors_LDE_ILDERow:
    """
    Returns a surface object at the given index.

    :param SurfaceNum:  Surface index number
    :type SurfaceNum: int
    :return: The object of the surface at index.
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """

    SurfaceNum = int(SurfaceNum)
    if SurfaceNum < self.LDE_GetNumberOfSurfaces() and SurfaceNum >= 0:
        return self.TheSystem.LDE.GetSurfaceAt(int(SurfaceNum))
    if self._verbose: cp('!@ly!@LDE_GetSurface :: Asked for Surface [!@lm!@{}!@ly!@] but there are only !@lm!@{}!@ly!@ surfaces built up to index !@lm!@{}!@ly!@.'.format(SurfaceNum, self.LDE_GetNumberOfSurfaces(), self.LDE_GetNumberOfSurfaces()-1))
    return None

def LDE_InsertNewSurface(self, insertSurface: Union[int, ZOSAPI_Editors_LDE_ILDERow])->ZOSAPI_Editors_LDE_ILDERow:
    """
    Inserts a new surface at specified location in the LDE.

    :param insertSurface: The location to insert the surface. Specified by either an index or a surface object. 
    :type insertSurface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :return: The surface object of the newly inserted surface.
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """

    return self.TheSystem.LDE.InsertNewSurfaceAt(self._convert_raw_surface_input_(insertSurface, return_index=True))

def LDE_AddNewSurface(self)->ZOSAPI_Editors_LDE_ILDERow:
    """
    Adds a new surface to the end of the system

    :return: The surface object of the newly made surface.
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """

    return self.TheSystem.LDE.AddSurface()

def LDE_RemoveSurface(self, delSurface: Union[int, ZOSAPI_Editors_LDE_ILDERow])->None:
    """
    Removes the surface at specified location in the LDE.

    :param delSurface: The location to delete the surface. Specified by either an index or a surface object. 
    :type delSurface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    """

    self.TheSystem.LDE.RemoveSurfaceAt(self._convert_raw_surface_input_(delSurface, return_index=True))

def LDE_CopyAndInsertSurfacesFromFile(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], path_to_file:str, first_surface_to_copy:int, number_surfaces_to_copy:int, )->None:
    """
    Copies surfaces from another .zmx file and insert them into the current one.
    Surfaces of first_surface_to_copy to (first_surface_to_copy + number_surfaces_to_copy) are inserted in the current file beginning at in_Surface.

    :param in_Surface: Location in the active file to begin inserting surfaces.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param path_to_file: Path to another Zemax file from which to copy some surface elements.
    :type path_to_file: str
    :param first_surface_to_copy: The first surface in the external Zemax file to copy over into the currently active one.
    :type first_surface_to_copy: int
    :param number_surfaces_to_copy: The number of surfaces after first_surface_to_copy to copy over along with it.
    :type number_surfaces_to_copy: int
    """
    SurfaceLDE = self._convert_raw_surface_input_(in_Surface, return_index=True)
    new_system = self.TheApplication.CreateNewSystem(self.ZOSAPI.SystemType.Sequential)
    new_system.LoadFile(path_to_file, False)
    self.TheSystem.LDE.CopySurfacesFrom(new_system.LDE, first_surface_to_copy, number_surfaces_to_copy, SurfaceLDE)
    self.TheApplication.CloseSystemAt(self.TheApplication.get_NumberOfOpticalSystems()-1, False)
    del new_system

def LDE_GetNamesOfAllSurfaceTypes(self, print_to_console:bool=False)->list:
    """
    This function is simply for user convenance to look up the ZOS-API names of all surface types.
    This can be useful to look up what one may want to code as input to functions like :func:`LDE_ChangeSurfaceType`.

    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :return:  A list of the names of all surface types the ZOS-API knows.
    :rtype: list
    """
    surface_types = __LowLevelZemaxStringCheck__(self, in_obj=self.ZOSAPI.Editors.LDE.SurfaceType)
    if print_to_console:
        cp('\n!@lg!@LDE_GetListOfAllSurfaceTypes :: Names of Surface Types:')
        [cp('   !@lm!@' + str(x)) for x in surface_types]
        cp('\n')
    return surface_types

def LDE_ChangeSurfaceType(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], surface_type: str)->ZOSAPI_Editors_LDE_ILDERow:
    """
    This function changes the surface type of a (sequential) surface element in the lens data editor.

    Surface types are described in Zemax documentation, and can be named by the :func:`LDE_GetNamesOfAllSurfaceTypes` function.

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param surface_type: A string identifying the surface type to change it to.
    :type surface_type: str
    :return: The surface object being operated on.
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """
    SurfaceLDE = self._convert_raw_surface_input_(in_Surface, return_index=False)
    surfacetype = self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.LDE.SurfaceType, str(surface_type))
    if surfacetype is not None:
        SurfaceLDE.ChangeType(SurfaceLDE.GetSurfaceTypeSettings(surfacetype))
    elif self._verbose: cp('!@ly!@LDE_ChangeSurfaceType :: Did not change surface type')
    return SurfaceLDE

def LDE_GetNamesOfAllApertureTypes(self, print_to_console:bool=False)->list:
    """
    This function is simply for user convenance to look up the ZOS-API names of all aperture types.
    This can be useful to look up what one may want to code as input to functions like :func:`LDE_GetApertureTypeSettings`.

    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :return: A list of the names of all aperture types the ZOS-API knows.
    :rtype: list
    """
    aperture_types = __LowLevelZemaxStringCheck__(self, in_obj=self.ZOSAPI.Editors.LDE.SurfaceApertureTypes)
    if print_to_console:
        cp('\n!@lg!@LDE_GetNamesOfAllApertureTypes :: Names of Aperture Types:')
        [cp('   !@lm!@' + str(x)) for x in aperture_types]
        cp('\n')
    return aperture_types

def LDE_GetApertureTypeSettings(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], aperture_type: str)->ZOSAPI_Editors_LDE_ISurfaceApertureType:
    """
    Gets the aperture type settings to change a LDE surface's aperture.
    
    Note that while this is available to a user for customized implantation, it is recommended to go through a pre-defined function like
    :func:`LDE_ChangeApertureToRectangular` or :func:`LDE_ChangeApertureToCircular` to change the aperture.


    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param aperture_type: A string identifying the aperture type to change it to.
    :type aperture_type: str
    :return: The settings of the aperture to change.
    :rtype: ZOSAPI_Editors_LDE_ISurfaceApertureType
    """
    SurfaceLDE      = self._convert_raw_surface_input_(in_Surface, return_index=False)
    aperturetype    = self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.LDE.SurfaceApertureTypes, str(aperture_type))
    settings        = None
    if aperturetype is not None:
        settings = SurfaceLDE.ApertureData.CreateApertureTypeSettings(aperturetype)
    elif self._verbose:
        cp('!@ly!@LDE_GetApertureTypeSettings :: Did not find {} aperture type settings'.format(str(aperture_type)))
        return None
    return settings

def LDE_ChangeApertureToRectangular(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], XHalfWidth:float=10.0, YHalfWidth:float=10.0, ApertureXDecenter:float=0.0, ApertureYDecenter:float=0.0)->ZOSAPI_Editors_LDE_ILDERow:
    """
    Changes the aperture of the surface to a rectangular one with specified widths
    Rays are vignetted which intercept the surface outside the rectangular region defined by the half widths in x and y.

    :param in_Surface:  The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param XHalfWidth: The half-width in the x-direction of the aperture, defaults to 10.0
    :type XHalfWidth: float, optional
    :param YHalfWidth: The half-width in the y-direction of the aperture, defaults to 10.0
    :type YHalfWidth: float, optional
    :param ApertureXDecenter: The decenter in the x-direction of the aperture, defaults to 0.0
    :type ApertureXDecenter: float, optional
    :param ApertureYDecenter: The decenter in the y-direction of the aperture, defaults to 0.0
    :type ApertureYDecenter: float, optional
    :return: The surface object.
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """

    SurfaceLDE    = self._convert_raw_surface_input_(in_Surface, return_index=False)
    settings      = self.LDE_GetApertureTypeSettings(in_Surface=SurfaceLDE, aperture_type='RectangularAperture')
    settings._S_RectangularAperture.XHalfWidth          = XHalfWidth
    settings._S_RectangularAperture.YHalfWidth          = YHalfWidth
    settings._S_RectangularAperture.ApertureXDecenter   = ApertureXDecenter
    settings._S_RectangularAperture.ApertureYDecenter   = ApertureYDecenter
    SurfaceLDE.ApertureData.ChangeApertureTypeSettings(settings)
    return SurfaceLDE

def LDE_ChangeApertureToCircular(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], MinimumRadius:float=0.0, MaximumRadius:float=10.0, ApertureXDecenter:float=0.0, ApertureYDecenter:float=0.0)->ZOSAPI_Editors_LDE_ILDERow:
    """
    Changes the aperture of the surface to a circular one with specified radii.

    A Circular Aperture defines an annular region which vignettes all rays which strike the surface inside of the minimum radius, and outside of the maximum radius. 
    If the ray is between the minimum and maximum radii, then the ray will be allowed to proceed. 

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param MinimumRadius: The minimum radius of the aperture, defaults to 0.0
    :type MinimumRadius: float, optional
    :param MaximumRadius: The maximum radius of the aperture, defaults to 10.0
    :type MaximumRadius: float, optional
    :param ApertureXDecenter: The decenter in the x-direction of the aperture, defaults to 0.0
    :type ApertureXDecenter: float, optional
    :param ApertureYDecenter: The decenter in the y-direction of the aperture, defaults to 0.0
    :type ApertureYDecenter: float, optional
    :return: The surface object.
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """

    SurfaceLDE    = self._convert_raw_surface_input_(in_Surface, return_index=False)
    settings      = self.LDE_GetApertureTypeSettings(in_Surface=SurfaceLDE, aperture_type='CircularAperture')
    settings._S_CircularAperture.MinimumRadius       = MinimumRadius
    settings._S_CircularAperture.MaximumRadius       = MaximumRadius
    settings._S_CircularAperture.ApertureXDecenter   = ApertureXDecenter
    settings._S_CircularAperture.ApertureYDecenter   = ApertureYDecenter
    SurfaceLDE.ApertureData.ChangeApertureTypeSettings(settings)
    return SurfaceLDE

def LDE_ChangeApertureToCircularObscuration(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], MinimumRadius:float=0.0, MaximumRadius:float=10.0, ApertureXDecenter:float=0.0, ApertureYDecenter:float=0.0)->ZOSAPI_Editors_LDE_ILDERow:
    """
    Changes the aperture of the surface to a circular *obscuration* one with specified radii.

    The Circular Obscuration is the complement of the Circular Aperture. 
    If the ray is NOT between the minimum and maximum radii, then the ray will be allowed to proceed.

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param MinimumRadius: The minimum radius of the aperture, defaults to 0.0
    :type MinimumRadius: float, optional
    :param MaximumRadius: The maximum radius of the aperture, defaults to 10.0
    :type MaximumRadius: float, optional
    :param ApertureXDecenter: The decenter in the x-direction of the aperture, defaults to 0.0
    :type ApertureXDecenter: float, optional
    :param ApertureYDecenter: The decenter in the y-direction of the aperture, defaults to 0.0
    :type ApertureYDecenter: float, optional
    :return: The surface object.
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """

    SurfaceLDE    = self._convert_raw_surface_input_(in_Surface, return_index=False)
    settings      = self.LDE_GetApertureTypeSettings(in_Surface=SurfaceLDE, aperture_type='CircularObscuration')
    settings._S_CircularObscuration.MinimumRadius       = MinimumRadius
    settings._S_CircularObscuration.MaximumRadius       = MaximumRadius
    settings._S_CircularObscuration.ApertureXDecenter   = ApertureXDecenter
    settings._S_CircularObscuration.ApertureYDecenter   = ApertureYDecenter
    SurfaceLDE.ApertureData.ChangeApertureTypeSettings(settings)
    return SurfaceLDE

def LDE_ChangeApertureToFloating(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow])->ZOSAPI_Editors_LDE_ILDERow:
    """
    Changes the aperture of the surface to a Floating one.
    
    A floating aperture is very similar to the circular aperture, except the minimum radius is always
    zero, and the maximum radius is always equal to the clear semi-diameter or semi-diameter of the surface. Since the
    clear semi-diameter or semi-diameter value may be adjusted by OpticStudio (when in automatic mode) the aperture
    value "floats" as the clear semi-diameter or semi-diameter value. The floating aperture is useful when macros or
    external programs use OpticStudio to trace rays that may lie outside of the default clear semi-diameters or
    semi-diameters, and these rays are to be vignetted.

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :return: The surface object.
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """

    SurfaceLDE    = self._convert_raw_surface_input_(in_Surface, return_index=False)
    settings      = self.LDE_GetApertureTypeSettings(in_Surface=SurfaceLDE, aperture_type='FloatingAperture')
    SurfaceLDE.ApertureData.ChangeApertureTypeSettings(settings)
    return SurfaceLDE

def LDE_SetSurfaceAsStop(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow])->None:
    """
    Sets the surface as the system stop.

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    """
    in_Surface = self._convert_raw_surface_input_(in_Surface, return_index=False)
    in_Surface.IsStop = True

def LDE_CheckIfSurfaceIsStop(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow])->bool:
    """
    Checks if the given surface is the stop of the system.

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :return: True if the surface is the system stop.
    :rtype: bool
    """
    in_Surface = self._convert_raw_surface_input_(in_Surface, return_index=False)
    return in_Surface.IsStop

def _LDE_GetSurfaceColumns_(self)->tuple:
    """
    Worker function which builds a surface's column names and underlying attributes.

    :return: the surface column call to access the enumerators, and the sting names of the columns
    :rtype: tuple
    """
    all_surface_columns = __LowLevelZemaxStringCheck__(self, self.ZOSAPI.Editors.LDE.SurfaceColumn)
    # # surface_columns = [x for x in all_surface_columns if 'Par' not in x]
    # This is just making a nicer order (to match Zemax GUI) of the above 
    surface_columns = ['Comment', 'Radius', 'Thickness', 'Material', 'Coating',
                        'SemiDiameter', 'ChipZone', 'MechanicalSemiDiameter', 'Conic', 'TCE']
    par_columns = [x for x in all_surface_columns if 'Par' in x]
    # Ensure 'ParXX' names are sorted by int in XX
    surface_columns = surface_columns + [y for x, y, in sorted(zip([int(x.strip('Par')) for x in par_columns], par_columns))]
    surface_column_calls = [getattr(self.ZOSAPI.Editors.LDE.SurfaceColumn, x) for x in surface_columns]
    return surface_column_calls, surface_columns


def _LDE_GetSurfaceCalls_(self, SurfaceLDE:ZOSAPI_Editors_LDE_ILDERow)->tuple:
    """
    Worker function which (invoking :func:`_LDE_GetSurfaceColumns_`) will return the base underlying column calls of a surface.

    :param SurfaceLDE: A surface object (not expected to be the index).
    :type SurfaceLDE: ZOSAPI_Editors_LDE_ILDERow
    :return: The column calls, and the column names as strings.
    :rtype: tuple
    """
    surface_column_calls, surface_columns = self._LDE_GetSurfaceColumns_()
    surfacecolumn_calls = [SurfaceLDE.GetSurfaceCell(x) for x in surface_column_calls]
    return surfacecolumn_calls, surface_columns

def LDE_GetSurfaceColumnEnum(self, in_str:str, in_Surface: Union[None, int, ZOSAPI_Editors_LDE_ILDERow]=None)->ZOSAPI_Editors_LDE_SurfaceColumn:
    """
    Returns the underlying ZOI-API enumerators of a LDE column matching the input string.

    If in_Surface is None, then assuming only searching for a default/base property or one named by 'par#'.
    If in_Surface is not None, then will search for the property in the specific surface by name and return the right enum (since different surface types have different names for their columns).

    If the given string is able to be matched to more than one column name, then the first column within the names will be given.

    :param in_str: The column, by name, to get the ZOI-API enumerator of.
    :type in_str: str
    :param in_Surface: The surface to change as an object or as an index, defaults to None
    :type in_Surface: Union[None, int, ZOSAPI_Editors_LDE_ILDERow], optional
    :return: the ZOI-API enumerator
    :rtype: ZOSAPI_Editors_LDE_SurfaceColumn
    """

    if in_Surface is None or 'par' in in_str.lower():
        return self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.LDE.SurfaceColumn, in_str)
    surface_column_calls, surface_columns = self._LDE_GetSurfaceCalls_(self._convert_raw_surface_input_(in_Surface, return_index=False))
    bool_mask = [in_str.lower() in x.Header.lower() for x in surface_column_calls]
    if np.any(bool_mask):
        return self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.LDE.SurfaceColumn, surface_columns[int(np.where(bool_mask)[0][0])])
    if self._verbose: cp('!@ly!@LDE_GetSurfaceColumnEnum :: Did not find [!@lm!@{}!@ly!@] in surface properties.'.format(in_str))

def LDE_GetAllColumnDataOfSurface(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow])->dict:
    """
    Gets all column data of a Sequential surface and returns it as a dict.

    This was made to reflect the functions of :func:`NCE_GetAllColumnDataOfObject` and 
    :func:`NCE_SetAllColumnDataOfObjectFromDict` which are for robustness in Non-sequential mode.
    However, unlike Non-sequential mode, Sequential mode seems to work as the API intended so you don't 
    need to use these lower level dict functions to adjust surface properties. 
    
    However, it is still very useful to set properties through this mechanism in python code.

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :return: dict of the surface's column data.
    :rtype: dict
    """

    surfacecolumn_calls, surface_columns = self._LDE_GetSurfaceCalls_(self._convert_raw_surface_input_(in_Surface, return_index=False))
    out = dict()
    for scall in surfacecolumn_calls:
        if '(unused)' in scall.Header and 'Par 0' not in scall.Header:
            break # Everything after this should be empty
        if '(unused)' in scall.Header:
            pass
        else:
            out[scall.Header] = scall.Value
    return out


def LDE_SetAllColumnDataOfSurfaceFromDict(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], SurfaceLDE_dict:dict)->None:
    """
    Sets all column data of a Sequential surface from a dict - usually the dict produced by :func:`LDE_GetAllColumnDataOfSurface` after being altered.
    
    This was made to reflect the functions of :func:`NCE_GetAllColumnDataOfObject` and 
    :func:`NCE_SetAllColumnDataOfObjectFromDict` which are for robustness in Non-sequential mode.
    However, unlike Non-sequential mode, Sequential mode seems to work as the API intended so you don't 
    need to use these lower level dict functions to adjust surface properties. 
    
    However, it is still very useful to set properties through this mechanism in python code.

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param SurfaceLDE_dict: Column properties and values to set for the surface.
    :type SurfaceLDE_dict: dict
    """
    surfacecolumn_calls, surface_columns = self._LDE_GetSurfaceCalls_(self._convert_raw_surface_input_(in_Surface, return_index=False))
    for scall in surfacecolumn_calls:
        if '(unused)' in scall.Header and 'Par 0' not in scall.Header:
            break # Everything after this should be empty
        if '(unused)' in scall.Header:
            pass
        elif SurfaceLDE_dict[scall.Header] != scall.Value:
            if isinstance(SurfaceLDE_dict[scall.Header], int):
                try:
                    scall.IntegerValue = SurfaceLDE_dict[scall.Header]
                except:
                    scall.Value = str(SurfaceLDE_dict[scall.Header]) # If fail, fall back to string input.
            else:
                if SurfaceLDE_dict[scall.Header] is not None:
                    scall.Value =  str(SurfaceLDE_dict[scall.Header])

def LDE_SetTiltDecenterOfSurface(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow],
                                 BeforeSurfaceDecenterX: float=0.0, BeforeSurfaceDecenterY=0.0,
                                 BeforeSurfaceTiltX:float=0.0, BeforeSurfaceTiltY:float=0.0, BeforeSurfaceTiltZ:float=0.0,
                                 AfterSurfaceDecenterX : float=0.0, AfterSurfaceDecenterY=0.0,
                                 AfterSurfaceTiltX:float=0.0, AfterSurfaceTiltY:float=0.0, AfterSurfaceTiltZ:float=0.0,
                                 BeforeSurfaceOrder:str='Decenter_Tilt', AfterSurfaceOrder:str='Decenter_Tilt')->ZOSAPI_Editors_LDE_ILDERow:
    """
    Sets the tilt and decenter properties of a surface.

    Surface tilts and decenters allow a change in the coordinate system to be implemented both before and after ray tracing to the surface. 
    Surface tilts and decenters are redundant with and very similar to coordinate breaks. 
    A surface tilt/decenter can be thought of as a coordinate break, followed by the surface, followed by another coordinate break.

    The advantage to using surface tilts and decenters is the elimination of "dummy" coordinate break surfaces in the Lens Data Editor. 
    This allows for a somewhat less cluttered display some users prefer. 
    The disadvantage of using the surface tilts and decenters is the current implementation does not support optimization of surface tilt and decenter data.

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param BeforeSurfaceDecenterX: Decenter in X before surface, defaults to 0.0
    :type BeforeSurfaceDecenterX: float, optional
    :param BeforeSurfaceDecenterY: Decenter in Y before surface, defaults to 0.0
    :type BeforeSurfaceDecenterY: float, optional
    :param BeforeSurfaceTiltX: Tilt in X before surface, defaults to 0.0
    :type BeforeSurfaceTiltX: float, optional
    :param BeforeSurfaceTiltY: Tilt in Y before surface, defaults to 0.0
    :type BeforeSurfaceTiltY: float, optional
    :param BeforeSurfaceTiltZ: Tilt in Z before surface, defaults to 0.0
    :type BeforeSurfaceTiltZ: float, optional
    :param AfterSurfaceDecenterX: Decenter in X after surface, defaults to 0.0
    :type AfterSurfaceDecenterX: float, optional
    :param AfterSurfaceDecenterY: Decenter in Y after surface, defaults to 0.0
    :type AfterSurfaceDecenterY: float, optional
    :param AfterSurfaceTiltX: Tilt in X after surface, defaults to 0.0
    :type AfterSurfaceTiltX: float, optional
    :param AfterSurfaceTiltY: Tilt in Y after surface, defaults to 0.0
    :type AfterSurfaceTiltY: float, optional
    :param AfterSurfaceTiltZ: Tilt in Z after surface, defaults to 0.0
    :type AfterSurfaceTiltZ: float, optional
    :param BeforeSurfaceOrder: Before surface order of decenters and tilts, defaults to 'Decenter_Tilt'
    :type BeforeSurfaceOrder: str, optional
    :param AfterSurfaceOrder: After surface order of decenters and tilts, defaults to 'Decenter_Tilt'
    :type AfterSurfaceOrder: str, optional
    :return: The object of the surface.
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """
    SurfaceLDE                                            = self._convert_raw_surface_input_(in_Surface, return_index=False)
    SurfaceLDE.TiltDecenterData.BeforeSurfaceOrder        = self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.LDE.TiltDecenterOrderType , BeforeSurfaceOrder)
    SurfaceLDE.TiltDecenterData.AfterSurfaceOrder         = self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.LDE.TiltDecenterOrderType , AfterSurfaceOrder)
    SurfaceLDE.TiltDecenterData.BeforeSurfaceDecenterX    = BeforeSurfaceDecenterX
    SurfaceLDE.TiltDecenterData.BeforeSurfaceDecenterY    = BeforeSurfaceDecenterY
    SurfaceLDE.TiltDecenterData.BeforeSurfaceTiltX        = BeforeSurfaceTiltX
    SurfaceLDE.TiltDecenterData.BeforeSurfaceTiltY        = BeforeSurfaceTiltY
    SurfaceLDE.TiltDecenterData.BeforeSurfaceTiltZ        = BeforeSurfaceTiltZ
    SurfaceLDE.TiltDecenterData.AfterSurfaceDecenterX     = AfterSurfaceDecenterX
    SurfaceLDE.TiltDecenterData.AfterSurfaceDecenterY     = AfterSurfaceDecenterY
    SurfaceLDE.TiltDecenterData.AfterSurfaceTiltX         = AfterSurfaceTiltX
    SurfaceLDE.TiltDecenterData.AfterSurfaceTiltY         = AfterSurfaceTiltY
    SurfaceLDE.TiltDecenterData.AfterSurfaceTiltZ         = AfterSurfaceTiltZ
    return SurfaceLDE

def LDE_SetTiltDecenterAfterSurfaceMode(self, in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], mode:Union[str, tuple[str, int]])->ZOSAPI_Editors_LDE_ILDERow:
    """
    This function is a compliment function to :func:`LDE_SetTiltDecenterOfSurface` and sets the "After surface mode".

    After the surface, the same set of operations may be performed in either order. 
    The values for the before and after decenters and tilts, and the order in which they are done, may be independent. 
    However, it is frequently useful to have the after tilts and decenter values be related to previous before values.
        
        - "explicit"
        - "pickup"
        - "reverse"
        - ('pickup', surface[int, ZOSAPI_Editors_LDE_ILDERow])
        - ('reverse', surface[int, ZOSAPI_Editors_LDE_ILDERow])

    Reversing values from a prior surface involves changing the order and picking up the tilt and decenter values from the target surface and reversing the sign.
    The coordinate system resulting from the before and after tilt and decenters will define the coordinate system for the next surface. 
    The thickness of a surface is the thickness in the new coordinate system after all the tilt and decenters are applied, measured along the resulting Z axis.

    :param in_Surface: The surface to change as an object or as an index.
    :type in_Surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param mode: One of the modes listed above.
    :type mode: Union[str, tuple[str, Union[int, ZOSAPI_Editors_LDE_ILDERow]]]
    :return: The surface object
    :rtype: ZOSAPI_Editors_LDE_ILDERow
    """
    SurfaceLDE = self._convert_raw_surface_input_(in_Surface, return_index=False)
    if isinstance(mode, str):
        if 'explicit' in mode.lower():
            SurfaceLDE.TiltDecenterData.SetAfterSurfaceModeExplicit()
        elif 'pickup' in mode.lower():
            SurfaceLDE.TiltDecenterData.SetAfterSurfaceModePickupThis()
        elif 'reverse' in mode.lower():
            SurfaceLDE.TiltDecenterData.SetAfterSurfaceModeReverseThis()
        else:
            cp('!@ly!@LDE_SetTiltDecenterAfterSurfaceMode :: mode [!@lm!@{}!@ly!@] not understood.'.format(str(mode)))
    elif isinstance(mode, tuple):
        try:
            if 'pickup' in str(mode[0]).lower():
                SurfaceLDE.TiltDecenterData.SetAfterSurfaceModePickup(self._convert_raw_surface_input_(mode[1], return_index=True))
            elif 'reverse' in str(mode[0]).lower():
                SurfaceLDE.TiltDecenterData.SetAfterSurfaceModeReverse(self._convert_raw_surface_input_(mode[1], return_index=True))
            else:
                cp('!@ly!@LDE_SetTiltDecenterAfterSurfaceMode :: mode [!@lm!@{}!@ly!@] not understood.'.format(str(mode[0])))
        except:
             cp('!@ly!@LDE_SetTiltDecenterAfterSurfaceMode :: Problem setting input [!@lm!@{}!@ly!@].'.format(str(mode)))
    else:
        cp('!@ly!@LDE_SetTiltDecenterAfterSurfaceMode :: Expected [!@lm!@string!@ly!@] or [!@lm!@tuple!@ly!@] as input. Got [!@lm!@{}!@ly!@].'.format(str(type(mode))))

def LDE_BuildRayTraceNormalizedUnpolarizedRays(self,
                                               Hx:np.ndarray=np.linspace(-1, 1, 10), 
                                               Hy:np.ndarray=np.linspace(-1, 1, 10), 
                                               Px:np.ndarray=np.linspace(-1, 1, 10),
                                               Py:np.ndarray=np.linspace(-1, 1, 10),
                                               ending_surface:Union[int, ZOSAPI_Editors_LDE_ILDERow]=None,
                                               wavelengths:Union[int, ZOSAPI_SystemData_IWavelength, list[int, ZOSAPI_SystemData_IWavelength], np.ndarray[int, ZOSAPI_SystemData_IWavelength]]=None,
                                               ray_type:str='Real',
                                               OPD_mode:str='None',)->xr.Dataset:
    """
    This function sets up custom `unpolarized` rays in Zemax's `normalized` coordiante system. 
    These rays are intended to be used in an skZemax sequential ray trace executed with :func:`LDE_RunRayTrace`. 
    
        In this system a single ray is defined by a starting position at the front of the optical system `(Hx, Hy)`,
        and a point on the entrence pupil to travel through `(Px, Py)`.

    A grid of rays - defined by `Hx` and `Hy` - are built in a normalized coordianate as input to the optical system.
    There are two normalized systems - set by :func:`Field_SetNormalization`:

    Radial:

        If the field normalization is radial, then the normalized field coordinates represent points on a unit circle. The radius
        of this unit circle, called the maximum radial field, is given by the radius of the field point farthest from the origin in
        field coordinates. The maximum radial field magnitude is then used to scale all fields to normalized field coordinates.
        Real field coordinates can be determined by multiplying the normalized coordinates, `Hx` and `Hy`, by the maximum
        radial field magnitude:

        :math:`f_x = (Hx)(F_r)`

        :math:`f_y = (Hy)(F_r)`

        where :math:`F_r` is the maximum radial field magnitude and :math:`f_x` and :math:`f_y` are the field coordinates in field units.

    Rectangular:

        If the field normalization is rectangular, then the normalized field coordinates represent points on a unit rectangle.
        The x and y direction widths of this unit rectangle, called the maximum x field and maximum y field, are defined by
        the largest absolute magnitudes of all the x and y field coordinates. The maximum x and y field magnitudes are then
        used to scale all fields to normalized field coordinates. Real field coordinates can be determined by multiplying the
        normalized coordinates

        :math:`f_x = (Hx)(F_x)`

        :math:`f_y = (Hy)(F_y)`

        where :math:`F_x` and :math:`F_x` are the x and y field magnitudes, and :math:`f_x` and :math:`f_y` are the field coordinates in field units.

    This function builds rays such that each - and every - ray defined in the `(Hx, Hy) grid` at the front is then traced through a positon of the 
    entrance pupil defined also by a normalized system `(Px, Py)`. Unlike the `(Hx, Hy)` coordiantes, the entrnce pupil is always treated as radial:

        The normalized pupil coordinate (0.0, 1.0) is always at the top of the pupil, and therefore defines a marginal ray. 
        The normalized pupil coordinate (0.0, 0.0) always goes through the center of the pupil, and therefore defines a chief ray.
        The radial size of the pupil is defined by the radius of the paraxial entrance pupil, unless ray aiming is turned on, 
        in which case the radial size of the pupil is given by the radial size of the stop. 

    This function will build rays for you in this system, based on the inputs of the `(Hx, Hy)` and `(Px, Py)` grids. 
    In building both grids the radial constraints (if applicable) are handled for you and any input with a magnitude greater than 1 are filtered. 

    A Final note on calulation of optical path difference (`OPD_mode`) - which can only be calculated when tracing rays all the way to the image surface:

        Computing the OPD takes additional time beyond that for regular ray tracing, and OpticStudio only performs this
        additional computation if requested to do so. Computing the OPD is also more complicated for the client program,
        which means two rays must be traced rather than just one. To compute OPD for an arbitrary ray, OpticStudio must trace the chief ray, 
        then the arbitrary ray, then subtract the phase of the two to get the OPD. 
        Rather than trace the same chief ray over and over, which is slow, usually the chief ray is traced
        once, and then the phase of the chief ray is subtracted from each subsequent ray.

        `None`: no OPD calculation will be performed. It will return the optical path as defined in the Single Ray Trace analysis. 
        That value can differ from other analyses at infinite conjugates.

        `Current`: calculate the OPD based on the current ray and the previously computed chief ray.

        `CurrentAndChief`: will first compute the chief ray, and then calculate the OPD for the current ray. 

    If `Current` is suppiled, then :func:`LDE_RunRayTrace` will use `CurrentAndChief` only on the first ray in a new set of `(Hx, Hy)` and/or the wavelength changes.

    :param Hx: An array of Hx points, defaults to np.linspace(-1, 1, 10)
    :type Hx: np.ndarray, optional
    :param Hy: An array of Hy points, defaults to np.linspace(-1, 1, 10)
    :type Hy: np.ndarray, optional
    :param Px: An array of Px points, defaults to np.linspace(-1, 1, 10)
    :type Px: np.ndarray, optional
    :param Py: An array of Py points, defaults to np.linspace(-1, 1, 10)
    :type Py: np.ndarray, optional
    :param ending_surface: The surface to trace the rays up to (object or as an index), defaults to None (takes the last surface)
    :type ending_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], optional
    :param wavelengths: Wavelength(s) of the system to trace (object or as an index), defaults to None (takes all currently configured wavelengths)
    :type wavelengths: Union[int, ZOSAPI_SystemData_IWavelength, list[int, ZOSAPI_SystemData_IWavelength], np.ndarray[int, ZOSAPI_SystemData_IWavelength]], optional
    :param ray_type: Type of ray tracing to do. Options are "Real" or "Paraxial". "Paraxial" applies small angle approximations to snell's law for speed where "Real" does not, defaults to "Real"
    :type ray_type: str, optional
    :param OPD_mode: The type of OPD scheme to apply (see desciprtion above), defaults to 'None'
    :type OPD_mode: str, optional
    :return: An xarray of rays ready to be traced by :func:`LDE_RunRayTrace`
    :rtype: xr.Dataset
    """
    if ending_surface is None:
        ending_surface = self.LDE_GetNumberOfSurfaces()-1
    else:
        ending_surface = self._convert_raw_surface_input_(ending_surface, return_index=True)
    if wavelengths is None:
        wavelengths_idx = np.arange(1, self.Wavelength_GetNumberOfWavelengths()+1, 1)
    elif not isinstance(wavelengths, np.ndarray) and not isinstance(wavelengths, list):
        wavelengths = np.array([wavelengths])
    wavelengths_idx = np.array([_convert_raw_wavelength_input_(self, x, return_index=True) for x in wavelengths])
    wavelengths_um  = np.array([self.Wavelength_GetWavelength(x).Wavelength for x in wavelengths_idx])
    HX, HY    = np.meshgrid(Hx, Hy)
    HX        = HX[np.abs(HX) <=1]
    HY        = HY[np.abs(HY) <=1]
    if 'Rect' not in Field_GetNormalization(self):
        radius    = HX**2 + HY**2
        HX        = HX[radius <= 1]
        HY        = HY[radius <= 1]
    # Normazlied pupil is always radial
    PX, PY    = np.meshgrid(Px, Py)
    PX        = PX[np.abs(PX) <=1]
    PY        = PY[np.abs(PY) <=1]
    radius    = PX**2 + PY**2
    PX        = PX[radius <= 1]
    PY        = PY[radius <= 1]
    return xr.Dataset(
        {
            'wavelengths_um'   : ('wvln', wavelengths_um.astype(float)),
            'Hx'               : ('ray_num', np.repeat(HX, PX.shape[0]).astype(float)),
            'Hy'               : ('ray_num', np.repeat(HY, PX.shape[0]).astype(float)),
            'Px'               : ('ray_num', np.tile(PX, HX.shape[0]).astype(float)),
            'Py'               : ('ray_num', np.tile(PY, HX.shape[0]).astype(float)),
        },
        coords =
        {
            "wavelengths_idx"   : ('wvln', wavelengths_idx.astype(int))
        },
        attrs={
            'ray_trace_type' : 'NormUnpol',
            'ending_surface' : str(int(ending_surface)),
            'ray_type'       : str(_CheckIfStringValidInDir_(self, self.ZOSAPI.Tools.RayTrace.RaysType, ray_type)),
            'OPD_mode'       : str(_CheckIfStringValidInDir_(self, self.ZOSAPI.Tools.RayTrace.OPDMode, OPD_mode))
        })
    


def LDE_RunRayTrace(self, ray_trace_rays:xr.Dataset=None, ray_read_chunk:int=1000):
    """
    This funcion executes a sequential ray trace.
    There are differnt definitions for a seqeutnal ray trace:

        - Normalized Unpolarized (NormUnpol)
        - Direct Unpolarized (DirectUnpol)
        - Normalized Polarized (NormPol)
        - Direct Polarized (DirectPol)

    The normalized/direct distinction consdiersdsda 
    
    according to settings/values given in an xarray.

    :param ray_trace_rays: _description_, defaults to None
    :type ray_trace_rays: xr.Dataset, optional
    :param ray_read_chunk: _description_, defaults to 1000
    :type ray_read_chunk: int, optional
    """
    if ray_trace_rays is None:
        ray_trace_rays = self.LDE_BuildRayTraceNormalizedUnpolarizedRays()
    opened_batch_ray_trace = self.TheSystem.Tools.OpenBatchRayTrace()
    desired_ray_trace_call = _CheckIfStringValidInDir_(self, opened_batch_ray_trace, ray_trace_rays.attrs['ray_trace_type'], extra_include_filter=['Create'], extra_exclude_filter=['NSC'])
    if 'CreateNormUnpol' in str(desired_ray_trace_call):
        ray_tracer = desired_ray_trace_call(ray_trace_rays.ray_num.shape[0], _CheckIfStringValidInDir_(self, self.ZOSAPI.Tools.RayTrace.RaysType, ray_trace_rays.attrs['ray_type']), int(ray_trace_rays.attrs['ending_surface']))
        dataReader = self.BatchRayTrace.ReadNormUnpolData(opened_batch_ray_trace, ray_tracer)
        
    dataReader.ClearData()
    if ray_read_chunk is None or ray_read_chunk > ray_trace_rays.ray_num.shape[0]:
        ray_read_chunk = ray_trace_rays.ray_num.shape[0]

    for wvidx in range(1, self.Wavelength_GetNumberOfWavelengths()+1, 1):
        dataReader.AddRay(wvidx, 
                          ray_trace_rays.Hx.values, ray_trace_rays.Hy.values, 
                          ray_trace_rays.Px.values, ray_trace_rays.Py.values, 
                          _CheckIfStringValidInDir_(self, self.ZOSAPI.Tools.RayTrace.OPDMode, ray_trace_rays.attrs['OPD_mode']))
    rayData       = dataReader.InitializeOutput(ray_read_chunk)
    isFinished    = False
    totalSegRead = 0
    while isFinished == False and rayData is not None:
        readSegments = dataReader.ReadNextBlock(rayData)
        if readSegments == 0:
            isFinished = True
        else:
            totalSegRead = totalSegRead + readSegments
            totalRaysRead = np.max(_ctype_to_numpy_(self, rayData.rayNumber, data_length=int(np.floor(readSegments/2)), data_type=np.long))



# raytrace = TheSystem.Tools.OpenBatchRayTrace();
# % GetDirectFieldCoordinates
# % Result is the Boolean output, "X, Y, Z, L, M, N" are the "out double" variables as defined in the syntax guide
# [result,X,Y,Z,L,M,N] = raytrace.GetDirectFieldCoordinates(wavenumber, ZOSAPI.Tools.RayTrace.RaysType.Real, hx, hy, px, py);
# % GetPhase 
# % Result is the Boolean output, "exr, exi, eyr, eyi, ezr, ezi" are the "out double" variables as defined in the syntax guide 
# [exr,exi,eyr,eyi,ezr,ezi] = raytrace.GetPhase(L, M, N, jx, jy, xPhaseDeg, yPhaseDeg, intensity); 
# raytrace.Close();