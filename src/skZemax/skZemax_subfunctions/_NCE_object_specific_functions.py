from skZemax.skZemax_subfunctions._NCE_functions import (
    NCE_GetObjectType,
    NCE_GetAllColumnDataOfObject,
    NCE_SetAllColumnDataOfObjectFromDict
)
from skZemax.skZemax_subfunctions._log_maker import get_logger
log = get_logger('SkZemax_NCE')
import numpy as np

type ZOSAPI_Editors_NCE_INCERow = object  # <- ZOSAPI.Editors.NCE.INCERow # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Editors_NCE_ObjectColumn = object  # <- ZOSAPI.Editors.NCE.ObjectColumn # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Editors_NCE_IEditorCell = object  # <- ZOSAPI.Editors.IEditorCell # The actual module is referenced by the base PythonStandaloneApplication class.

def NCE_SetMuellerMatrix(self, ObjectNCE: int | ZOSAPI_Editors_NCE_INCERow, mueller_matrix:np.ndarray=np.eye(4))->ZOSAPI_Editors_NCE_INCERow:
    """This function sets the properties of a "Mueller Matrix" object in non-sequential mode.

    :param ObjectNCE: The NCE object to get the type of. Can be given as an index or an NCE object.
    :type ObjectNCE: int | ZOSAPI_Editors_NCE_INCERow
    :param mueller_matrix: The 4x4 mueller matrix of the component as a np.ndarray, defaults to np.eye(4)
    :type mueller_matrix: float, The angle of the component.
    :return: The same NCE Mueller Matrix object but now changed.
    :rtype: ZOSAPI_Editors_NCE_INCERow
    """
    ObjectNCE = self._convert_raw_obj_input_(ObjectNCE, return_index=True)
    if 'MuellerMatrix' not in self.NCE_GetObjectType(ObjectNCE):
        log.warning("Trying to adjust the Mueller Matrix of an object which is not a Mueller Matrix.")
        return ObjectNCE
    
    columns = self.NCE_GetAllColumnDataOfObject(ObjectNCE)
    columns.Depolarize = 1 # Should always be set to 1 for a Mueller Matrix object. A 0 is for a Jones Matrix object.
    columns.M00 = mueller_matrix[0,0]
    columns.M01 = mueller_matrix[0,1]
    columns.M02 = mueller_matrix[0,2]
    columns.M03 = mueller_matrix[0,3]
    columns.M10 = mueller_matrix[1,0]
    columns.M11 = mueller_matrix[1,1]
    columns.M12 = mueller_matrix[1,2]
    columns.M13 = mueller_matrix[1,3]
    columns.M20 = mueller_matrix[2,0]
    columns.M21 = mueller_matrix[2,1]
    columns.M22 = mueller_matrix[2,2]
    columns.M23 = mueller_matrix[2,3]
    columns.M30 = mueller_matrix[3,0]
    columns.M31 = mueller_matrix[3,1]
    columns.M32 = mueller_matrix[3,2]
    columns.M33 = mueller_matrix[3,3]
    self.NCE_SetAllColumnDataOfObjectFromDict(ObjectNCE, columns)
    return self._convert_raw_obj_input_(ObjectNCE, return_index=False)

def NCE_SetMuellerMatrixLinearDiattenuator(self, ObjectNCE: int | ZOSAPI_Editors_NCE_INCERow, angle:float=0.0, transmission:float=1.0, extinction_ratio:float=np.inf)->ZOSAPI_Editors_NCE_INCERow:
    """This function sets a Mueller Matrix object coefficients directly to be that of a Linear Diattenuator described by the Handbook of Optics 3rd Edition Volume 1 Chapter 14.16: Mueller Matrices of Diattenuators.

    :param ObjectNCE: The NCE object to get the type of. Can be given as an index or an NCE object.
    :type ObjectNCE: int | ZOSAPI_Editors_NCE_INCERow
    :param angle: The orientation of the linear diattenuator in degrees, defaults to 0.0
    :type angle: float, optional
    :param transmission: The maximum transmission of the polarizer (when it is orientated parallel to the plane of linear polarization of the Stokes vector), defaults to 1.0
    :type transmission: float, optional
    :param extinction_ratio: This is equal to the maximum transmission divided by the minimum transmission (when it is orientated perpendicular to the plane of linear polarization of the Stokes vector). Typically, the specifications of a linear polarizer given by manufactures provide this as a #:1 ratio, defaults to np.inf (ideal)
    :type extinction_ratio: float, optional
    :return: The same NCE Mueller Matrix object but now changed.
    :rtype: ZOSAPI_Editors_NCE_INCERow
    """
    mueller_matrix = np.eye(4)*0.0
    alp = np.deg2rad(angle)
    p = transmission  # max transmittance of the polarizer aka transmittance of an aligned polarizer.
    s = p / extinction_ratio  # min transmittance of the polarizer aka p scaled by the extinction ratio.
    A = p + s
    B = p - s
    C = 2 * np.sqrt(p * s)

    mueller_matrix[0, 0]    = A
    mueller_matrix[0, 1]    = B * np.cos(2 * alp)
    mueller_matrix[0, 2]    = B * np.sin(2 * alp)

    mueller_matrix[1, 0]    = B * np.cos(2 * alp)
    mueller_matrix[1, 1]    = (A * (np.cos(2 * alp) ** 2)) + (C * (np.sin(2 * alp) ** 2))
    mueller_matrix[1, 2]    = (A - C) * np.sin(2 * alp) * np.cos(2 * alp)

    mueller_matrix[2, 0]    = B * np.sin(2 * alp)
    mueller_matrix[2, 1]    = (A - C) * np.sin(2 * alp) * np.cos(2 * alp)
    mueller_matrix[2, 2]    = (A * (np.sin(2 * alp) ** 2)) + (C * (np.cos(2 * alp) ** 2))

    mueller_matrix[3, 3]    = C

    mueller_matrix         *= 1/2

    return self.NCE_SetMuellerMatrix(ObjectNCE=ObjectNCE, mueller_matrix=mueller_matrix)
