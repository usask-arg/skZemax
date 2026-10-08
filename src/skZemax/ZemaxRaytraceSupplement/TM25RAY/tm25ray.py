from skZemax.ZemaxRaytraceSupplement.TM25RAY.reading_workers import (
    _read_binary_block_, 
    _parse_header_and_flags_, 
    _parse_description_,
    _parse_spectral_tables_,
    _parse_additional_ray_data_column_labels_,
    _parse_additional_text_block_,
    _parse_ray_data_
    )
from skZemax.ZemaxRaytraceSupplement.TM25RAY.wirting_workers import (
    _encode_str_,
    _write_binary_block_,
    _write_header_and_flags_,
    _write_description_,
    _write_spectral_tables_,
    _write_additional_ray_data_column_labels_,
    _write_ray_data_,
    _template_RayData_,
    _angle_deg_between_two_vectors_,
    _rot_about_arb_axis_
)

from pathlib import Path
from box import Box
import pandas as pd
import struct
import numpy as np

from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import (
    _convert_raw_input_worker_,
)

type ZOSAPI_Editors_NCE_INCERow = object  # <- ZOSAPI.Editors.NCE.INCERow # The actual module is referenced by the base PythonStandaloneApplication class.

def TM25RAY_ReadFile(path_to_file:str|Path)->Box:
    """Reads a TM25RAY file and returns the contents as a Box.

    :param path_to_file: Path to a binary TM25RAY file.
    :type path_to_file: str | Path
    :return: Box of the TM25RAY file contents.
    :rtype: Box
    """
    buffer_generator        = _read_binary_block_(str(Path(str(path_to_file)).with_suffix('.TM25RAY')))
    next(buffer_generator)  # start the generator
    header_and_flags        = _parse_header_and_flags_(in_buffer_generator=buffer_generator)
    description             = _parse_description_(in_buffer_generator=buffer_generator)
    spectral_tables         = _parse_spectral_tables_(in_buffer_generator=buffer_generator, header_and_flags=header_and_flags)
    additional_ray_labels   = _parse_additional_ray_data_column_labels_(in_buffer_generator=buffer_generator, header_and_flags=header_and_flags)
    additional_text_block   = _parse_additional_text_block_(in_buffer_generator=buffer_generator, header_and_flags=header_and_flags)
    ray_data                = _parse_ray_data_(in_buffer_generator=buffer_generator, header_and_flags=header_and_flags, additional_ray_labels=additional_ray_labels)
    buffer_generator.close()
    return header_and_flags + description + spectral_tables + additional_ray_labels + additional_text_block + ray_data

def TM25RAY_WriteFile(path_to_file:str|Path, RayData:pd.DataFrame, SpectralTables:pd.DataFrame=pd.DataFrame(), AdditionalTextBlock:str='')->None:
    """Writes a TM25RAY binary file.

    This function looks at a pd.DataFrame expected to hold ray information following the TM25RAY descriptions i.e. a format of:

    +-----------+----------+----------+----------+--------------------+-------------------+
    | (Index)   | XPosition| YPosition| ZPosition| XDirectionCosine   | ...               |
    | RayNumber |          |          |          |                    |                   |
    +-----------+----------+----------+----------+--------------------+-------------------+
    |     0     |   ...    |   ...    |  ....    |       ....         | ...               |
    +-----------+----------+----------+----------+--------------------+-------------------+
                                        //
    +-----------+----------+----------+----------+--------------------+-------------------+
    |     n     |   ...    |   ...    |  ....    |       ....         | ...               |
    +-----------+----------+----------+----------+--------------------+-------------------+      

    ...where n is the total number of rays (index from zero). The number of columns are variables depending on the content of the TM25RAY file.
    
    If the file requires spectral table information then this input should be provided as another pd.DataFrame following:

    +------------+---------------+------------+
    | Wavelengths| RelativeWeight| TableIndex |
    +------------+---------------+------------+
    | ...        |    ...        |     1      |
    +------------+---------------+------------+
                       //
    +------------+---------------+------------+
    | ...        |    ...        |     n      |
    +------------+---------------+------------+    

    ...where n is the total number of tables in the file. If there are no tables then an empty pd.DataFrame is used.  


    :param path_to_file:  Path to the binary TM25RAY file.
    :type path_to_file: str | Path
    :param RayData: As described above.
    :type RayData: pd.DataFrame
    :param SpectralTables: As described above., defaults to pd.DataFrame()
    :type SpectralTables: pd.DataFrame, optional
    :param AdditionalTextBlock: A string of additional text to include in the file, defaults to ''
    :type AdditionalTextBlock: str, optional
    """
    # Encode the additional text block as a binary string without the byte order mark since we know the explicitly size at little-endian order by file definition.
    # We will round up to the nearest size that is a multiple of 32 as defined. Format it here so it has the right size for _write_header_and_flags_.
    AdditionalTextBlock = _encode_str_(AdditionalTextBlock, size_bytes=((len(AdditionalTextBlock) + 31) // 32) * 32, format='utf-32-le')
    # Start the writ
    buffer_generator = _write_binary_block_(str(Path(str(path_to_file)).with_suffix('.TM25RAY')))
    next(buffer_generator) # start the generator
    header_and_flags = _write_header_and_flags_(in_buffer_generator=buffer_generator, RayData=RayData, SpectralTables=SpectralTables, AdditionalTextBlock=AdditionalTextBlock)
    _write_description_(in_buffer_generator=buffer_generator)
    _write_spectral_tables_(in_buffer_generator=buffer_generator, SpectralTables=SpectralTables)
    _write_additional_ray_data_column_labels_(in_buffer_generator=buffer_generator, RayData=RayData, header_and_flags=header_and_flags)
    # Write the additional text block
    buffer_generator.send(struct.pack(f"<{len(AdditionalTextBlock)}s", AdditionalTextBlock))
    _write_ray_data_(in_buffer_generator=buffer_generator, RayData=RayData)
    buffer_generator.close()

def TM25RAY_MakePolarizedSourceFile(self, 
                                    file_name: str,
                                    wavelengths:list|np.ndarray|float=750.0,
                                    XPosition:np.ndarray=np.array([0]), 
                                    YPosition:np.ndarray=np.array([0]), 
                                    ZPosition:np.ndarray=np.array([0]), 
                                    TiltAboutX:np.ndarray=np.array([0]), 
                                    TiltAboutY:np.ndarray=np.array([0]), 
                                    TiltAboutZ:np.ndarray=np.array([0]), 
                                    random_polarization:bool=True,
                                    UseGlobalXYZRotationOrder: bool=False)->pd.DataFrame:
    wavelengths = np.atleast_1d(wavelengths)
    # # https://optics.ansys.com/hc/en-us/articles/42661777200403-Rotation-Matrix-and-Tilt-About-X-Y-Z-in-OpticStudio
    # if UseGlobalXYZRotationOrder:
    #     # This option allows the system to (instrinsic rotation of):
    #     # - first tilt about the Z axis, 
    #     # - then tilt about Y axis, 
    #     # - lastly by X axis. 
    #     # The tilt about Z value changes the Y axis direction, which allows the rotation about new Y’ axis to tilt the Z’ axis to the desired Z” direction.
    #     pass
    # else:
    #     #   extrinsic (rotate along the original axes) z-y-x rotation, where we 
    #     # - first extrinsically tilt about Z, 
    #     # - then tilt about Y, 
    #     # - lastly tilt about X. 
    #     # This is equivalent to an instrinsic x-y-z rotation, where the system is rotated intrinsically first about X, then about Y, lastly about Z.
    #     pass
    RayData                                                     = _template_RayData_(is_polarized=True, include_Zemax_extra_fields=False)
    RayData["XPosition"]                                        = [0.0, 0.0, 0.0, 0.0]
    RayData["YPosition"]                                        = [0.0, 0.0, 0.0, 0.0]
    RayData["ZPosition"]                                        = [0.0, 0.0, 0.0, 0.0]
    RayData["XDirectionCosine"]                                 = [0.0, 0.0, 0.0, 0.0]
    RayData["YDirectionCosine"]                                 = [0.0, 0.0, 0.0, 0.0]
    RayData["ZDirectionCosine"]                                 = [1.0, 1.0, 1.0, 1.0]
    RayData["RadiantFluxStokesS0"]                              = [1.0, 1.0, 1.0, 1.0]
    RayData["Wavelength"]                                       = np.broadcast_to(wavelengths,  RayData["RadiantFluxStokesS0"].shape)
    RayData["StokesS1"]                                         = [0.0, 1.0, 0.0, 0.0]
    RayData["StokesS2"]                                         = [0.0, 0.0, 1.0, 0.0]
    RayData["StokesS3"]                                         = [0.0, 0.0, 0.0, 1.0]
    RayData["PolarizationEllipseMajorAxis_XDirectionCosine"]    = [0.0, 0.0, 0.0, 0.0]
    RayData["PolarizationEllipseMajorAxis_YDirectionCosine"]    = [1.0, 1.0, 1.0, 1.0]
    RayData["PolarizationEllipseMajorAxis_ZDirectionCosine"]    = [0.0, 0.0, 0.0, 0.0]
    TM25RAY_WriteFile((self.Utilities_ZemaxInstallationSourceDir() / file_name).with_suffix(".TM25RAY"), RayData=RayData)

    # # Current understanding:
    # If the TM25RAY file contains Stokes and/or the extra Zemax E components then Jx, Jy, X-Phase and Y-Phase settings should be ignored.
    # If the TM25RAY file has phase information then initial phase should be ignored. 
    # Coherence length is always used

    # # Get the source position and rotation matrices to build the ray file from
    # off, R = self.NCE_GetObjectRotationAndPositionMatrices(ObjectNCE)
    # 
    # basis_angles_deg_wr_to_Z = _angle_deg_between_two_vectors_(np.array([0,0,1]), R)
    # xyz_directional_cosines = R[:, -1] # == np.cos(np.deg2rad(basis_angles_deg_wr_to_Z)) 


