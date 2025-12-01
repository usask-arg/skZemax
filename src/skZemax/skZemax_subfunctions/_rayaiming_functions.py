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

    :param method: Ray aiming method to use (see  :func:`RayAiming_GetNamesOfAllAimingMethods`). Options are: 'Off', 'Paraxial', 'Real', defaults to 'Off'
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
    available_aiming_properties = [x for x in self.__LowLevelZemaxStringCheck__(self.TheSystem.SystemData.RayAiming, extra_exclude_filter='_') if 'Method' not in x]
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

    :param aimingProperty: Property of the ray aiming method to set, defaults to "UseRayAimingCache"
    :type aimingProperty: str, optional
    :param aimingValue: The value to set the aiming property to. To understand property functions and values please refer to Zemax documenting (pdf pages 150-154), defaults to True
    :type aimingValue: Union[float,int,bool], optional
    """
    _SetAttrByStringIfValid_(self, self.TheSystem.SystemData.RayAiming, aiming_property, aiming_value)
