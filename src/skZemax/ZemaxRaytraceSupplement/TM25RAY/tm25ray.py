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
    _rot_about_arb_axis_,
    _stokes_to_TM25RAY_polarization_
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
    # UTF-32 uses 4 bytes per character, so the size in bytes is 4*len(text) before rounding.
    AdditionalTextBlock = _encode_str_(AdditionalTextBlock, size_bytes=((4*len(AdditionalTextBlock) + 31) // 32) * 32, format='utf-32-le')
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
    """Writes a polarized TM25RAY source file for use with a Zemax non-sequential ``SourceFile`` object.

    .. warning::
        Work in progress. The function currently writes four hard-coded test rays, all at the origin and
        travelling along +Z, with S0 = 1 and Stokes vectors (S1, S2, S3) = (0,0,0), (1,0,0), (0,1,0) and (0,0,1)
        defined in the lab basis (x_ref = +X, y_ref = +Y), i.e. unpolarized, X-linear, +45° linear and circular.
        These are converted to the TM25RAY columns with :func:`_stokes_to_TM25RAY_polarization_`.
        ``XPosition``, ``YPosition``, ``ZPosition``, ``TiltAboutX``, ``TiltAboutY``, ``TiltAboutZ``,
        ``random_polarization`` and ``UseGlobalXYZRotationOrder`` are not used yet.
        Nothing is returned, despite the ``pd.DataFrame`` return annotation.

    **How TM-25 defines the polarization basis** (ANSI/IES TM-25-20(R25), §3.21 and §4.8.1.10-15):

    * S1, S2 and S3 are stored **normalized by S0**, so each is in [-1, 1] and S1² + S2² + S3² <= 1.
      The ``RadiantFluxStokesS0`` column holds the ray flux. S1 = S2 = S3 = 0 means unpolarized.
      Non-normalized Stokes vectors or axis vectors make the file invalid.
    * The ``PolarizationEllipseMajorAxis_*DirectionCosine`` columns give a unit vector M, orthogonal to the
      ray direction k, that provides the Stokes reference frame. The frame is right-handed:
      x = M, y = k × x. Here k always points along the direction of ray **propagation** (the ray's
      direction cosines), not towards the source. §3.21 only *recommends* that M lie along the ellipse major axis, but
      §4.8.1.13-15 define M *as* the major axis.

    **How Zemax reads it** (OpticStudio User Manual, Source File, "Read TM-25 rayfiles (polarization)"):

    * For each ray, Zemax draws rd ~ U[0, 1]. If rd > Sp/S0, with Sp = sqrt(S1² + S2² + S3²), the ray is given
      a random polarization state. Partial polarization is therefore represented statistically
      across many rays, and an unpolarized ray (Sp = 0) is always randomized.
    * Otherwise the ellipse shape and handedness come from the full Stokes vector (a standard
      Stokes-to-Jones conversion that uses S1, S2 and S3). The ellipse is then rotated about k so that its
      **major axis lies along M**. The orientation of linear polarization therefore comes **only from M**.
    * Zemax combines the stored S1-S3 directly with S0. This only agrees with TM-25's
      S0-normalization when S0 = 1, so keep S0 = 1 per ray and set the total power with the
      ``SourceFile`` object's power parameter.
    * Files written by Zemax place the major axis on x and carry extra Ex/Ey/Ez columns.
      Zemax uses those columns, not the Stokes values, when it re-reads its own files.

    **Encoding used here (valid under both TM-25 readings and Zemax):** for Stokes (S0, S1, S2, S3)
    given in a user basis (x_ref, y_ref = k × x_ref), take psi = 0.5*atan2(S2, S1) and write

        - M = cos(psi)*x_ref + sin(psi)*y_ref
        - (S1, S2, S3) = (sqrt(S1² + S2²), 0, S3) / S0, with S0 = 1

    For example, +45° linear light along +Z with x_ref = +X is written as M = (1/√2, 1/√2, 0) and Stokes (1, 0, 0).
    The physical sign of S3 (circular handedness) is not defined by TM-25. It still needs to be checked
    against a known Zemax source.

    The file is written to Zemax's source-file directory
    (:func:`Utilities_ZemaxInstallationSourceDir`), so the ``SourceFile`` object can reference it by name.

    :param file_name: Name of the TM25RAY file to write. The ``.TM25RAY`` suffix is added or replaced automatically.
    :type file_name: str
    :param wavelengths: Wavelength of the rays in nm (TM-25 units). Broadcast across all rays, defaults to 750.0
    :type wavelengths: list | np.ndarray | float, optional
    :param XPosition: (Not yet used) Ray start x-positions, defaults to np.array([0])
    :type XPosition: np.ndarray, optional
    :param YPosition: (Not yet used) Ray start y-positions, defaults to np.array([0])
    :type YPosition: np.ndarray, optional
    :param ZPosition: (Not yet used) Ray start z-positions, defaults to np.array([0])
    :type ZPosition: np.ndarray, optional
    :param TiltAboutX: (Not yet used) Source tilt about X in degrees, defaults to np.array([0])
    :type TiltAboutX: np.ndarray, optional
    :param TiltAboutY: (Not yet used) Source tilt about Y in degrees, defaults to np.array([0])
    :type TiltAboutY: np.ndarray, optional
    :param TiltAboutZ: (Not yet used) Source tilt about Z in degrees, defaults to np.array([0])
    :type TiltAboutZ: np.ndarray, optional
    :param random_polarization: (Not yet used) If True, rays would be given random polarization states, defaults to True
    :type random_polarization: bool, optional
    :param UseGlobalXYZRotationOrder: (Not yet used) Must match the ``UseGlobalXYZRotationOrder`` setting of the
        Zemax ``SourceFile`` object, which sets the order in which the tilts are applied, defaults to False
    :type UseGlobalXYZRotationOrder: bool, optional
    :return: Nothing at present. The file is written to disk.
    :rtype: None
    """
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
    # Stokes vectors (S0, S1, S2, S3) in the lab basis: unpolarized, X-linear, +45° linear, circular.
    stokes                                                      = np.array([[1.0, 0.0, 0.0, 0.0],
                                                                            [1.0, 1.0, 0.0, 0.0],
                                                                            [1.0, 0.0, 1.0, 0.0],
                                                                            [1.0, 0.0, 0.0, 1.0]])
    polarization                                                = _stokes_to_TM25RAY_polarization_(stokes, ray_direction=RayData[["XDirectionCosine", "YDirectionCosine", "ZDirectionCosine"]].to_numpy(dtype=float), reference_x=np.array([1.0, 0.0, 0.0]))
    for col in polarization.columns:
        RayData[col]                                            = polarization[col].to_numpy()
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


