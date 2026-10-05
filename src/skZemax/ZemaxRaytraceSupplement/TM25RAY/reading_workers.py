from box import Box
import struct
import numpy as np
import pandas as pd
from typing import Generator
from skZemax.ZemaxRaytraceSupplement.TM25RAY.reading_and_writeing_workers import _header_and_flags_error_checking_

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

    :param in_buffer_generator: A generator to produce binary data. It should be set to start reading after :func:`_parse_header_and_flags_`.
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

    :param in_buffer_generator:  A generator to produce binary data. It should be set to start reading after :func:`_parse_description_`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param header_and_flags: The output of :func:`_parse_header_and_flags_`
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

    :param in_buffer_generator: A generator to produce binary data. It should be set to start reading after :func:`_parse_spectral_tables_`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param header_and_flags: The output of :func:`_parse_header_and_flags_`
    :type header_and_flags: Box
    :return: A Box containing the list of column names. If there are no column names this Box contains an empty list
    :rtype: Box
    """
    out = Box({})
    out.AdditionalRayDataColumnLabels = [_decode_str_(struct.unpack("<512s", in_buffer_generator.send(512))[0]) for x in range(header_and_flags.NumberOfAdditionalRayDataItemsPerRay)]
    return out

def _parse_additional_text_block_(in_buffer_generator:Generator[bytes, int, None], header_and_flags:Box)->Box:
    """Parses any additional text in the TM25RAY file.

    :param in_buffer_generator:  A generator to produce binary data. It should be set to start reading after :func:`_parse_spectral_tables_`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param header_and_flags:  The output of :func:`_parse_header_and_flags_`
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
   

    :param header_and_flags: The output of :func:`_parse_header_and_flags_`
    :type header_and_flags: Box
    :param additional_ray_labels: The output of :func:`_parse_additional_ray_data_column_labels_`
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

    :param in_buffer_generator: A generator to produce binary data. It should be set to start reading after :func:`_parse_additional_text_block_`.
    :type in_buffer_generator: Generator[bytes, int, None]
    :param header_and_flags: The output of :func:`_parse_header_and_flags_`
    :type header_and_flags: Box
    :param additional_ray_labels:  The output of :func:`_parse_additional_ray_data_column_labels_`
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
