from __future__ import annotations

import numpy as np

from skZemax.skZemax_subfunctions._c_print import c_print as cp
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import (
    __LowLevelZemaxStringCheck__,
    _convert_raw_input_worker_,
)

type ZOSAPI_SystemData_IWavelength = object  # <- ZOSAPI.SystemData.IWavelength # The actual module is referenced by the base PythonStandaloneApplication class.


def _convert_raw_wavelength_input_(
    self,
    in_wavelength: int | float | ZOSAPI_SystemData_IWavelength,
    return_index: bool = True,
) -> int | ZOSAPI_SystemData_IWavelength:
    # Handselling the "special" case where a micrometer is given
    if isinstance(in_wavelength, float):
        in_wavelength = self.Wavelength_GetWavelengthByMicrometers(
            wavelength_micrometers=in_wavelength, add_if_not_in_system=True
        )
    return _convert_raw_input_worker_(
        self,
        in_value=in_wavelength,
        object_type=self.ZOSAPI.SystemData.IWavelength,
        return_index=return_index,
    )


def Wavelength_GetNamesOfAllPresets(self, print_to_console: bool = False) -> list:
    """
    This function builds a list of all the the preset wavelengths configurations in Zemax.
    This can be useful to look up what one may want to code as input to functions like :func:`Wavelength_SelectWavelengthPreset`.

    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :return: A list of the names of all preset wavelengthss in Zemax.
    :rtype: list
    """
    wvln_presets = __LowLevelZemaxStringCheck__(
        self, in_obj=self.ZOSAPI.SystemData.WavelengthPreset
    )
    if print_to_console:
        cp(
            "\n!@lg!@Wavelength_GetNamesOfAllPresets :: Names of all Wavelength Presets:"
        )
        [cp("   !@lm!@" + str(x)) for x in wvln_presets]
        cp("\n")
    return wvln_presets


def Wavelength_SelectWavelengthPreset(self, preset: str = "d_0p587") -> None:
    """
    Configures the system's wavelengths to one of the named preset configurations within Zemax.

    See :func:`Wavelength_GetNamesOfAllPresets` to extract the names in python.

    If more than one preset could match the specified string, the first one sorted by ascending length, then alphabet, is taken.

    :param preset: Name of the preset to use, defaults to "d_0p587"
    :type preset: str, optional
    """
    wvln_presets = self.Wavelength_GetNamesOfAllPresets(print_to_console=False)
    bool_mask = [str(preset).lower() in x.lower() for x in wvln_presets]
    if np.any(bool_mask):
        preset_enum = self._CheckIfStringValidInDir_(
            self.ZOSAPI.SystemData.WavelengthPreset,
            str(wvln_presets[int(np.where(bool_mask)[0][0])]),
        )
        self.TheSystem.SystemData.Wavelengths.SelectWavelengthPreset(preset_enum)
    else:
        cp(
            f"!@ly!@Wavelength_SelectWavelengthPreset :: Wavelength preset [!@lm!@{preset}!@ly!@] not found."
        )


def Wavelength_GetNumberOfWavelengths(self) -> int:
    """
    Returns number of wavelengths in the system.

    :return: The number of wavelengths configured in the system.
    :rtype: int
    """
    return int(self.TheSystem.SystemData.Wavelengths.NumberOfWavelengths)


def Wavelength_GetAllSystemWavelengthsAsMicrometers(self) -> np.ndarray:
    """
    Returns an array of all the system wavelengths, ordered by their Zemax index, in units of micrometers.

    :return: The wavelengths configured in the system.
    :rtype: np.ndarray
    """
    return np.array(
        [
            self._convert_raw_wavelength_input_(x, return_index=False).Wavelength
            for x in range(1, self.Wavelength_GetNumberOfWavelengths() + 1, 1)
        ]
    )


def Wavelength_GetAllSystemWavelengthsWeights(self) -> np.ndarray:
    """
    Returns an array of all the system wavelength weights, ordered by their Zemax index.

    :return: The wavelength weights configured in the system.
    :rtype: np.ndarray
    """
    return np.array(
        [
            self._convert_raw_wavelength_input_(x, return_index=False).Weight
            for x in range(1, self.Wavelength_GetNumberOfWavelengths() + 1, 1)
        ]
    )


def Wavelength_GetWavelength(
    self, wavelengthNum: int = 1
) -> ZOSAPI_SystemData_IWavelength:
    """
    Gets the wavelength entry at index.

    :param wavelengthNum: Index of wavelength entry to lookup, defaults to 1
    :type wavelengthNum: int, optional
    :return: The object associated with that wavelength.
    :rtype: ZOSAPI_SystemData_IWavelength
    """
    wavelengthNum = int(wavelengthNum)
    if wavelengthNum <= self.Wavelength_GetNumberOfWavelengths() and wavelengthNum > 0:
        return self.TheSystem.SystemData.Wavelengths.GetWavelength(wavelengthNum)
    if self._verbose:
        cp(
            f"!@ly!@Wavelength_GetWavelength :: Asked for wavelength [!@lm!@{wavelengthNum}!@ly!@] but there are only !@lm!@{self.Wavelength_GetNumberOfWavelengths()}!@ly!@ wavelengths built."
        )
    return None


def Wavelength_GetWavelengthByMicrometers(
    self,
    wavelength_micrometers: float,
    add_if_not_in_system: bool = True,
    weight_of_added_wavelength: float = 1.0,
) -> ZOSAPI_SystemData_IWavelength:
    """
    Gets the wavelength entry by the micrometer value (instead of index value like :func:`Wavelength_GetWavelength`).
    By default behavior, the specified micrometer wavelength will be added if it is not found in the system and returned automatically.
    If this behavior is turned off and the wavelength is not found then None will be returned

    :param wavelength_micrometers: The wavelength in micrometers to lookup.
    :type wavelength_micrometers: float
    :param add_if_not_in_system: If True and the given wavelength is not found then it will be added to the system, defaults to True
    :type add_if_not_in_system: bool
    :param weight_of_added_wavelength: If wavelength is to be added to the system then this will be the assigned weight.
    :type weight_of_added_wavelength: bool
    :return: The object associated with the wavelength.
    :rtype: ZOSAPI_SystemData_IWavelength
    """
    index = np.where(
        np.isclose(
            wavelength_micrometers,
            self.Wavelength_GetAllSystemWavelengthsAsMicrometers(),
        )
    )[0]
    if len(index) > 0:
        # Found the wavelength
        return self.Wavelength_GetWavelength(
            index[0] + 1
        )  # `index` is indexed from zero but Zemax indexes wavelengths starting at 1.
    elif add_if_not_in_system:
        return self.Wavelength_AddWavelength(
            wavelength_micrometers=wavelength_micrometers,
            wavelength_weight=weight_of_added_wavelength,
        )
    else:
        return None


def Wavelength_RemoveWavelength(
    self, in_wavelength: int | ZOSAPI_SystemData_IWavelength
) -> bool:
    """
        Deletes/removes a wavelengths from the system

    :param in_wavelength: The wavelength to remove - either an index or the wavelength object.
    :type in_wavelength: Union[int, ZOSAPI_SystemData_IWavelength]
    :return: True if the wavelength is valid and there were at least two wavelengths in the system, else False.
    :rtype: bool
    """
    return self.TheSystem.SystemData.Wavelengths.RemoveWavelength(
        self._convert_raw_wavelength_input_(in_wavelength, return_index=True)
    )


def Wavelength_RemoveWavelengthByMicrometers(
    self, wavelength_micrometers: float
) -> bool:
    """
    Removes the wavelength entry by the micrometer value (instead of index or ZOSAPI_SystemData_IWavelength value like :func:`Wavelength_RemoveWavelength`).
    If wavelength doesn't exist then this function effectively does nothing.

    :param wavelength_micrometers: The wavelength in micrometers to remove.
    :type wavelength_micrometers: float
    :return: True if the wavelength is valid and there were at least two wavelengths in the system, else False.
    :rtype: ZOSAPI_SystemData_IWavelength
    """
    index = np.where(
        np.isclose(
            wavelength_micrometers,
            self.Wavelength_GetAllSystemWavelengthsAsMicrometers(),
        )
    )[0]
    if len(index) > 0:
        # Found the wavelength
        return self.Wavelength_RemoveWavelength(
            index[0] + 1
        )  # `index` is indexed from zero but Zemax indexes wavelengths starting at 1.
    else:
        return False


def Wavelength_RemoveAllButPrimaryWavelength(self) -> None:
    """
    Removes all wavelengths in the current system except the primary wavelength.

    :return: None
    :rtype: None
    """
    primary_wvln = self.Wavelength_GetPrimaryWavelength()
    microns = float(primary_wvln.Wavelength)
    weight = float(primary_wvln.Weight)
    while self.Wavelength_GetNumberOfWavelengths() > 1:
        self.Wavelength_RemoveWavelength(1)
    self.Wavelength_AddWavelength(
        wavelength_micrometers=microns, wavelength_weight=weight
    )
    self.Wavelength_RemoveWavelength(1)


def Wavelength_AddWavelength(
    self, wavelength_micrometers: float, wavelength_weight: float = 1.0
) -> ZOSAPI_SystemData_IWavelength:
    """
    Adds a new wavelength to the system.

    :param wavelength_micrometers: The wavelength - in microns - to add to the system.
    :type wavelength_micrometers: float
    :param wavelength_weight: Weight to give the wavelength, defaults to 1.0
    :type wavelength_weight: float, optional
    :return: The newly added wavelength object.
    :rtype: ZOSAPI_SystemData_IWavelength
    """
    return self.TheSystem.SystemData.Wavelengths.AddWavelength(
        float(wavelength_micrometers), float(wavelength_weight)
    )


def Wavelength_SetPrimaryWavelength(
    self, in_wavelength: int | ZOSAPI_SystemData_IWavelength
) -> ZOSAPI_SystemData_IWavelength:
    """
    Sets the wavelength as the primary one in the system

    :param in_wavelength: The wavelength to make primary - either an index or the wavelength object.
    :type in_wavelength: Union[int, ZOSAPI_SystemData_IWavelength]
    :return: The primary wavelength object.
    :rtype: ZOSAPI_SystemData_IWavelength
    """
    wavelength_object = self._convert_raw_wavelength_input_(
        in_wavelength, return_index=False
    )
    wavelength_object.MakePrimary()
    return wavelength_object


def Wavelength_GetPrimaryWavelength(self) -> ZOSAPI_SystemData_IWavelength:
    """
    Returns the wavelength which is the primary one in the system

    :return: The primary wavelength object.
    :rtype: ZOSAPI_SystemData_IWavelength
    """
    bool_primary = [
        self._convert_raw_wavelength_input_(x, return_index=False).IsPrimary
        for x in range(1, self.Wavelength_GetNumberOfWavelengths() + 1, 1)
    ]
    return self._convert_raw_wavelength_input_(
        np.argmax(bool_primary) + 1, return_index=False
    )


def Wavelength_GetPrimaryWavelengthAsMicrometers(self) -> float:
    """
    Returns the micrometer value of the wavelength which is the primary one in the system

    :return: The primary wavelength in micrometers.
    :rtype: float
    """
    return float(self.Wavelength_GetPrimaryWavelength().Wavelength)
