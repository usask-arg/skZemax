

from box import Box
import struct
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Generator

# ------------------------------------------------------------------------------------------------------------------------------------------------------ #
# Functions for reading or writing a TM25RAY file
# ------------------------------------------------------------------------------------------------------------------------------------------------------ #
def _header_and_flags_error_checking_(header_and_flags:Box)->Box:
    """Does error checking on the header and flag information of a TM25RAY file.

    :param header_and_flags: Header and flag information (output of :func:`_parse_header_and_flags_` for instance).
    :type header_and_flags: Box
    :raises Exception: FileType != TM25
    :raises Exception: FileVersion != 2013
    :raises Exception: Neither TotalLuminousFlux or TotalRadiantFlux give
    :raises Exception: NumberOfRays < 1
    :raises Exception: SpectralDataIdentifier < 1 or SpectralDataIdentifier > 4
    :raises Exception: SizeOfAdditionalTextBlock % 32 != 0
    :raises Exception: PositionFlag < 1
    :raises Exception: DirectionFlag < 1
    :raises Exception: WavelengthFlag < 1 and SpectralDataIdentifier == 2
    :raises Exception: SpectralDataIdentifier == 2|4 and RadiantFluxStokesS0Flag == 1 and LuminousFluxYTristimulusFlag > 0
    :raises Exception: StokesFlag == 1 and RadiantFluxStokesS0Flag < 1
    :raises Exception: TristimulusFlag == 1 and (LuminousFluxYTristimulusFlag < 1 or SpectralDataIdentifier != 4)
    :raises Exception: SpectrumIndexFlag != 1 and SpectralDataIdentifier == 4
    :return: Passes back the given input unaltered.
    :rtype: Box
    """
    if header_and_flags.FileType != 'TM25':
        raise Exception('Non-valid TM25RAY file (FileType != TM25).')
    if header_and_flags.FileVersion != 2013:
        raise Exception('Non-valid TM25RAY file (FileVersion != 2013).')
    if (np.isnan(header_and_flags.TotalLuminousFlux) or header_and_flags.TotalLuminousFlux <=0) and (np.isnan(header_and_flags.TotalRadiantFlux) or header_and_flags.TotalRadiantFlux <=0):
        raise Exception('Non-valid TM25RAY file (Neither TotalLuminousFlux or TotalRadiantFlux given).') 
    if header_and_flags.NumberOfRays < 1:
        raise Exception('Non-valid TM25RAY file (NumberOfRays < 1).') 
    if header_and_flags.SpectralDataIdentifier < 0 or header_and_flags.SpectralDataIdentifier > 4:
        raise Exception('Non-valid TM25RAY file (SpectralDataIdentifier < 1 or SpectralDataIdentifier > 4).') 
    if header_and_flags.SizeOfAdditionalTextBlock % 32 != 0:
        raise Exception('Non-valid TM25RAY file (SizeOfAdditionalTextBlock % 32 != 0).') 
    if header_and_flags.PositionFlag < 1:
        raise Exception('Non-valid TM25RAY file (PositionFlag < 1).') 
    if header_and_flags.DirectionFlag < 1:
        raise Exception('Non-valid TM25RAY file (DirectionFlag < 1).') 
    if header_and_flags.WavelengthFlag < 1 and header_and_flags.SpectralDataIdentifier==2:
        raise Exception('Non-valid TM25RAY file (WavelengthFlag < 1 and SpectralDataIdentifier == 2).') 
    if (header_and_flags.SpectralDataIdentifier == 2 or header_and_flags.SpectralDataIdentifier == 4)  and header_and_flags.RadiantFluxStokesS0Flag==1 and header_and_flags.LuminousFluxYTristimulusFlag > 0:
        raise Exception('Non-valid TM25RAY file (SpectralDataIdentifier == 2|4 and RadiantFluxStokesS0Flag == 1 and LuminousFluxYTristimulusFlag > 0).') 
    if header_and_flags.StokesFlag == 1 and header_and_flags.RadiantFluxStokesS0Flag < 1:
        raise Exception('Non-valid TM25RAY file (StokesFlag == 1 and RadiantFluxStokesS0Flag < 1).')
    if header_and_flags.TristimulusFlag == 1 and (header_and_flags.LuminousFluxYTristimulusFlag < 1 or header_and_flags.SpectralDataIdentifier != 4):
        raise Exception('Non-valid TM25RAY file (TristimulusFlag == 1 and (LuminousFluxYTristimulusFlag < 1 or SpectralDataIdentifier != 4)).')
    if header_and_flags.SpectrumIndexFlag != 1 and header_and_flags.SpectralDataIdentifier == 4:
        raise Exception('Non-valid TM25RAY file (SpectrumIndexFlag != 1 and SpectralDataIdentifier == 4).') 
    return header_and_flags

# ------------------------------------------------------------------------------------------------------------------------------------------------------ #
# Functions to read a TM25RAY file
# ------------------------------------------------------------------------------------------------------------------------------------------------------ #
def _read_binary_block_(filename:str)->Generator[bytes, int, None]:
    """This function constructs a generator for reading in binary data.
    This generator should be started with and external call of `next(buffer_generator)`
    This generator will *read and advance* the buffer a specific number of bytes with a call of `buffer_generator.send(int)`
    This generator will *rewind* a specific number of bytes with a call of `buffer_generator.send(-int)`. 
    After a *rewind* the information must be read again with `buffer_generator.send(int)`

    :param filename: Full path to the binary file to open.
    :type filename: str
    :raises EOFError: If requested bytes is not available.
    :yield: The binary generator.
    :rtype: Generator[bytes, int, None]
    """
    with open(filename, "rb") as f:
        request = yield  # get the first request
        while True:
            if request >= 0:
                chunk = f.read(request)
                if len(chunk) != request:
                    raise EOFError(
                        f"Expected {request} bytes, "
                        f"got {len(chunk)}"
                    )
                request = yield chunk
            else:
                # Negative number means "step backward". 
                # Another call to read will be reburied to get the data (again). 
                # This simply moves the buffer back.
                f.seek(request, 1)
                request = yield

def _decode_str_(in_bytes:bytes, format:str='utf-32')->str:
    """Worker function to decode a TM25RAY field as a string.

    :param in_bytes: array of bytes expected to form a string
    :type in_bytes: bytes
    :param format: decoding scheme, defaults to 'utf-32'
    :type format: str, optional
    :return: the binary data as text
    :rtype: str
    """
    return in_bytes.decode(format).rstrip("\x00")

def _parse_header_and_flags_(in_buffer_generator:Generator[bytes, int, None])->Box:
    """This function reads the file header information and data flags of a TM25RAY file.
    The contents of the header and flags are conditionally checked to ensure a valid TM25RAY file. 
    If the file in invalid, an error is raised.


    :param in_buffer_generator:  A generator to produce binary data. It should be set to read from the start of the file.
    :type in_buffer_generator: Generator[bytes, int, None]
    :return: The contents of the file header and data flags.
    :rtype: Box
    """
    # Read in the header and flags:
    # The header is the first 256 bytes, the flags are the last 32 bytes.
    buffer = in_buffer_generator.send(288)
    buffer_contents= struct.unpack(
        "<4s i i f f Q 28s i i f f f i i i 168x i i i i i i i i",
        buffer
    )
    out                                         = Box({})
    # Parse the header
    out.FileType                                = _decode_str_(buffer_contents[0], format='ascii')
    out.FileVersion                             = buffer_contents[1]
    out.CreationMethod                          = buffer_contents[2]
    out.TotalLuminousFlux                       = buffer_contents[3]
    out.TotalRadiantFlux                        = buffer_contents[4]
    out.NumberOfRays                            = buffer_contents[5]
    out.FileCreationDateAndTime                 = _decode_str_(buffer_contents[6], format='ascii')
    out.RayStartPosition                        = buffer_contents[7]
    out.SpectralDataIdentifier                  = buffer_contents[8]
    out.SingleWavelength                        = buffer_contents[9]
    out.MinimumWavelength                       = buffer_contents[10]
    out.MaximumWavelength                       = buffer_contents[11]
    out.NumberOfSpectralTables                  = buffer_contents[12]
    out.NumberOfAdditionalRayDataItemsPerRay    = buffer_contents[13]
    out.SizeOfAdditionalTextBlock               = buffer_contents[14]
    # Parse the flags
    out.PositionFlag                            = buffer_contents[15]
    out.DirectionFlag                           = buffer_contents[16]
    out.RadiantFluxStokesS0Flag                 = buffer_contents[17]
    out.WavelengthFlag                          = buffer_contents[18]
    out.LuminousFluxYTristimulusFlag            = buffer_contents[19]
    out.StokesFlag                              = buffer_contents[20]
    out.TristimulusFlag                         = buffer_contents[21]
    out.SpectrumIndexFlag                       = buffer_contents[22]
    return _header_and_flags_error_checking_(out)


def _parse_description_(in_buffer_generator:Generator[bytes, int, None])->Box:
    """This function reads the description header block of a TM25RAY file.

    :param in_buffer_generator: A generator to produce binary data. It should be set to start reading after :func:`parse_header_and_flags`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :return: The file descriptions
    :rtype: Box
    """
    buffer = in_buffer_generator.send(36000)
    buffer_contents= struct.unpack(
        "<4000s 4000s 4000s 4000s 4000s 4000s 4000s 4000s 4000s",
        buffer
    )
    out                                           = Box({})
    out.NameOfLightSource                         = _decode_str_(buffer_contents[0])
    out.ManufacturerOfLightSource                 = _decode_str_(buffer_contents[1])
    out.CreatorOfOpticalLightSourceModel          = _decode_str_(buffer_contents[2])
    out.CreatorOfTheRayFile                       = _decode_str_(buffer_contents[3])
    out.MeasurementEquipmentSimulationSoftware    = _decode_str_(buffer_contents[4])
    out.CameraInformation                         = _decode_str_(buffer_contents[5])
    out.LightSourceOperationInformation           = _decode_str_(buffer_contents[6])
    out.AdditionalInformation                     = _decode_str_(buffer_contents[7])
    out.DataReferenceToLightSourceGeometry        = _decode_str_(buffer_contents[8])
    return out

def _parse_spectral_tables_(in_buffer_generator:Generator[bytes, int, None], header_and_flags:Box)->Box:
    """This function will parse all spectral tables within the TM25RAY file (if any are present). 
    Error checking is done as the tables are read, and the binary buffer is advanced to the end of this block.

    Spectral table(s) are parsed into a pd.DataFrame with the format of:

    +------------+---------------+------------+
    | Wavelengths| RelativeWeight| TableIndex |
    +------------+---------------+------------+
    | ...        |    ...        |     1      |
    +------------+---------------+------------+
                       //
    +------------+---------------+------------+
    | ...        |    ...        |     n      |
    +------------+---------------+------------+                     

    ...where n is the total number of tables in the file. If there are no tables then an empty pd.DataFrame is made.  

    :param in_buffer_generator:  A generator to produce binary data. It should be set to start reading after :func:`parse_description`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param header_and_flags: The output of :func:`parse_header_and_flags`
    :type header_and_flags: Box
    :return: The spectral table(s) formatted into a pd.dataframe with columns = ['Wavelengths', 'RelativeWeight', 'TableIndex'] returned inside of a Box under the field of 'SpectralTables'. If not tables are present then 'SpectralTables' is a empty df.
    :rtype: Box
    """
    def _parse_table_():
        num_data_pairs= struct.unpack(
            "<i",
            in_buffer_generator.send(4)
        )[0]
        data_table = struct.unpack(
            f"<{num_data_pairs*2}f",
            in_buffer_generator.send(num_data_pairs*2*4)
        )
        if num_data_pairs <= 0:
            raise Exception(f'Spectral table {idx+1} returned a zero or negative number of data paris.') 
        table_out = pd.DataFrame({
                        "Wavelengths": np.asarray(data_table[::2]),
                        "RelativeWeight": np.asarray(data_table[1::2]),
                    })
        if np.any(table_out.Wavelengths<= 0)  or np.any(table_out.RelativeWeight<= 0):
            raise Exception(f'Found zero or negative wavelengths or relative weights in spectral table {idx+1}.') 
        return table_out, (num_data_pairs*2*4) + 4

    out = Box({})
    out.SpectralTables = pd.DataFrame()
    if not np.isnan(header_and_flags.NumberOfSpectralTables) and header_and_flags.NumberOfSpectralTables > 0 and (header_and_flags.SpectralDataIdentifier == 3 or header_and_flags.SpectralDataIdentifier == 4):
        total_bytes_read = 0
        dfs = []
        for idx in range(header_and_flags.NumberOfSpectralTables):
            df_out, bytes_read = _parse_table_()
            df_out['TableIndex'] = idx+1
            dfs.append(df_out)
            total_bytes_read += bytes_read
        out.SpectralTables = pd.concat(dfs, ignore_index=True)
        # Advance the buffer past the padding added to the end of the spectral table.
        # (the total spectral table block should be a number of bytes which is a multiple of 32 by definition).
        padding = struct.unpack(
                f"<{(total_bytes_read%32)}i",
                in_buffer_generator.send(
                (total_bytes_read%32)*4)
            )
        if len(padding)>1 and int(np.sum(np.abs(padding)))>0:
            raise Exception('Found non-zero data in the expected spectral table padding.') 
    return out

def _parse_additional_ray_data_column_labels_(in_buffer_generator:Generator[bytes, int, None], header_and_flags:Box)->Box:
    """This function parses the block of the TM25RAY file that lists the labels of any additional ray data.

    :param in_buffer_generator: A generator to produce binary data. It should be set to start reading after :func:`parse_spectral_tables`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param header_and_flags: The output of :func:`parse_header_and_flags`
    :type header_and_flags: Box
    :return: A Box containing the list of column names. If there are no column names this Box contains an empty list
    :rtype: Box
    """
    out = Box({})
    out.AdditionalRayDataColumnLabels = [_decode_str_(struct.unpack("<512s", in_buffer_generator.send(512))[0]) for x in range(header_and_flags.NumberOfAdditionalRayDataItemsPerRay)]
    return out

def _parse_additional_text_block_(in_buffer_generator:Generator[bytes, int, None], header_and_flags:Box)->Box:
    """Parses any additional text in the TM25RAY file.

    :param in_buffer_generator:  A generator to produce binary data. It should be set to start reading after :func:`parse_additional_ray_data_column_labels`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param header_and_flags:  The output of :func:`parse_header_and_flags`
    :type header_and_flags: Box
    :raises Exception: SizeOfAdditionalTextBlock % 32 != 0
    :return: The additional text in a Box under the field 'AdditionalTextBlock'. If there is no additional text then '' is in this field.
    :rtype: Box
    """
    out = Box({})
    if header_and_flags.SizeOfAdditionalTextBlock % 32 != 0:
        raise Exception('Size of additional text block is not a multiple of 32.')
    out.AdditionalTextBlock = _decode_str_(struct.unpack(f"<{header_and_flags.SizeOfAdditionalTextBlock}s", in_buffer_generator.send(header_and_flags.SizeOfAdditionalTextBlock))[0])
    return out

def _define_ray_block_contents_from_header_and_flags_(header_and_flags:Box, additional_ray_labels:Box)->list:
    """This is a worker function for :func:`parse_ray_data`. 
    This function looks at the header and flags in the file and determines the content of what each ray block should have.
   

    :param header_and_flags: The output of :func:`parse_header_and_flags`
    :type header_and_flags: Box
    :param additional_ray_labels: The output of :func:`parse_additional_ray_data_column_labels`
    :type additional_ray_labels: Box
    :return: A list of names - properly ordered for the binary data in the TM25RAY file - of all the information attached to one ray.
    :rtype: list
    """
    # Ray data should always have these else it is not valid
    ray_block_labels = ['XPosition', 'YPosition', 'ZPosition', 'XDirectionCosine', 'YDirectionCosine', 'ZDirectionCosine']
    # In the below, if the flag(s) of each condition are set then ray data should have the properties added to the list or the file is not valid.
    if header_and_flags.RadiantFluxStokesS0Flag == 1 or header_and_flags.StokesFlag == 1 or header_and_flags.SpectralDataIdentifier > 0:
        ray_block_labels += ['RadiantFluxStokesS0']
    if header_and_flags.WavelengthFlag == 1:
        ray_block_labels += ['Wavelength']
    if header_and_flags.LuminousFluxYTristimulusFlag == 1 and header_and_flags.SpectralDataIdentifier == 0:
        ray_block_labels += ['LuminousFluxYTristimulus']
    if header_and_flags.StokesFlag == 1:
        ray_block_labels += ['StokesS1', 'StokesS2', 'StokesS3', 'PolarizationEllipseMajorAxis_XDirectionCosine', 'PolarizationEllipseMajorAxis_YDirectionCosine', 'PolarizationEllipseMajorAxis_ZDirectionCosine']
    if header_and_flags.TristimulusFlag == 1:
        ray_block_labels += ['XTristimulus', 'ZTristimulus']
    if header_and_flags.SpectrumIndexFlag == 1:
        ray_block_labels += ['SpectrumIndex']
    if len(additional_ray_labels.AdditionalRayDataColumnLabels) > 0:
        ray_block_labels += list(additional_ray_labels.AdditionalRayDataColumnLabels)
    return ray_block_labels

def _parse_ray_data_(in_buffer_generator:Generator[bytes, int, None], header_and_flags:Box, additional_ray_labels:Box)->Box:
    """This function parses all the ray data within the TM25RAY file. The rays are parsed into a pd.DataFrame following:

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

    :param in_buffer_generator: A generator to produce binary data. It should be set to start reading after :func:`parse_additional_text_block`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param header_and_flags: The output of :func:`parse_header_and_flags`
    :type header_and_flags: Box
    :param additional_ray_labels:  The output of :func:`parse_additional_ray_data_column_labels`
    :type additional_ray_labels: Box
    :return: All ray information formatted into a pd.DataFrame and stored in a Box under the field 'RayData`. If no rays are in the file Box.RayData = None is returned instead.
    :rtype: Box
    """
    out = Box({}) 
    if header_and_flags.NumberOfRays > 0:
        ray_block_labels = _define_ray_block_contents_from_header_and_flags_(header_and_flags=header_and_flags, additional_ray_labels=additional_ray_labels)
        total_buffer_format = '<'+' '.join(['f' if 'SpectrumIndex' not in x else 'i' for x in ray_block_labels]*header_and_flags.NumberOfRays)
        total_ray_data = np.asarray(struct.unpack(
                    total_buffer_format, in_buffer_generator.send(len(ray_block_labels)*4*header_and_flags.NumberOfRays))).reshape(-1, len(ray_block_labels))
        df = pd.DataFrame(total_ray_data, columns=ray_block_labels)
        df.index.name = 'RayNumber'
        out.RayData = df
    else:
        out.RayData = None
    return out

# ------------------------------------------------------------------------------------------------------------------------------------------------------ #
# Functions to write a TM25RAY file
# ------------------------------------------------------------------------------------------------------------------------------------------------------ #

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


def _define_ray_block_contents_from_ray_info_(RayData:pd.DataFrame, SpectralTables:pd.DataFrame=pd.DataFrame())->Box:
    """This is a worker function for writing TM25RAY files (:func:`write_TM25RAY_file`). 
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
    :param SpectralTables: _description_, defaults to pd.DataFrame()
    :type SpectralTables: pd.DataFrame, optional
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
    out.SizeOfAdditionalTextBlock               = 0
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
        if not SpectralTables.empty and len(SpectralTables.TableIndex.unique()) and in_box.SpectrumIndexFlag == 0:
            in_box.NumberOfSpectralTables == 1
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


def _write_header_and_flags_(in_buffer_generator:Generator[bytes, int, None], RayData:pd.DataFrame, SpectralTables:pd.DataFrame=pd.DataFrame())->Box:
    """This function works out the headers and flags which should be in the file given the ray data and (optional) spectral tables.

    :param in_buffer_generator:  A generator to produce binary data. It should be set to read from the start of the file.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param RayData: The ray data. See description in :func:`_define_ray_block_contents_from_ray_info_`
    :type RayData: pd.DataFrame
    :param SpectralTables: The spectral data. See description in :func:`_define_ray_block_contents_from_ray_info_`, defaults to pd.DataFrame()
    :type SpectralTables: pd.DataFrame, optional
    :return: The determined headers and flags of the file (which have already been written).
    :rtype: Box
    """
    header_and_flags = _define_ray_block_contents_from_ray_info_(RayData=RayData, SpectralTables=SpectralTables)
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



# ------------------------------------------------------------------------------------------------------------------------------------------------------ #
# Functions to invoke
# ------------------------------------------------------------------------------------------------------------------------------------------------------ #
def read_TM25RAY_file(path_to_file:str|Path)->Box:
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

def write_TM25RAY_file(path_to_file:str|Path, RayData:pd.DataFrame, SpectralTables:pd.DataFrame=pd.DataFrame())->None:
    buffer_generator = _write_binary_block_(str(Path(str(path_to_file)).with_suffix('.TM25RAY')))
    next(buffer_generator) # start the generator
    header_and_flags = _write_header_and_flags_(in_buffer_generator=buffer_generator, RayData=RayData, SpectralTables=SpectralTables)
    buffer_generator.close()

if __name__ == '__main__':
    pd.set_option("display.width", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", None)



    def return_all_files_of_type_in_dir(
        basedirectory: str, filetype: str
    ) -> np.ndarray[Path]:
        """This function returns all files of the given extension type within the base-directory and all of its sub-directories.

        :param str basedirectory: Base dircotry of the files
        :param str filetype: the extension of the file type
        :return np.ndarray[Path]: array of all file Path objects, or just None if nothing is found.
        """
        files = list(Path(basedirectory).rglob(f"*.{filetype.strip(' ').strip('.')}"))
        if not files:
            log.warning(f"Could not find any [{filetype}] files in [{basedirectory}]")
            return None
        return np.array(files)


    ZemaxTest = read_TM25RAY_file(r"C:\Users\dsl935\Documents\Zemax\Objects\Sources\Source Files\test.tm25ray")
    examples = []
    for file in return_all_files_of_type_in_dir(r'C:\Users\dsl935\Downloads\EXAMPLE_TM25RAY_FILES', '.tm25ray'):
        print(file)
        examples.append(read_TM25RAY_file(file))

    write_TM25RAY_file(path_to_file=r'C:\argdev\_Reopsitories\ZemaxRepos\skZemax\src\stand_alone\testwrite.tm25ray', 
                       RayData=ZemaxTest.RayData, SpectralTables=ZemaxTest.SpectralTables)
    a= 1
