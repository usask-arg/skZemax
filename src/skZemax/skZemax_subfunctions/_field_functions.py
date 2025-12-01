from typing import Union
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import _convert_raw_input_worker_
from skZemax.skZemax_subfunctions._c_print import c_print as cp

type ZOSAPI_SystemData_IField = object #<- ZOSAPI.SystemData.IField # The actual module is referenced by the base PythonStandaloneApplication class.

def _convert_raw_field_input_(self, in_field: Union[int, ZOSAPI_SystemData_IField], return_index:bool=True)->Union[int, ZOSAPI_SystemData_IField]:
    return _convert_raw_input_worker_(self, in_value=in_field, object_type=self.ZOSAPI.SystemData.IField, return_index=return_index)

def Fields_GetNumberOfFields(self)->int:
    """
    Returns the total number of current field angles

    :return: The total number of field angles
    :rtype: int
    """

    return int(self.TheSystem.SystemData.Fields.get_NumberOfFields())

def Field_GetField(self, fieldNum:int=1)->ZOSAPI_SystemData_IField:
    """
    Returns the Field object at the given field index

    :param fieldNum: The field index, defaults to 1
    :type fieldNum: int, optional
    :return: The field object at index.
    :rtype: ZOSAPI_SystemData_IField
    """

    fieldNum = int(fieldNum)
    if fieldNum <= self.Fields_GetNumberOfFields() and fieldNum > 0:
        return self.TheSystem.SystemData.Fields.GetField(fieldNum)
    if self._verbose: 
        cp('!@ly!@Field_GetField :: Asked for field [!@lm!@{}!@ly!@] but there are only !@lm!@{}!@ly!@ fields built.'.format(fieldNum, self.Fields_GetNumberOfFields()))
    return None

def Field_DeleteField(self, in_field: Union[int, ZOSAPI_SystemData_IField])->None:
    """
    Deletes a field.

    :param in_field: Field to delete - either the index or the object.
    :type in_field: Union[int, ZOSAPI_SystemData_IField]
    """

    self.TheSystem.SystemData.Fields.DeleteFieldAt(self._convert_raw_field_input_(in_field, return_index=True))

def Fields_AddField(self, field_x:float, field_y:float, field_weight:float=1.0)->ZOSAPI_SystemData_IField:
    """
    Adds a new field.

    :param field_x: Field angle (degrees) in the x-axis.
    :type field_x: float
    :param field_y: Field angle (degrees) in the y-axis.
    :type field_y: float
    :param field_weight: Field weight, defaults to 1.0
    :type field_weight: float, optional
    :return: The new field object
    :rtype: ZOSAPI_SystemData_IField
    """

    return self.TheSystem.SystemData.Fields.AddField(float(field_x), float(field_y), float(field_weight))

