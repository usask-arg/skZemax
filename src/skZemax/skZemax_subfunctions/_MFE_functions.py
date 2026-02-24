from __future__ import annotations


import numpy as np

from skZemax.skZemax_subfunctions._c_print import c_print as cp
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import (
    _convert_raw_input_worker_,
)

type ZOSAPI_Editors_MFE_IMFERow = object  # <- ZOSAPI.Editors.MFE.IMFERow # The actual module is referenced by the base PythonStandaloneApplication class.


def _convert_raw_operand_input_(
    self, in_obj: int | ZOSAPI_Editors_MFE_IMFERow, return_index: bool = True
) -> int | ZOSAPI_Editors_MFE_IMFERow:
    return _convert_raw_input_worker_(
        self,
        in_value=in_obj,
        object_type=self.ZOSAPI.Editors.MFE.IMFERow,
        return_index=return_index,
    )


def MFE_GetNumberOfOperands(self) -> int:
    """
    Gets number of Merit function operators

    :return: The number of merit function operators
    :rtype: int
    """
    return int(self.TheSystem.MFE.get_NumberOfOperands())


def MFE_GetOperand(self, operandNum: int) -> ZOSAPI_Editors_MFE_IMFERow:
    """
    Gets an MFE Operand.

    :param operandNum: The index of the operand.
    :type operandNum: int
    :return: The operand object.
    :rtype: ZOSAPI_Editors_MFE_IMFERow
    """
    operandNum = int(operandNum)
    if operandNum <= self.MFE_GetNumberOfOperands() and operandNum > 0:
        return self.TheSystem.MFE.GetOperandAt(int(operandNum))
    if self._verbose:
        cp(
            f"!@ly!@MFE_GetOperand :: Asked for Operand [!@lm!@{operandNum}!@ly!@] but there are only !@lm!@{self.MFE_GetNumberOfOperands()}!@ly!@ operands built."
        )
    return None


def MFE_AddNewOperand(self) -> ZOSAPI_Editors_MFE_IMFERow:
    """
    Adds a new Operand and returns it.

    :return: The new MFE operand object
    :rtype: ZOSAPI_Editors_MFE_IMFERow
    """
    return self.TheSystem.MFE.AddOperand()


def MFE_InsertNewOperand(self, newOperand: int | ZOSAPI_Editors_MFE_IMFERow) -> None:
    """
    Inserts a new Operand and returns it.

    :param newOperand: The location to insert the new operand (can be an index or MFE object).
    :type newOperand: Union[int, ZOSAPI_Editors_MFE_IMFERow]
    :return: The newly inserted MFE object.
    :rtype: _type_
    """
    return self.TheSystem.MFE.InsertNewOperandAt(
        self._convert_raw_operand_input_(newOperand, return_index=True)
    )


def MFE_SetOperand(
    self,
    in_Operand: int | ZOSAPI_Editors_MFE_IMFERow,
    operand_type: str,
    target: int | str | float | None = None,
    weight: int | str | float | None = None,
    param1: int | str | float | None = None,
    param2: int | str | float | None = None,
    param3: int | str | float | None = None,
    param4: int | str | float | None = None,
    param5: int | str | float | None = None,
    param6: int | str | float | None = None,
    param7: int | str | float | None = None,
    param8: int | str | float | None = None,
    comment: int | str | float | None = None,
    value: int | str | float | None = None,
    contrib: int | str | float | None = None,
) -> None:
    """
    Configures a MFE operand. As :func:`MFE_GetOperandValues` discusses, a user is referred to the Zemax help pdf: Section 5.2.1.3. Optimization Operand.

    For all the param# inputs, if an int is given this function will attempt to explicitly set the property as an int, otherwise expects a string
    and will trust Zemax API knows how to handle the input (as well as the user for giving good input vs operand type).

    This function just maps the operand fields to the correct cells

    :param in_Operand: The MFE operand (can be index or object)
    :type in_Operand: Union[int, ZOSAPI_Editors_MFE_IMFERow]
    :param operand_type: a string identifying the optimization (see Section 5.2.1.3)
    :type operand_type: str
    :param target: operand target input, defaults to None
    :type target: Union[int,str,float], optional
    :param weight: operand weight input, defaults to None
    :type weight: Union[int,str,float], optional
    :param param1: operand param1 input, defaults to None
    :type param1: Union[int,str,float], optional
    :param param2: operand param2 input, defaults to None
    :type param2: Union[int,str,float], optional
    :param param3: operand param3 input, defaults to None
    :type param3: Union[int,str,float], optional
    :param param4: operand param4 input, defaults to None
    :type param4: Union[int,str,float], optional
    :param param5: operand param5 input, defaults to None
    :type param5: Union[int,str,float], optional
    :param param6: operand param6 input, defaults to None
    :type param6: Union[int,str,float], optional
    :param param7: operand param7 input, defaults to None
    :type param7: Union[int,str,float], optional
    :param param8: operand param8 input, defaults to None
    :type param8: Union[int,str,float], optional
    :param comment: operand description, defaults to None
    :type comment: Union[int,str,float], optional
    :param value: operand value input, defaults to None
    :type value: Union[int,str,float], optional
    :param contrib: operand contrib input, defaults to None
    :type contrib: Union[int,str,float], optional
    """

    def _assign_(invalue, in_cell):
        if invalue is not None:
            if isinstance(invalue, int):
                try:
                    in_Operand.GetCellAt(in_cell).IntegerValue = invalue
                except Exception:
                    in_Operand.GetCellAt(in_cell).Value = str(
                        invalue
                    )  # If fail, fall back to string input.
            else:
                in_Operand.GetCellAt(in_cell).Value = str(invalue)

    in_Operand = self._convert_raw_operand_input_(in_Operand, return_index=False)
    in_Operand.ChangeType(
        self._CheckIfStringValidInDir_(
            self.ZOSAPI.Editors.MFE.MeritOperandType, operand_type, check_if_upper=True
        )
    )
    _assign_(comment, 1)
    _assign_(param1, 2)
    _assign_(param2, 3)
    _assign_(param3, 4)
    _assign_(param4, 5)
    _assign_(param5, 6)
    _assign_(param6, 7)
    _assign_(param7, 8)
    _assign_(param8, 9)
    _assign_(target, 10)
    _assign_(weight, 11)
    _assign_(value, 12)
    _assign_(contrib, 13)


def MFE_GetOperandValues(
    self, operand_type: str, param_array: np.ndarray
) -> np.ndarray:
    """
    This function supports getting direct access to retrieving/queuing operand values.

    This is a pretty low level function and can access a lot of properties with much use outside of only a "solver/optimize" context.

    There are many (...many...) different operand types which require different inputs to the parameters.
    Because of the exceeding many options, along with their short and ambiguous names within Zemax and the ZOS-API, there is little
    point to making any useful skZemax tool to aid a user in the lookup of these operands.

    Therefore, this is one of the functions which trusts the user to look up Zemax document on the operands and work out how to call this function.
    Section 5.2.1.3. Optimization Operand in the main Zemax help pdf is the best resource.
    A further helpful example can be found in `Examples/example07.py` where it is used to get the global rotation matrix of a surface element.

    :param operand_type: A string indicating the operand (see Zemax help pdf: Section 5.2.1.3. Optimization Operand).
    :type operand_type: str
    :param param_array: Expected as a 2d array which is Nx8 in size, where N is the number of parameter configurations to use in queuing/retrieval of the operand value.
    :type param_array: np.ndarray
    :return: an array of size N, where each index of the returned array is the answer to the Nth que of the param_array.
    :rtype: np.ndarray
    """

    if param_array.shape[1] != 8:
        cp(
            "!@ly!@MFE_GetOperandValues :: Expected 8 parameters for each configuration along the first dimension of given array. Found [!@lm!@%i!@lg!@] instead."
            % param_array.shape[1]
        )
        return None
    out = np.zeros(param_array.shape[0]) * np.nan
    for idx, config in enumerate(param_array):
        out[idx] = self.TheSystem.MFE.GetOperandValue(
            self._CheckIfStringValidInDir_(
                self.ZOSAPI.Editors.MFE.MeritOperandType,
                operand_type,
                check_if_upper=True,
            ),
            int(config[0]),
            int(config[1]),
            float(config[2]),
            float(config[3]),
            float(config[4]),
            float(config[5]),
            float(config[6]),
            float(config[7]),
        )
    return out
