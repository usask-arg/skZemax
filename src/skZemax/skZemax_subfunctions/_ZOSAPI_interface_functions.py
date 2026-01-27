import numpy as np
from typing import Union, Any
from skZemax.skZemax_subfunctions._c_print import c_print as cp
import clr, os, winreg, ctypes, sys
import numpy as np
from System.Runtime.InteropServices import GCHandle, GCHandleType

def _convert_raw_input_worker_(self, in_value: Union[int, Any], object_type: Any, return_index:bool=True)->Union[int, Any]:
    """
    ZOS-API commonly uses a scheme of indexing objects within an array. For instance, a surface can be an object or a corresponding index number.
    This is a low level worker function which compares and converts Zemax index integers and Zemax object types to return what another function needs regardless of the user's input.
    This is intended only to be called by other functions in skZemax submodules.


    :param in_value: Either an index or an object of a Zemax data type.
    :type in_value: Union[int, Any]
    :param object_type: The Zemax object type which should correspond to the index.
    :type object_type: Any
    :param return_index: Selects weather to return the index (True) or the object at that index (False), defaults to True
    :type return_index: bool, optional
    :return: Either the index of the object, or the object at the index depending on bool state of return_index.
    :rtype: Union[int, Any]
    """
    def _object_to_index_tree_()->int:
        if isinstance(in_value, self.ZOSAPI.SystemData.IField):
            return int(in_value.FieldNumber)
        elif isinstance(in_value, self.ZOSAPI.Editors.LDE.ILDERow):
            return int(in_value.SurfaceNumber)
        elif isinstance(in_value, self.ZOSAPI.SystemData.IWavelength):
            return int(in_value.WavelengthNumber)
        elif isinstance(in_value, self.ZOSAPI.Editors.MFE.IMFERow) or isinstance(in_value, self.ZOSAPI.Editors.MCE.IMCERow):
            return int(in_value.OperandNumber)
        elif isinstance(in_value, self.ZOSAPI.Editors.NCE.INCERow):
            return int(in_value.RowIndex + 1)# Indexed from zero (unlike surfaces)
        else:
            cp('!@ly!@_convert_raw_input_worker_ :: [!@lm!@{}!@ly!@] not found.'.format(object_type))
            return None
    
    def _index_to_object_tree_()->Any:
        if str(object_type) == str(self.ZOSAPI.SystemData.IField):
            return self.Field_GetField(int(in_value))
        elif str(object_type) == str(self.ZOSAPI.Editors.LDE.ILDERow):
            return self.LDE_GetSurface(int(in_value))
        elif str(object_type) == str(self.ZOSAPI.SystemData.IWavelength):
            return self.Wavelength_GetWavelength(int(in_value))
        elif str(object_type) == str(self.ZOSAPI.Editors.MFE.IMFERow):
            return self.MFE_GetOperand(int(in_value))
        elif str(object_type) == str(self.ZOSAPI.Editors.MCE.IMCERow):
            return self.MCE_GetConfigOperand(int(in_value))
        elif str(object_type) == str(self.ZOSAPI.Editors.NCE.INCERow):
            return self.NCE_GetObject(int(in_value))
        else:
            cp('!@ly!@_convert_raw_input_worker_ :: [!@lm!@{}!@ly!@] not found.'.format(object_type))
            return None

    if return_index and not isinstance(in_value, object_type):
        return int(in_value)
    elif return_index and isinstance(in_value, object_type):
        return _object_to_index_tree_()
    elif not return_index and not isinstance(in_value, object_type):
        return _index_to_object_tree_()
    else:
        return in_value #<- should already be of type(object_type)

@staticmethod
def __LowLevelZemaxStringCheck__(self, 
                                 in_obj,
                                 extra_include_filter:Union[str, list]=None,
                                 extra_exclude_filter:Union[str, list]=None,
                                 check_if_upper:bool=False)->list:
    """
    A low level function which produces a list of values given by python's dir() call - after some additional filtering.

    :param in_obj: The object for which the contents will be listed.
    :type in_obj: _type_
    :param extra_include_filter: A string which (or list of strings), if provided, will keep only the elements of the dir() call that have this sequence within it, defaults to None
    :type extra_include_filter: str, optional
    :param extra_exclude_filter: A string which (or list of strings), if provided, will exclude all the elements of the dir() call that have this sequence within it, defaults to None
    :type extra_exclude_filter: str, optional
    :param check_if_upper: If True, will only keep elements which are all upper cased, defaults to False
    :type check_if_upper: bool, optional
    :return: A list of the objects attributes (after any filtering)
    :rtype: list
    """
    if extra_include_filter is not None and isinstance(extra_include_filter, str):
        extra_include_filter = list([extra_include_filter])
    if extra_exclude_filter is not None and isinstance(extra_exclude_filter, str):
        extra_exclude_filter = list([extra_exclude_filter])
    all_names = [x for x in dir(in_obj) if '__' not in x]
    if extra_include_filter is not None:
        all_names = [x for x in all_names if any(y in x for y in extra_include_filter)]
    if extra_exclude_filter is not None:
        all_names = [x for x in all_names if not any(y in x for y in extra_exclude_filter)]
    if check_if_upper:
        all_names = [x for x in all_names if x.isupper()]
    # Filter out calls one shouldn't use through this function
    for x in ['Format', 'Equals', 'CompareTo', 'Finalize', 'GetHashCode', 'GetName',
                'GetNames', 'GetType', 'GetTypeCode', 'GetUnderlyingType', 'GetValues',
                'HasFlag', 'MemberwiseClone', 'Overloads', 'Parse', 'ReferenceEquals',
                'ToObject', 'ToString', 'TryParse', 'IsDefined']:
        try:
            all_names.remove(x)
        except:
            pass
    return sorted(all_names, key=lambda item: (len(item), item))

def _CheckIfStringValidInDir_(self, 
                              in_obj:Any, 
                              in_string:str,
                              extra_include_filter:Union[str, list]=None,
                              extra_exclude_filter:Union[str, list]=None,
                              check_if_upper:bool=False)->Any:
    """
    Looks at a Zemax class/module/etc and sees if the given string is an attribute/call within the Zemax code (via a dir() call).
    This function *returns* the value of the attribute in the Zemax code. Returns None if string does not match anything.

    If the given string matches more than one attribute, the first attribute within the dir() call will be given.

    :param in_obj:  The Zemax object to inspect.
    :type in_obj: Any
    :param in_string: The string to find within the object. This is not case sensitive. 
    :type in_string: str
    :param extra_include_filter: A string which (or list of strings), if provided, will keep only the elements of the dir() call that have this sequence within it, defaults to None
    :type extra_include_filter: str, optional
    :param extra_exclude_filter: A string which (or list of strings), if provided, will exclude all the elements of the dir() call that have this sequence within it, defaults to None
    :type extra_exclude_filter: str, optional
    :param check_if_upper: If True, will only keep elements - of the object dir() - which are all upper cased, defaults to False
    :type check_if_upper: bool, optional
    :return: he value of the Zemax object indicated by the string. None is returned if the string is not found.
    :rtype: Any
    """

    all_names = __LowLevelZemaxStringCheck__(self,
                                             in_obj=in_obj,
                                             extra_include_filter=extra_include_filter,
                                             extra_exclude_filter=extra_exclude_filter,
                                             check_if_upper=check_if_upper)
    # Check if input is known and return.
    bool_mask = [in_string.lower() in x.lower() for x in all_names]
    if np.any(bool_mask):
         return getattr(in_obj, all_names[int(np.where(bool_mask)[0][0])])
    if self._verbose: cp('!@ly!@_CheckIfStringValidInDir_ :: [!@lm!@{}!@ly!@] not found in object [!@lm!@{}!@ly!@].'.format(in_string, str(in_obj)))
    return None

def _SetAttrByStringIfValid_(self,
                             in_obj:Any,
                             in_string:str,
                             in_value:Any,
                             extra_include_filter:Union[str, list]=None,
                             extra_exclude_filter:Union[str, list]=None,
                             check_if_upper:bool=False):
    """
    Looks at a Zemax class/module/etc and sees if the given string is an attribute/call within the Zemax code (via a dir() call).
    This function *sets* the value of the attribute in the Zemax code.

    If the given string matches more than one attribute, the first attribute within the dir() call will be given.

    :param in_obj: The Zemax object to inspect.
    :type in_obj: Any
    :param in_string: The string to find within the object. This is not case sensitive. 
    :type in_string: str
    :param in_value: The value one would like to set the attribute/call identified by the in_string.
    :type in_value: Any
    :param extra_include_filter: A string which (or list of strings), if provided, will keep only the elements of the dir() call that have this sequence within it, defaults to None
    :type extra_include_filter: Union[str, list], optional
    :param extra_exclude_filter: A string which (or list of strings), if provided, will exclude all the elements of the dir() call that have this sequence within it, defaults to None
    :type extra_exclude_filter: Union[str, list], optional
    :param check_if_upper: If True, will only keep elements - of the object dir() - which are all upper cased, defaults to False
    :type check_if_upper: bool, optional
    """

    all_names = __LowLevelZemaxStringCheck__(self, 
                                             in_obj=in_obj,
                                             extra_include_filter=extra_include_filter,
                                             extra_exclude_filter=extra_exclude_filter,
                                             check_if_upper=check_if_upper)
    # Check if input is known and return.
    bool_mask = [in_string.lower() in x.lower() for x in all_names]
    if np.any(bool_mask):
         try:
            in_obj.__setattr__(all_names[int(np.where(bool_mask)[0][0])], in_value)
         except Exception as e:
            cp('!@lr!@_SetAttrByStringIfValid_ :: Error [!@lm!@{}!@lr!@] when trying to set [!@lm!@{}!@lr!@] with [!@lm!@{}!@lr!@].'.format(e, str(all_names[int(np.where(bool_mask)[0][0])]), str(in_value)))
    else:
        cp('!@ly!@_SetAttrByStringIfValid_ :: [!@lm!@{}!@ly!@] not found in object [!@lm!@{}!@ly!@].'.format(in_string, str(in_obj)))
        return

@staticmethod
def _ctype_to_numpy_(self, data:Any, data_length:int, data_type:Any=np.int64)->Any:
    """
    This method is a port from the example code attached to the `ZemaxRaytraceSupplement/RayTrace.dll`.
    This conversion helps interface python with the C# code.

    :param data: A pointer to a double reported by the C# code.
    :type data: Any
    :param data_length: The pointer array length to read in.
    :type data_length: int, optional
    :param data_type: The type of data to expect from the C# code, defaults to np.int64
    :type data_type: Any, optional
    :return: The value(s)
    :rtype: Any
    """
    src_hndl = GCHandle.Alloc(data, GCHandleType.Pinned)
    try:
        size_factor = ctypes.sizeof(ctypes.c_int32)/np.dtype(data_type).itemsize
        src_ptr = src_hndl.AddrOfPinnedObject().ToInt64()
        if size_factor >= 1:
            cbuf = (ctypes.c_int32*int(data_length*size_factor)).from_address(src_ptr)
        else:
            cbuf = (ctypes.c_int32*int(data_length/size_factor)).from_address(src_ptr)
        npData = np.frombuffer(cbuf, dtype=data_type)
    finally:
        if src_hndl.IsAllocated: src_hndl.Free()
    return npData
