from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import __LowLevelZemaxStringCheck__, _SetAttrByStringIfValid_
from typing import Union
import numpy as np
from skZemax.skZemax_subfunctions._c_print import c_print as cp

def RayAiming_GetNamesOfAllAimingMethods(self, print_to_console:bool=False)->list:
    """
    This function builds a list of all the ray aiming methods that Zemax is aware of.
    This can be useful to look up what one may want to code as input to functions like :func:`RayAiming_SetAimingMethod`.

    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :return: A list of the names of all ray aiming methods the ZOS-API knows.
    :rtype: list
    """
    available_aiming_methods = __LowLevelZemaxStringCheck__(self, in_obj=self.ZOSAPI.SystemData.RayAimingMethod)
    if print_to_console:
        cp('\n!@lg!@RayAiming_GetNamesOfAllAimingMethods :: Names of all Ray Aiming Methods:')
        [cp('   !@lm!@' + str(x)) for x in available_aiming_methods]
        cp('\n')
    return available_aiming_methods

def RayAiming_SetAimingMethod(self, method:str='Off'):
    """
    Special property of the Ray Aiming properties. This one sets the Ray Aiming mode itself.
    Options are:
        - "Off": If ray aiming is off, Zemax will use the paraxial entrance pupil size and location determined by the aperture settings and calculated at the primary wavelength on axis for launching rays from the object surface.
        - "Paraxial": Paraxial rays are well behaved and paraxial definitions are commonly used for most first-order system properties.
        - "Real": For real rays to have the object space properties defined by the system aperture, use real rays instead of paraxial rays to determine the stop radius.

    See 2.1.1.7. Ray Aiming in the Zemax pdf help document for more detail

    :param method: Ray aiming method to use (see options above and/or :func:`RayAiming_GetNamesOfAllAimingMethods`), defaults to 'Off'
    :type method: str, optional
    """
    available_aiming_methods = self.RayAiming_GetNamesOfAllAimingMethods(print_to_console=False)
    bool_mask = [str(method).lower() in x.lower() for x in available_aiming_methods]
    if np.any(bool_mask):
        self.TheSystem.SystemData.RayAiming.RayAiming = self._CheckIfStringValidInDir_(self.ZOSAPI.SystemData.RayAimingMethod, str(available_aiming_methods[int(np.where(bool_mask)[0][0])]))
    else:
        cp('!@ly!@RayAiming_SetAimingMethod :: Ray aiming method [!@lm!@{}!@ly!@] not found.'.format(method))

def RayAiming_GetNamesOfAllAimingProperties(self, print_to_console:bool=False)->list:
    """
    This function builds a list of all the ray aiming properties that Zemax is aware of.
    This can be useful to look up what one may want to code as input to functions like :func:`RayAiming_SetAimingProperty`.

    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :return: A list of the names of all ray aiming properties the ZOS-API knows.
    :rtype: list
    """
    available_aiming_properties = [x for x in __LowLevelZemaxStringCheck__(self, self.TheSystem.SystemData.RayAiming, extra_exclude_filter='_') if ('Method' not in x) and ('RayAiming' != x)]
    if print_to_console:
        cp('\n!@lg!@RayAiming_GetNamesOfAllAimingProperties :: Names of all Ray Aiming Properties:')
        [cp('   !@lm!@' + str(x)) for x in available_aiming_properties]
        cp('\n')
    return available_aiming_properties

def RayAiming_SetAimingProperty(self, aiming_property:str="UseRayAimingCache", aiming_value:Union[float,int,bool]=True):
    """
    Sets a property of the Ray Aiming system. 
    There is a soft assumption that the correct method is already set for what you want to do.
    See :func:`RayAiming_SetAimingMethod` for setting the method.

    Properties are:
        - "UseRayAimingCache": If True, Zemax caches ray aiming coordinates so that new ray traces take advantage of previous iterations of the ray tracing algorithm
        - "UseRobustRayAiming": If True, Zemax uses a more reliable, but slower algorithm for aiming rays.
        - "ScalePupilShiftFactorsByField": If True, the x and y pupil shift values are also scaled with field, otherwise, the x and y shift values are used for all fields without any scaling. All shifts are in lens units.
        - "AutomaticallyCalculatePupilShiftsIsChecked":  When True, OpticStudio will automatically calculate the difference in location between the real and paraxial entrance pupils in order to determine the value for the pupil shift factors
        - "PupilShiftX": Rough guess in X as to how much the pupil has been shifted and compressed with respect to the paraxial pupil
        - "PupilShiftY": Rough guess in Y as to how much the pupil has been shifted and compressed with respect to the paraxial pupil 
        - "PupilShiftZ": Rough guess in Z as to how much the pupil has been shifted and compressed with respect to the paraxial pupil
        - "PupilCompressX": The X compress value is used to change the relative coordinates on the paraxial entrance pupil to start the iteration. A value of zero means no compress, while a value of 0.1 indicates the pupil is compressed 10 percent
        - "PupilCompressY": The Y compress value is used to change the relative coordinates on the paraxial entrance pupil to start the iteration. A value of zero means no compress, while a value of 0.1 indicates the pupil is compressed 10 percent
        - "UseEnhancedRayAiming": If selected, the Enhanced Ray Aiming algorithm is used. See 2.1.1.7. Ray Aiming in the Zemax pdf help document for more detail.
        - "UseFallBackSearchDuringCacheSetup": This option can be used to improve the Enhanced Ray Aiming for certain off axis or aspherical systems where the Enhanced Ray Algorithm performs less well. Recommended to leave this option False unless there are problems in ray aiming.
        - "UseAdvancedConvergence": This option can be used to improve the Enhanced Ray Aiming algorithm for systems substantial rotations around the z-axis although it may improve ray tracing in other types of systems
        - "NumStepsCacheSetup": Choose the number of steps used during the Cache Setup for Enhanced Ray Aiming. Recommended value of 10. Higher number of steps can improve stability but will reduce speed of the ray aiming calculations

    See 2.1.1.7. Ray Aiming in the Zemax pdf help document for more detail

    :param aimingProperty: Property of the ray aiming method to set, defaults to "UseRayAimingCache"
    :type aimingProperty: str, optional
    :param aimingValue: The value to set the aiming property to. To understand property functions and values please refer to Zemax documenting (pdf pages 150-154), defaults to True
    :type aimingValue: Union[float,int,bool], optional
    """
    available_aiming_props = self.RayAiming_GetNamesOfAllAimingProperties(print_to_console=False)
    bool_mask = [str(aiming_property).lower() in x.lower() for x in available_aiming_props]
    if np.any(bool_mask):
        _SetAttrByStringIfValid_(self, self.TheSystem.SystemData.RayAiming, str(available_aiming_props[int(np.where(bool_mask)[0][0])]), aiming_value)
    else:
        cp('!@ly!@RayAiming_SetAimingProperty :: Ray aiming property [!@lm!@{}!@ly!@] not found.'.format(aiming_property))
