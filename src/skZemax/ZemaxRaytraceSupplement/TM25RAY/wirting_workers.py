from box import Box
import struct
import numpy as np
import pandas as pd
from typing import Generator
from skZemax.ZemaxRaytraceSupplement.TM25RAY.reading_and_writeing_workers import _header_and_flags_error_checking_

def _write_binary_block_(filename: str) -> Generator[None, bytes | int, None]:
    """Construct a generator for writing binary data.

    This generator should be started with an external call to
    ``next(buffer_generator)``.

    The generator will *write* binary data to the file with a call to
    ``buffer_generator.send(bytes)``.

    The generator will *move* the file position forward or backward by a
    specific number of bytes with a call to ``buffer_generator.send(int)``.
    A positive integer moves the file position forward, while a negative
    integer moves it backward.

    Moving the file position does not modify the contents of the file.
    Subsequent binary data written with ``buffer_generator.send(bytes)``
    will be written at the new file position, potentially overwriting
    existing data.

    :param filename: Full path to the binary file to open.
    :type filename: str
    :raises TypeError: If the value sent to the generator is neither
        ``bytes`` nor ``int``.
    :yield: The binary generator.
    :rtype: Generator[None, bytes | int, None]
    """
    with open(filename, "wb") as f:
        request = yield

        while True:
            if isinstance(request, bytes):
                f.write(request)
            elif isinstance(request, int):
                f.seek(request, 1)
            else:
                raise TypeError(
                    f"Expected bytes or int, got {type(request).__name__}"
                )

            request = yield

def _encode_str_(in_str: str, size_bytes: int, format: str = "utf-32",
) -> bytes:
    """Worker function to encode a TM25RAY string field as bytes.

    The encoded string is padded with ``\\x00`` bytes to fill exactly
    ``size_bytes`` bytes. If the encoded string exceeds the requested size,
    a ValueError is raised.

    :param in_str: string to encode as binary data
    :type in_str: str
    :param size_bytes: number of bytes to allocate for the string field
    :type size_bytes: int
    :param format: encoding scheme, defaults to 'utf-32'
    :type format: str, optional
    :raises ValueError: If the encoded string is larger than ``size_bytes`` bytes.
    :return: the encoded and padded binary data
    :rtype: bytes
    """
    encoded = in_str.encode(format)
    if len(encoded) > size_bytes:
        raise ValueError(
            f"Encoded string is {len(encoded)} bytes, "
            f"but field size is {size_bytes} bytes"
        )
    return encoded + b"\x00" * (size_bytes - len(encoded))


def _define_ray_block_contents_from_ray_info_(RayData:pd.DataFrame, SpectralTables:pd.DataFrame=pd.DataFrame(), AdditionalTextBlock:str='')->Box:
    """This is a worker function for writing TM25RAY files (:func:`TM25RAY_write_file`). 
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

    ...where n is the total number of rays (index from zero). This is the same output as made in :func:`_parse_ray_data_`.
    The number of columns are variables depending on the content of the TM25RAY file.
    
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

    ...where n is the total number of tables in the file. This is the same output as made in :func:`_parse_spectral_tables_`.
    If there are no tables then an empty pd.DataFrame is used.  

    This function will raise Exceptions if the information seems misformed or lacking to correctly make a TM25RAY file.

    :param RayData: DataFrame of ray data
    :type RayData: pd.DataFrame
    :param SpectralTables: Spectral table as defined above, defaults to pd.DataFrame()
    :type SpectralTables: pd.DataFrame, optional
    :param AdditionalTextBlock: A string representing an additional text block to add to the file, defaults to ''
    :type AdditionalTextBlock: str, optional
    :return: Information to correctly fill the file.
    :rtype: Box
    """
    out         = Box({})
    columns     = RayData.columns.str.lower()
    IsValid     = True
    out.NumberOfRays = RayData.shape[0]
    IsValid    &= out.NumberOfRays > 0
    IsValid    &= 'position' in columns[0] and 'x' in columns[0] 
    IsValid    &= 'position' in columns[1] and 'y' in columns[1] 
    IsValid    &= 'position' in columns[2] and 'z' in columns[2] 
    IsValid    &= 'direction' in columns[3] and 'cosine' in columns[3] and 'x' in columns[3] and 'polarization' not in columns[3] and 'ellipse' not in columns[3]
    IsValid    &= 'direction' in columns[4] and 'cosine' in columns[4] and 'y' in columns[4] and 'polarization' not in columns[4] and 'ellipse' not in columns[4]
    IsValid    &= 'direction' in columns[5] and 'cosine' in columns[5] and 'z' in columns[5] and 'polarization' not in columns[5] and 'ellipse' not in columns[5]
    if not IsValid:
        raise Exception('RayData is missing correct position and/or direction information.')
    # Define defaults for the file data (assuming optional data cannot be found it in the RayData)
    out.FileType                                = 'TM25'
    out.FileVersion                             = 2013
    out.CreationMethod                          = 0 # Simulation
    out.FileCreationDateAndTime                 = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%S%z")
    out.RayStartPosition                        = 1 # Specified rays
    out.PositionFlag                            = 1
    out.DirectionFlag                           = 1
    out.SizeOfAdditionalTextBlock               = len(AdditionalTextBlock)
    # Stuff below may be found in the RayData...
    out.RadiantFluxStokesS0Flag                 = 0
    out.TotalRadiantFlux                        = np.nan
    out.WavelengthFlag                          = 0
    out.SingleWavelength                        = np.nan
    out.MinimumWavelength                       = np.nan
    out.MaximumWavelength                       = np.nan
    out.LuminousFluxYTristimulusFlag            = 0
    out.TotalLuminousFlux                       = np.nan
    out.StokesFlag                              = 0
    out.TristimulusFlag                         = 0
    out.SpectrumIndexFlag                       = 0
    out.SpectralDataIdentifier                  = 0
    out.NumberOfSpectralTables                  = 0
    out.NumberOfAdditionalRayDataItemsPerRay    = 0
    # The first 6 columns are correctly positions and directions. Now check what all the non-required fields are.
    def _return_formatted_header_and_flags_(in_box:Box)->Box:
        """After the ray file has been parsed, configure anything that needs to be done before returning"""
        if not SpectralTables.empty and len(SpectralTables.TableIndex.unique()) == 1 and in_box.SpectrumIndexFlag == 0:
            in_box.NumberOfSpectralTables = 1
            in_box.SpectralDataIdentifier = 3
        elif in_box.SpectrumIndexFlag > 0 and not SpectralTables.empty:
            in_box.NumberOfSpectralTables = SpectralTables.TableIndex.max()
            in_box.SpectralDataIdentifier = 4
        elif not np.isnan(in_box.SingleWavelength):
            in_box.SpectralDataIdentifier = 1
        elif not np.isnan(in_box.MinimumWavelength):
            in_box.SpectralDataIdentifier = 2
        else:
            raise Exception("Can not identify the correct SpectralDataIdentifier.")
        if in_box.SpectralDataIdentifier == 3 or in_box.SpectralDataIdentifier == 4:
            in_box.MinimumWavelength = SpectralTables.Wavelengths.min()
            in_box.MaximumWavelength = SpectralTables.Wavelengths.max()
        return _header_and_flags_error_checking_(in_box)
    
    current_column = 6
    if current_column == len(columns):
        return _return_formatted_header_and_flags_(out)
    #----------------------------------------------------------------------------------------------------------#
    out.RadiantFluxStokesS0Flag = 1 if (('radiant' in columns[current_column] and 'flux' in columns[current_column]) or ('stokes' in columns[current_column] and 's0' in  columns[current_column])) else 0
    if out.RadiantFluxStokesS0Flag == 1:
        out.TotalRadiantFlux = np.sum(RayData.iloc[:, current_column])
        current_column += 1
        if current_column == len(columns):
            return _return_formatted_header_and_flags_(out)
    #----------------------------------------------------------------------------------------------------------#
    out.WavelengthFlag = 1 if ('wavelength' in columns[current_column]) else 0
    if out.WavelengthFlag == 1:
        wvlns = RayData.iloc[:, current_column]
        if len(np.unique(wvlns)) == 1:
            out.SingleWavelength = float(np.unique(RayData.iloc[:, current_column])[0])
            if out.SingleWavelength <= 0:
                raise Exception('RayData contains a single zero or negative wavelength.')
        else:
            out.MinimumWavelength = np.min(wvlns)
            out.MaximumWavelength = np.max(wvlns)
            if out.MinimumWavelength <= 0 or out.MaximumWavelength <= 0:
                raise Exception('RayData contains zero or negative wavelengths.')
        current_column += 1
        if current_column == len(columns):
                return _return_formatted_header_and_flags_(out)
    #----------------------------------------------------------------------------------------------------------#
    out.LuminousFluxYTristimulusFlag = 1 if (('luminous' in columns[current_column] and 'flux' in columns[current_column]) or ('y' in columns[current_column] and 'tristimulus' in  columns[current_column])) else 0
    if out.LuminousFluxYTristimulusFlag == 1:
        out.TotalLuminousFlux = np.sum(RayData.iloc[:, current_column])
        current_column += 1
        if current_column == len(columns):
            return _return_formatted_header_and_flags_(out)
    #----------------------------------------------------------------------------------------------------------#
    if current_column+6 < len(columns):
        stokes_vector_present = (all('stokes' in x for x in columns[current_column:current_column+3]) and 's1' in columns[current_column] and 's2' in columns[current_column+1] and 's3' in columns[current_column+2])
        stokes_axis_present   = (all(('ellipse' in x and 'polarization' in x and 'major' in x and 'direction' in x and 'cosine' in x) for x in columns[current_column+3:current_column+6]) and 'x' in columns[current_column+3] and 'y' in columns[current_column+4] and 'z' in columns[current_column+5])
        out.StokesFlag = 1 if stokes_vector_present and stokes_axis_present else 0
        if out.StokesFlag == 1:
            current_column += 6
            if current_column == len(columns):
                return _return_formatted_header_and_flags_(out)
    #----------------------------------------------------------------------------------------------------------#
    if current_column+2 < len(columns):
        out.TristimulusFlag = 1 if all('tristimulus' in x for x in columns[current_column:current_column+2]) and 'x' in columns[current_column] and 'y' in columns[current_column+1] else 0
        if out.TristimulusFlag == 1:
            current_column += 2
            if current_column == len(columns):
                return _return_formatted_header_and_flags_(out)
    #----------------------------------------------------------------------------------------------------------#
    out.SpectrumIndexFlag = 1 if 'spectrum' in columns[current_column] and 'index' in columns[current_column] else 0
    if out.SpectrumIndexFlag == 1:
        current_column += 1
        if current_column == len(columns):
            return _return_formatted_header_and_flags_(out)
    #----------------------------------------------------------------------------------------------------------#
    if current_column < len(columns):
        out.NumberOfAdditionalRayDataItemsPerRay = len(columns[current_column::])
    return _return_formatted_header_and_flags_(out)


def _write_header_and_flags_(in_buffer_generator:Generator[bytes, int, None], RayData:pd.DataFrame, SpectralTables:pd.DataFrame, AdditionalTextBlock:str)->Box:
    """This function works out the headers and flags which should be in the file given the ray data, spectral tables, and additional text block.

    :param in_buffer_generator:  A generator to produce binary data. It should be set to read from the start of the file.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param RayData: The ray data. See description in :func:`_define_ray_block_contents_from_ray_info_`
    :type RayData: pd.DataFrame
    :param SpectralTables: The spectral data. See description in :func:`_define_ray_block_contents_from_ray_info_`
    :type SpectralTables: pd.DataFrame, optional
    :param AdditionalTextBlock: A string representing an additional text block to add to the file
    :type AdditionalTextBlock: str, optional
    :return: The determined headers and flags of the file (which have already been written).
    :rtype: Box
    """
    header_and_flags = _define_ray_block_contents_from_ray_info_(RayData=RayData, SpectralTables=SpectralTables, AdditionalTextBlock=AdditionalTextBlock)
    data_to_write = (
        _encode_str_(in_str=header_and_flags.FileType, size_bytes=4, format='ascii'),
        header_and_flags.FileVersion,
        header_and_flags.CreationMethod,
        header_and_flags.TotalLuminousFlux,
        header_and_flags.TotalRadiantFlux,
        header_and_flags.NumberOfRays,
        _encode_str_(in_str=header_and_flags.FileCreationDateAndTime, size_bytes=28, format='ascii'),
        header_and_flags.RayStartPosition,
        header_and_flags.SpectralDataIdentifier,
        header_and_flags.SingleWavelength,
        header_and_flags.MinimumWavelength,
        header_and_flags.MaximumWavelength,
        header_and_flags.NumberOfSpectralTables,
        header_and_flags.NumberOfAdditionalRayDataItemsPerRay,
        header_and_flags.SizeOfAdditionalTextBlock,
        header_and_flags.PositionFlag,
        header_and_flags.DirectionFlag,
        header_and_flags.RadiantFluxStokesS0Flag,
        header_and_flags.WavelengthFlag,
        header_and_flags.LuminousFluxYTristimulusFlag,
        header_and_flags.StokesFlag,
        header_and_flags.TristimulusFlag,
        header_and_flags.SpectrumIndexFlag
    )
    buffer = struct.pack(
            "<4s i i f f Q 28s i i f f f i i i 168x i i i i i i i i",
            *data_to_write
        )
    in_buffer_generator.send(buffer)
    return header_and_flags

def _write_description_(in_buffer_generator:Generator[bytes, int, None])->None:
    """This function writes the description header block of a TM25RAY file.

    :param in_buffer_generator: A generator to produce binary data. It should be set to start writing after :func:`_write_header_and_flags_`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :return: The file descriptions
    :rtype: Box
    """
    data_to_write = (
        _encode_str_(in_str='skZemax Non-sequential Raytrace', size_bytes=4000),
        _encode_str_(in_str='skZemax', size_bytes=4000),
        _encode_str_(in_str='skZemax', size_bytes=4000),
        _encode_str_(in_str='skZemax', size_bytes=4000),
        _encode_str_(in_str='skZemax', size_bytes=4000),
        _encode_str_(in_str='skZemax', size_bytes=4000),
        _encode_str_(in_str='skZemax', size_bytes=4000),
        _encode_str_(in_str='skZemax', size_bytes=4000),
        _encode_str_(in_str='skZemax', size_bytes=4000),
    )
    buffer = struct.pack(
            "<4000s 4000s 4000s 4000s 4000s 4000s 4000s 4000s 4000s",
            *data_to_write
        )
    in_buffer_generator.send(buffer)

def _write_spectral_tables_(in_buffer_generator:Generator[bytes, int, None], SpectralTables:pd.DataFrame):
    """This function will write all spectral tables to the TM25RAY file (if any are present). 
    Error checking is done as the tables are written, and the binary buffer is advanced to the end of this block.

    Spectral table(s) to be written are expected to be a pd.DataFrame with the format of:

    +------------+---------------+------------+
    | Wavelengths| RelativeWeight| TableIndex |
    +------------+---------------+------------+
    | ...        |    ...        |     1      |
    +------------+---------------+------------+
                       //
    +------------+---------------+------------+
    | ...        |    ...        |     n      |
    +------------+---------------+------------+                     

    ...where n is the total number of tables in the file. If there are no tables then nothing is written  

    :param in_buffer_generator:  A generator to produce binary data. It should be set to start writing after :func:`_write_description_`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param SpectralTables: Spectral table as defined above.
    :type SpectralTables: pd.DataFrame
    """
    data_to_write = []
    data_format = '<'

    def _write_table_(in_table: pd.DataFrame):
        table_data = [int(in_table.shape[0])]
        table_data.extend(
            in_table[["Wavelengths", "RelativeWeight"]]
            .to_numpy()
            .flatten()
        )
        table_format = 'i ' + 'f f ' * len(in_table)
        return table_data, table_format
    if not SpectralTables.empty:
        for idx in SpectralTables.TableIndex.unique():
            table_data, table_format = _write_table_(
                SpectralTables[SpectralTables["TableIndex"] == idx]
            )

            data_to_write.extend(table_data)
            data_format += table_format

        # Add any needed padding so it is a multiple of 32
        padding = (len(data_to_write)*4)%32
        if padding > 0:
            data_to_write.extend([0 for x in range(padding)])
            data_format+= 'i '*padding

        buffer = struct.pack(
            data_format,
            *data_to_write
        )
        in_buffer_generator.send(buffer)

def _write_additional_ray_data_column_labels_(in_buffer_generator:Generator[bytes, int, None], RayData:pd.DataFrame, header_and_flags:Box):
    """This function writes the block of the TM25RAY file that lists the labels of any additional ray data.

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
    
    ...where n is the total number of rays (index from zero). This is the same output as made in :func:`_parse_ray_data_`.
    The number of columns are variables depending on the content of the TM25RAY file.

    :param in_buffer_generator: A generator to produce binary data. It should be set to start reading after :func:`_write_spectral_tables_`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param RayData: As defined above.
    :type RayData: pd.DataFrame
    :param header_and_flags: The output of :func:`_write_header_and_flags_`
    :type header_and_flags: Box
    """
    if header_and_flags.NumberOfAdditionalRayDataItemsPerRay > 0:
        AdditionalRayDataColumnLabels = list(RayData.columns[-header_and_flags.NumberOfAdditionalRayDataItemsPerRay::])
        data_to_write = [_encode_str_(x, 512) for x in AdditionalRayDataColumnLabels]
        data_format = '<' + '512s '*header_and_flags.NumberOfAdditionalRayDataItemsPerRay
        buffer = struct.pack(
            data_format,
            *data_to_write
        )
        in_buffer_generator.send(buffer)


def _write_ray_data_(in_buffer_generator:Generator[bytes, int, None],  RayData:pd.DataFrame):
    """This function writes all the ray data within the TM25RAY file. The rays are expected to be given as a pd.DataFrame following:

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

    :param in_buffer_generator: A generator to produce binary data. It should be set to after the writing of the additional text block in :func:`TM25RAY_write_file`
    :type in_buffer_generator: Generator[bytes, int, None]
    :param RayData: As defined above.
    :type RayData: pd.DataFrame
    """
    data_to_write = list(RayData[[x for x in RayData.columns]].to_numpy().flatten())
    data_format = '<' + ' '.join(['f' if ('spectrum' not in x.lower() or 'index' not in x.lower()) else 'i' for x in RayData.columns]*RayData.shape[0])
    buffer = struct.pack(
                data_format,
                *data_to_write
            )
    in_buffer_generator.send(buffer)

def _rot_about_arb_axis_(
    rot_axis: np.ndarray,
    vec_to_rot: np.ndarray,
    angle_deg: float | np.ndarray,
    should_make_unit: bool = True,
) -> np.ndarray:
    """
    Rotate vectors about arbitrary axes using Rodrigues' rotation formula.

    Parameters
    ----------
    rot_axis : np.ndarray
        Rotation axes with shape (..., 3).

    vec_to_rot : np.ndarray
        Vectors to rotate with shape (..., 3).

    angle_deg : float or np.ndarray
        Rotation angle(s) in degrees. Can be scalar or have shape (...).

    should_make_unit : bool
        If True, normalize both the rotation axes and input vectors,
        and normalize the output.

    Returns
    -------
    np.ndarray
        Rotated vectors with shape (..., 3).
    """

    angle_rad = np.deg2rad(angle_deg)

    rot_axis = np.array(rot_axis, dtype=float, copy=True)
    vec_to_rot = np.array(vec_to_rot, dtype=float, copy=True)

    if should_make_unit:
        rot_axis /= np.linalg.norm(
            rot_axis,
            axis=-1,
            keepdims=True
        )

        vec_to_rot /= np.linalg.norm(
            vec_to_rot,
            axis=-1,
            keepdims=True
        )

    cos_angle = np.cos(angle_rad)[..., None]
    sin_angle = np.sin(angle_rad)[..., None]

    dot = np.sum(
        rot_axis * vec_to_rot,
        axis=-1,
        keepdims=True
    )

    rotated_vector = (
        vec_to_rot * cos_angle
        + np.cross(rot_axis, vec_to_rot) * sin_angle
        + rot_axis * dot * (1 - cos_angle)
    )

    if should_make_unit:
        rotated_vector /= np.linalg.norm(
            rotated_vector,
            axis=-1,
            keepdims=True
        )

    return rotated_vector

def _angle_deg_between_two_vectors_(v1:np.ndarray, v2:np.ndarray):
    """Returns the angle in degrees between vectors

    :param np.ndarray v1: [..., xyz]
    :param np.ndarray v2: [..., xyz]
    :return _type_: angles between the vectors
    """
    dot = np.sum(v1 * v2, axis=-1) / (
        np.linalg.norm(v1, axis=-1) *
        np.linalg.norm(v2, axis=-1))
    return np.asarray(np.rad2deg(np.arccos(np.clip(dot, -1, 1))))

def _template_RayData_(is_polarized:bool=True, include_Zemax_extra_fields:bool=False)->pd.DataFrame:
    """This function returns an empty dataset to write TM25RAY files that Zemax will like to read for a (NCE) raytrace. 

    :param is_polarized: If True polarization of the ray will be defined, defaults to True
    :type is_polarized: bool, optional
    :param include_Zemax_extra_fields: If True the user is expected to define the phase and electric field components of each ray. Zemax should read this over Stokes definitions - but it is ideal to have the correct Stokes information in as well, defaults to False
    :type include_Zemax_extra_fields: bool, optional
    :return: A template to write rays to which can be saved as a TM25RAY file with :func:`TM25RAY_write_file`
    :rtype: pd.DataFrame
    """
    columns = [
    "XPosition",
    "YPosition",
    "ZPosition",
    "XDirectionCosine",
    "YDirectionCosine",
    "ZDirectionCosine",
    "RadiantFluxStokesS0",
    "Wavelength",
    ]
    if is_polarized:
        columns = columns + [
    "StokesS1",
    "StokesS2",
    "StokesS3",
    "PolarizationEllipseMajorAxis_XDirectionCosine",
    "PolarizationEllipseMajorAxis_YDirectionCosine",
    "PolarizationEllipseMajorAxis_ZDirectionCosine",
    ]
    if include_Zemax_extra_fields:
        columns = columns + [
    "phase",
    "phase_dbl_err",
    "exr",
    "exi",
    "eyr",
    "eyi",
    "ezr",
    "ezi",
    ]

    df = pd.DataFrame(columns=columns)
    df.index.name = "RayNumber"
    return df