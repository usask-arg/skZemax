from typing import Union
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import _convert_raw_input_worker_, __LowLevelZemaxStringCheck__, _CheckIfStringValidInDir_, _SetAttrByStringIfValid_
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

    :param field_x: Field X parameter. Typically angle (degrees) in the x-axis. See :func:`Field_SetFieldType`.
    :type field_x: float
    :param field_y: Field Y parameter. Typically angle (degrees) in the y-axis. See :func:`Field_SetFieldType`.
    :type field_y: float
    :param field_weight: Field weight, defaults to 1.0
    :type field_weight: float, optional
    :return: The new field object
    :rtype: ZOSAPI_SystemData_IField
    """
    return self.TheSystem.SystemData.Fields.AddField(float(field_x), float(field_y), float(field_weight))

def Field_GetAllDataOfField(self, in_field: Union[int, ZOSAPI_SystemData_IField])->dict:
    """
    Gets all column data of a Field object and returns it as a dict.

    :param in_field: The Field - either the index or the object.
    :type in_field: Union[int, ZOSAPI_SystemData_IField]
    :return: dict of all Field's properties
    :rtype: dict
    """
    field_obj = self._convert_raw_field_input_(in_field, return_index=False)
    out = dict()
    for key in __LowLevelZemaxStringCheck__(self, self.ZOSAPI.SystemData.FieldColumn, extra_exclude_filter=['get', 'Get', 'set', 'Set', 'Solve', 'solve']):
        out[key] = _CheckIfStringValidInDir_(self, field_obj, key, extra_exclude_filter=['get', 'Get', 'set', 'Set', 'Solve', 'solve'])
    return out

def Field_SetAllDataOfFieldFromDict(self, in_field: Union[int, ZOSAPI_SystemData_IField], Field_dict:dict)->None:
    """
    Sets all column data of a Field object and returns it as a dict.

    :param in_field: The Field - either the index or the object.
    :type in_field: Union[int, ZOSAPI_SystemData_IField]
    :param Field_dict: dict of Field properties to set (i.e. :func:`Field_GetDataOfField`)
    :type Field_dict: dict
    :return: _description_
    :rtype: dict
    """
    field_obj = self._convert_raw_field_input_(in_field, return_index=False)
    for key in Field_dict.keys():
        _SetAttrByStringIfValid_(self, field_obj, key, Field_dict[key], extra_exclude_filter=['get', 'Get', 'set', 'Set', 'Solve', 'solve'])

def Field_SetFieldType(self, field_type:str='Angle'):
    """
    Sets the system field type to one of the following options:

        - Angle (default)
            Angle Field angles are always in degrees. The angles are measured with respect to the object space z axis and the
            paraxial entrance pupil position on the object space z axis. Positive field angles imply positive slope for the ray in
            that direction, and thus refer to negative coordinates on distant objects.
        - ObjectHeight
            Object Height Measured in lens units.
        - ParaxialImageHeight
            Paraxial Image Measured in lens units. When paraxial image heights are used as the field definition, the heights
            are the paraxial image coordinates of the primary wavelength chief ray on the paraxial image surface, and if the
            optical system has distortion, then the real chief rays will be at different locations.
        - RealImageHeight
            Real Image Measured in lens units. When real image heights are used as the field definition, the heights are the real
            ray coordinates of the primary wavelength chief ray on the image surface
        - TheodoliteAngle
            If the field definition is Theodolite Angle in the Field Data Editor, the X/Y Field Width indicates the Azimuth/Elevation
            angle in degrees, respectively.

    :param field_type: _description_, defaults to 'Angle'
    :type field_type: str, optional
    """
    self.TheSystem.SystemData.Fields.ConvertToFieldType(_CheckIfStringValidInDir_(self, self.ZOSAPI.SystemData.FieldType, field_type))

def Field_GetFieldType(self)->str:
    """
    Returns the currently set field type (see :func:`Field_SetFieldType`). 

    :return: Name of the currently set field type.
    :rtype: str
    """
    return str(self.TheSystem.SystemData.Fields.GetFieldType())

def Field_SetVignettingFactors(self)->None:
    """
    Recomputes the vignetting factors for each field based upon the current lens data. Vignetting factors
    (VDX, VDY, VCX, VCY) are coefficients which describe the apparent entrance pupil size and location for different field
    positions. These vignetting factors should be left at zero if there is no vignetting in the system. 
    The set vignetting algorithm estimates the vignetting decenter and compression factors so that the four 
    marginal rays in the top, bottom, left, and right edges of the pupil pass within the apertures of each surface. 
    Only the primary wavelength is used.
    """
    self.TheSystem.SystemData.Fields.SetVignetting()

def Field_ClearVignettingFactors(self)->None:
    """
    Sets vignetting factors to zero.
    """
    self.TheSystem.SystemData.Fields.ClearVignetting()

def Field_SetNormalization(self, normalization:str='Radial')->None:
    """
    Sets the type of field normalization to apply.
    This is relevant for specifying rays in normalized normalized x-field coordinate `Hx` and normalized y-field coordinate `Hy`.

    See :func:`LDE_BuildRayTraceNormalizedUnpolarizedRays` for a more in-depth description.
     
    Options are:

    - Radial
        `Hx^2 + Hy^2 <= 1`
    - Rectangular
        `abs(Hx) <= 1` and `abs(Hy) <= 1`

    :param normalization: Type of normalization to apply when specifying ray coordinates `Hx` and `Hy`, defaults to 'Radial'
    :type normalization: str, optional
    """
    norm = _CheckIfStringValidInDir_(self, self.ZOSAPI.SystemData.FieldNormalizationType, normalization)
    if norm is not None:
        self.TheSystem.SystemData.Fields.Normalization = norm
    
def Field_GetNormalization(self)->str:
    """
    Returns the currently set normalization. See :func:`Field_SetNormalization`.

    :return: The name of the set normalization.
    :rtype: str
    """
    return str(self.TheSystem.SystemData.Fields.get_Normalization())