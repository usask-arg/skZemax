from box import Box
import struct
import numpy as np
import pandas as pd
from typing import Generator
from skZemax.ZemaxRaytraceSupplement.TM25RAY.reading_and_writeing_workers import _header_and_flags_error_checking_, _float32_to_TM25RAY_bytes_, _ray_data_error_checking_
from skZemax.ZemaxRaytraceSupplement.TM25RAY.reading_workers import _define_ray_block_contents_from_header_and_flags_

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

def _encode_str_(in_str: str, size_bytes: int, format: str = "utf-32-le",
) -> bytes:
    """Worker function to encode a TM25RAY string field as bytes.

    The encoded string is padded with ``\\x00`` bytes to fill exactly
    ``size_bytes`` bytes. If the encoded string exceeds the requested size,
    a ValueError is raised.

    TM-25 strings are UTF-32 (§4.5.4) in a little-endian file (§4.1), so the default is ``'utf-32-le'``, which
    writes no byte order mark. (Python's ``'utf-32'`` would prepend a 4-byte mark, which other readers may show
    as a leading character and which uses up one of the 1,000 characters a 4,000-byte field can hold.)

    :param in_str: string to encode as binary data
    :type in_str: str
    :param size_bytes: number of bytes to allocate for the string field
    :type size_bytes: int
    :param format: encoding scheme, defaults to 'utf-32-le'
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
    out.FileCreationDateAndTime                 = pd.Timestamp.now(tz="UTC").isoformat(timespec='seconds') # ISO 8601 YYYY-MM-DDThh:mm:ss+hh:mm (TM-25 §4.7.1.7)
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
        elif not SpectralTables.empty:
            # Several tables but no per-ray SpectrumIndex column to say which ray uses which table.
            raise Exception("Can not identify the correct SpectralDataIdentifier (several spectral tables given but no SpectrumIndex column).")
        else:
            # No wavelength column and no spectral tables: a watts/lumen based file without wavelength information (TM-25 §4.7.1.9 option 0).
            in_box.SpectralDataIdentifier = 0
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
    if current_column+6 <= len(columns):
        stokes_vector_present = (all('stokes' in x for x in columns[current_column:current_column+3]) and 's1' in columns[current_column] and 's2' in columns[current_column+1] and 's3' in columns[current_column+2])
        stokes_axis_present   = (all(('ellipse' in x and 'polarization' in x and 'major' in x and 'direction' in x and 'cosine' in x) for x in columns[current_column+3:current_column+6]) and 'x' in columns[current_column+3] and 'y' in columns[current_column+4] and 'z' in columns[current_column+5])
        out.StokesFlag = 1 if stokes_vector_present and stokes_axis_present else 0
        if out.StokesFlag == 1:
            current_column += 6
            if current_column == len(columns):
                return _return_formatted_header_and_flags_(out)
    #----------------------------------------------------------------------------------------------------------#
    if current_column+2 <= len(columns):
        out.TristimulusFlag = 1 if all('tristimulus' in x for x in columns[current_column:current_column+2]) and 'x' in columns[current_column] and 'z' in columns[current_column+1] else 0
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
    # Validate the ray data before anything is written. The writer detects columns by name fragments, so the columns are
    # first renamed to the canonical labels a reader would assign from these flags (any additional columns keep their names).
    n_additional = header_and_flags.NumberOfAdditionalRayDataItemsPerRay
    additional_labels = Box({'AdditionalRayDataColumnLabels': list(RayData.columns[-n_additional:]) if n_additional > 0 else []})
    canonical_labels = _define_ray_block_contents_from_header_and_flags_(header_and_flags=header_and_flags, additional_ray_labels=additional_labels)
    _ray_data_error_checking_(RayData.set_axis(canonical_labels, axis=1), header_and_flags)
    # Header float fields are packed as raw bytes ('4s') via _float32_to_TM25RAY_bytes_ so that missing values (NaN)
    # are written as signaling NaNs, as TM-25 §4.5.3 requires (struct's 'f' would write a quiet NaN, which is invalid).
    data_to_write = (
        _encode_str_(in_str=header_and_flags.FileType, size_bytes=4, format='ascii'),
        header_and_flags.FileVersion,
        header_and_flags.CreationMethod,
        _float32_to_TM25RAY_bytes_(header_and_flags.TotalLuminousFlux),
        _float32_to_TM25RAY_bytes_(header_and_flags.TotalRadiantFlux),
        header_and_flags.NumberOfRays,
        _encode_str_(in_str=header_and_flags.FileCreationDateAndTime, size_bytes=28, format='ascii'),
        header_and_flags.RayStartPosition,
        header_and_flags.SpectralDataIdentifier,
        _float32_to_TM25RAY_bytes_(header_and_flags.SingleWavelength),
        _float32_to_TM25RAY_bytes_(header_and_flags.MinimumWavelength),
        _float32_to_TM25RAY_bytes_(header_and_flags.MaximumWavelength),
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
            "<4s i i 4s 4s Q 28s i i 4s 4s 4s i i i 168x i i i i i i i i",
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

        # Zero-pad the block to a multiple of 32 bytes with 4-byte integer zeros (TM-25 §4.7.4, Table 4-4).
        # Every item written above is 4 bytes, so the number of padding integers is (bytes needed)/4.
        n_padding_ints = ((32 - (len(data_to_write)*4) % 32) % 32) // 4
        data_to_write.extend([0]*n_padding_ints)
        data_format += 'i '*n_padding_ints

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

    Every column is written as a little-endian 4-byte float, except a ``SpectrumIndex`` column (any column whose name
    contains both "spectrum" and "index"), which TM-25 §4.8.1.18 defines as a 4-byte integer. A numpy structured array
    is used so each column keeps its own type; converting the whole frame with ``to_numpy()`` would turn the
    integer column into floats, which ``struct``'s integer format cannot pack.

    :param in_buffer_generator: A generator to produce binary data. It should be set to after the writing of the additional text block in :func:`TM25RAY_write_file`
    :type in_buffer_generator: Generator[bytes, int, None]
    :param RayData: As defined above.
    :type RayData: pd.DataFrame
    """
    ray_line_dtype = np.dtype([(x, '<i4' if ('spectrum' in x.lower() and 'index' in x.lower()) else '<f4') for x in RayData.columns])
    ray_lines = np.empty(RayData.shape[0], dtype=ray_line_dtype)
    for x in RayData.columns:
        ray_lines[x] = RayData[x].to_numpy()
    in_buffer_generator.send(ray_lines.tobytes())

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

def _stokes_to_TM25RAY_polarization_(stokes:np.ndarray, ray_direction:np.ndarray=np.array([0.0, 0.0, 1.0]), reference_x:np.ndarray=np.array([1.0, 0.0, 0.0]))->pd.DataFrame:
    """Converts Stokes vectors measured in a user-chosen basis into the TM25RAY polarization columns
    (normalized Stokes S1, S2, S3 and the polarization ellipse major axis direction cosines).

    TM-25 (§4.8.1.13-15) defines the per-ray polarization vector M as the major axis of the polarization ellipse,
    and Zemax orients the ellipse it builds from a TM25RAY file using M only (see :func:`TM25RAY_MakePolarizedSourceFile`).
    Stokes vectors are therefore not written in the user basis directly. Instead the basis is rotated about the
    ray direction k by the ellipse azimuth so that its x-axis lies along the major axis. In that frame S2 = 0 and
    S1 >= 0, which is valid under both the strict and the loose reading of TM-25 and gives the intended state in Zemax.

    .. note::
        k always points along the direction of ray **propagation** (the way the light travels, i.e. the
        ``XDirectionCosine``, ``YDirectionCosine`` and ``ZDirectionCosine`` columns of the same rays), not towards the
        source. The basis therefore looks like the usual "x right, y up" frame to an observer looking back along the
        ray towards the source. Because y_ref = k × x_ref, reversing k with the same x_ref flips y_ref: for k = -Z and
        x_ref = +X, y_ref = -Y, so +S2 then appears at -45° in lab coordinates. Use x_ref = -X for backward rays
        to keep the lab sense of +45°.

    The user basis is (x_ref, y_ref, k) with y_ref = k × x_ref (right-handed, matching TM-25 §3.21), so that:

        - +S1 is linear polarization along x_ref,
        - +S2 is linear polarization at +45° from x_ref towards y_ref,
        - S3 is circular polarization (unchanged by the rotation about k).

    The conversion is psi = 0.5*atan2(S2, S1), M = cos(psi)*x_ref + sin(psi)*y_ref and
    (S1, S2, S3)_TM25 = (sqrt(S1² + S2²), 0, S3) / S0.

    Edge cases:

        - ``reference_x`` does not need to be exactly orthogonal to the ray. Its component along k is removed
          before use, so e.g. a lab +X can be used for slightly tilted rays. It must not be parallel to the ray.
        - If the linear part is zero (circular or unpolarized light) the azimuth is undefined; psi = 0 is used,
          so M = x_ref. Zemax ignores the orientation in that case.
        - M and -M describe the same ellipse (psi is only defined modulo 180°).

    :param stokes: Stokes vectors (S0, S1, S2, S3) in the user basis, shape (N, 4) or (4,). S0 must be > 0 and
        S1² + S2² + S3² <= S0². Any consistent unit is accepted because the output is normalized by S0.
    :type stokes: np.ndarray
    :param ray_direction: Ray direction vectors k, shape (N, 3) or (3,) (broadcast across rays). Normalized internally,
        defaults to np.array([0.0, 0.0, 1.0]) (+Z)
    :type ray_direction: np.ndarray, optional
    :param reference_x: Reference x-axis x_ref of the user basis, shape (N, 3) or (3,) (broadcast across rays).
        The defaults (k = +Z, x_ref = +X, so y_ref = +Y) give the conventional lab basis, defaults to np.array([1.0, 0.0, 0.0]) (+X)
    :type reference_x: np.ndarray, optional
    :raises ValueError: If S0 <= 0, if the Stokes vector is over-polarized (S1² + S2² + S3² > S0²), or if
        ``reference_x`` is (nearly) parallel to the ray direction.
    :return: A DataFrame with N rows and the columns ``StokesS1``, ``StokesS2``, ``StokesS3``,
        ``PolarizationEllipseMajorAxis_XDirectionCosine``, ``PolarizationEllipseMajorAxis_YDirectionCosine`` and
        ``PolarizationEllipseMajorAxis_ZDirectionCosine``, named as in :func:`_template_RayData_` so they can be
        assigned directly into a RayData frame. ``RadiantFluxStokesS0`` is not returned and should be set by the caller
        (S0 = 1 per ray is recommended for Zemax).
    :rtype: pd.DataFrame
    """
    stokes = np.atleast_2d(np.asarray(stokes, dtype=float))
    S0, S1, S2, S3 = stokes[:, 0], stokes[:, 1], stokes[:, 2], stokes[:, 3]
    if np.any(S0 <= 0):
        raise ValueError('All Stokes S0 values must be > 0.')
    if np.any(S1**2 + S2**2 + S3**2 > S0**2 * (1 + 1e-6)):
        raise ValueError('Found Stokes vectors with S1² + S2² + S3² > S0² (over-polarized).')
    # Build the right-handed user basis (x_ref, y_ref, k) for every ray.
    k = np.broadcast_to(np.asarray(ray_direction, dtype=float), (stokes.shape[0], 3))
    k = k / np.linalg.norm(k, axis=-1, keepdims=True)
    x_ref = np.broadcast_to(np.asarray(reference_x, dtype=float), (stokes.shape[0], 3))
    x_ref = x_ref - np.sum(x_ref * k, axis=-1, keepdims=True) * k  # remove any component along the ray
    x_norm = np.linalg.norm(x_ref, axis=-1, keepdims=True)
    if np.any(x_norm < 1e-9):
        raise ValueError('reference_x is parallel to the ray direction for at least one ray.')
    x_ref = x_ref / x_norm
    y_ref = np.cross(k, x_ref)
    # Rotate the basis about k by the ellipse azimuth so x lies on the major axis.
    psi = 0.5 * np.arctan2(S2, S1)
    M = np.cos(psi)[:, None] * x_ref + np.sin(psi)[:, None] * y_ref
    out = pd.DataFrame({
        "StokesS1": np.hypot(S1, S2) / S0,
        "StokesS2": np.zeros_like(S0),
        "StokesS3": S3 / S0,
        "PolarizationEllipseMajorAxis_XDirectionCosine": M[:, 0],
        "PolarizationEllipseMajorAxis_YDirectionCosine": M[:, 1],
        "PolarizationEllipseMajorAxis_ZDirectionCosine": M[:, 2],
    })
    out.index.name = "RayNumber"
    return out

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