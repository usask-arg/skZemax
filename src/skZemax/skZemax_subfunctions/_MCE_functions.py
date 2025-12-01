from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import _convert_raw_input_worker_, __LowLevelZemaxStringCheck__
from typing import Union
from skZemax.skZemax_subfunctions._c_print import c_print as cp

type ZOSAPI_Editors_MCE_IMCERow = object #<- ZOSAPI.Editors.MCE.IMCERow # The actual module is referenced by the base PythonStandaloneApplication class.

def MCE_GetNumberOfConfigs(self)->int:
    """
    Returns the total number of current configurations

    :return: The number of configurations within the current Zemax file.
    :rtype: int
    """
    return int(self.TheSystem.MCE.NumberOfConfigurations)

def MCE_GetCurrentConfig(self)->int:
    """
    Gets the currently active configuration index.

    :return: The index of the current active configuration.
    :rtype: int
    """
    return int(self.TheSystem.MCE.CurrentConfiguration)

def MCE_AddConfig(self, with_pickups:bool=False):
    """
    Adds a new Zemax Configuration.

    :param with_pickups: if set to true, add pickups from the previous configuration, defaults to False
    :type with_pickups: bool, optional
    """
    self.TheSystem.MCE.AddConfiguration(with_pickups)

def MCE_InsertConfig(self, config_idx:int, with_pickups:bool=False):
    """
    Inserts a new Zemax Configuration at index.

    :param config_idx: if set to true, add pickups from the previous configuration, defaults to False
    :type config_idx: int
    :param with_pickups: _description_, defaults to False
    :type with_pickups: bool, optional
    """
    self.TheSystem.MCE.InsertConfiguration(config_idx, with_pickups)


def MCE_DeleteConfig(self, config_idx:int):
    """
    Deletes a Zemax Configuration.

    :param config_idx: The index of the MCE to delete.
    :type config_idx: int
    """
    if config_idx <= self.MCE_GetNumberOfConfigs() and config_idx > 0:
        self.TheSystem.MCE.DeleteConfiguration(config_idx)
    else:
        if self._verbose: cp('!@ly!@MCE_SetActiveConfig :: Asked for configuration [!@lm!@{}!@ly!@] but there are only !@lm!@1-{}!@ly!@ configurations built.'.format(config_idx, self.MCE_GetNumberOfConfigs()))
        return

def MCE_MakeAllSingleConfig(self, deleteMFEOperands:bool=False):
    """
    Removes all configurations and operands. Reduces everything back to a single configuration.

    :param deleteMFEOperands: If True, merit function operands of the configurations will be removed, else MFE operands will remain, defaults to False
    :type deleteMFEOperands: bool, optional
    """
    self.TheSystem.MCE.MakeSingleConfigurationOpt(deleteMFEOperands)

def MCE_SetActiveConfig(self, config_idx:int):
    """
    Sets the active Zemax Configuration.

    :param config_idx: Index of the configuration to make active
    :type config_idx: int
    """
    if config_idx <= self.MCE_GetNumberOfConfigs() and config_idx > 0:
        self.TheSystem.MCE.SetCurrentConfiguration(config_idx)
    else:
        if self._verbose: cp('!@ly!@MCE_SetActiveConfig :: Asked for configuration [!@lm!@{}!@ly!@] but there are only !@lm!@1-{}!@ly!@ configurations built.'.format(config_idx, self.MCE_GetNumberOfConfigs()))
        return

def _convert_raw_MCEOper_input_(self, in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow], return_index:bool=True)->Union[int, ZOSAPI_Editors_MCE_IMCERow]:
    return _convert_raw_input_worker_(self, in_value=in_op, object_type=self.ZOSAPI.Editors.MCE.IMCERow, return_index=return_index)

def MCE_GetCurrentNumOperands(self)->int:
    """
    Gets the total number of multi-configuration operands in the current configuration.

    :return: The total number of operands
    :rtype: int
    """
    return int(self.TheSystem.MCE.NumberOfOperands)

def MCE_GetConfigOperand(self, op_idx:int)->ZOSAPI_Editors_MCE_IMCERow:
    """
    Gets the multi-configuration operand at index.

    :param op_idx: The index of the multi-configuration operand
    :type op_idx: int
    :return: The operand object
    :rtype: ZOSAPI_Editors_MCE_IMCERow
    """
    return self.TheSystem.MCE.GetOperandAt(op_idx)

def MCE_AddConfigOperand(self)->ZOSAPI_Editors_MCE_IMCERow:
    """
    Adds a new multi-configuration operand to the end of the configuration editor.

    :return: The operand object
    :rtype: ZOSAPI_Editors_MCE_IMCERow
    """
    return self.TheSystem.MCE.AddOperand()

def MCE_DeleteConfigOperand(self, in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow]):
    """
    Deletes an multi-configuration operand.

    :param in_op: The multi-configuration operand to delete (object or index).
    :type in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow]
    """
    self.TheSystem.MCE.RemoveOperandAt(self._convert_raw_MCEOper_input_(in_op, return_index=True))

def MCE_InsertConfigOperand(self, in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow])->ZOSAPI_Editors_MCE_IMCERow:
    """
    Inserts a new multi-configuration operand.

    :param in_op: The multi-configuration operand to delete (object or index).
    :type in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow]
    :return: The new operand object.
    :rtype: ZOSAPI_Editors_MCE_IMCERow
    """
    return self.TheSystem.MCE.InsertNewOperandAt(self._convert_raw_MCEOper_input_(in_op, return_index=True))

def MCE_SetOperand(self, in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow],
                   operand_type:str,
                   param1   : Union[int,str,float]=0,
                   param2   : Union[int,str,float]=0,
                   param3   : Union[int,str,float]=0,
                   operand_values: list[tuple]=None,
                   )->ZOSAPI_Editors_MCE_IMCERow:
    """
    Configures the multi-configuration operand. A user is directed to read Zemax documentation (help doc and API doc) - in particular 2.3.4.1. Multi-Configuration Operands.
    
    operand_type: There are *a lot* of them, just read the documents.
    param#: 
    operand_values: 

    :param in_op: A string identifying the configuration operand. 
    :type in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow]
    :param operand_type: _description_
    :type operand_type: str
    :param param1: Meaning (if any) comes from operand input (see the docs). 0 seems to be a "null" default of the MCE, defaults to 0
    :type param1: Union[int,str,float], optional
    :param param2: Meaning (if any) comes from operand input (see the docs). 0 seems to be a "null" default of the MCE, defaults to 0
    :type param2: Union[int,str,float], optional
    :param param3: Meaning (if any) comes from operand input (see the docs). 0 seems to be a "null" default of the MCE, defaults to 0
    :type param3: Union[int,str,float], optional
    :param operand_values: list of tuples where each tuple is (configuration_number:int, value_of_this_operand:Union[int,str,float]), defaults to None
    :type operand_values: list[tuple], optional
    :return: The operand object
    :rtype: ZOSAPI_Editors_MCE_IMCERow
    """
    def _assign_(invalue, in_cell):
        in_cell = int(in_cell)
        if in_cell <= num_of_configs and in_cell > 0:
            if isinstance(invalue, int):
                try:
                    in_op.GetOperandCell(in_cell).IntegerValue = invalue
                except:
                    in_op.GetOperandCell(in_cell).Value = str(invalue) # If fail, fall back to string input.
            elif isinstance(invalue, float):
                try:
                    in_op.GetOperandCell(in_cell).DoubleValue = invalue
                except:
                    in_op.GetOperandCell(in_cell).Value = str(invalue) # If fail, fall back to string input.
            else:
                in_op.GetOperandCell(in_cell).Value = str(invalue)
        else:
            if self._verbose: cp('!@ly!@MCE_SetOperand :: Attempted to adjust configuration'
            ' [!@lm!@%i!@ly!@] but there are only !@lm!@1-%i!@ly!@ configurations built.' % (in_cell, self.MCE_GetNumberOfConfigs()))
    num_of_configs =  self.MCE_GetNumberOfConfigs()
    in_op = self._convert_raw_MCEOper_input_(in_op, return_index=False)
    in_op.ChangeType(self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.MCE.MultiConfigOperandType, operand_type, check_if_upper=True))
    in_op.Param1 = param1
    in_op.Param2 = param2
    in_op.Param3 = param3
    if operand_values is not None:
        for conf_num, conf_value in operand_values:
            _assign_(conf_value, conf_num)
    return in_op
