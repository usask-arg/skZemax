

from box import Box
import struct
import numpy as np
from typing import Generator

def read_binary_block(filename:str)->Generator[bytes, int, None]:
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

def decode_str(in_bytes:bytes, format:str='utf-32')->str:
    """Worker function to decode a TM25RAY field as a string.

    :param in_bytes: array of bytes expected to form a string
    :type in_bytes: bytes
    :param format: decoding scheme, defaults to 'utf-32'
    :type format: str, optional
    :return: the binary data as text
    :rtype: str
    """
    return in_bytes.decode(format).rstrip("\x00")

def parse_header_and_flags(in_buffer_generator:Generator[bytes, int, None])->Box:
    """This function reads the file header information and data flags of a TM25RAY file.
    The contents of the header and flags are conditionally checked to ensure a valid TM25RAY file. 
    If the file in invalid, an error is raised.


    :param in_buffer_generator:  A generator to produce binary data. It should be set to read from the start of the file.
    :type in_buffer_generator: Generator[bytes, int, None]
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
    out.FileType                                = decode_str(buffer_contents[0], format='ascii')
    if out.FileType != 'TM25':
        raise Exception('Attempted to read a non-valid TM25RAY file (FileType != TM25).')
    out.FileVersion                             = buffer_contents[1]
    if out.FileVersion != 2013:
        raise Exception('Attempted to read a non-valid TM25RAY file (FileVersion != 2013).')
    out.CreationMethod                          = buffer_contents[2]
    out.TotalLuminousFlux                       = buffer_contents[3]
    out.TotalRadiantFlux                        = buffer_contents[4]
    if (np.isnan(out.TotalLuminousFlux) or out.TotalLuminousFlux <=0) and (np.isnan(out.TotalRadiantFlux) or out.TotalRadiantFlux <=0):
        raise Exception('Attempted to read a non-valid TM25RAY file (Neither TotalLuminousFlux or TotalRadiantFlux given).') 
    out.NumberOfRays                            = buffer_contents[5]
    if out.NumberOfRays < 1:
        raise Exception('Attempted to read a non-valid TM25RAY file (NumberOfRays < 1).') 
    out.FileCreationDateAndTime                 = decode_str(buffer_contents[6], format='ascii')
    out.RayStartPosition                        = buffer_contents[7]
    out.SpectralDataIdentifier                  = buffer_contents[8]
    if out.SpectralDataIdentifier < 1 or out.SpectralDataIdentifier > 4:
            raise Exception('Attempted to read a non-valid TM25RAY file (SpectralDataIdentifier < 1 or SpectralDataIdentifier > 4).') 
    out.SingleWavelength                        = buffer_contents[9]
    out.MinimumWavelength                       = buffer_contents[10]
    out.MaximumWavelength                       = buffer_contents[11]
    out.NumberOfSpectralTables                  = buffer_contents[12]
    out.NumberOfAdditionalRayDataItemsPerRay    = buffer_contents[13]
    out.SizeOfAdditionalTextBlock               = buffer_contents[14]
    if out.SizeOfAdditionalTextBlock % 32 != 0:
        raise Exception('Attempted to read a non-valid TM25RAY file (SizeOfAdditionalTextBlock % 32 != 0).') 
    # Parse the flags
    out.PositionFlag                    = buffer_contents[15]
    if out.PositionFlag < 1:
        raise Exception('Attempted to read a non-valid TM25RAY file (PositionFlag < 1).') 
    out.DirectionFlag                   = buffer_contents[16]
    if out.DirectionFlag < 1:
            raise Exception('Attempted to read a non-valid TM25RAY file (DirectionFlag < 1).') 
    out.RadiantFluxStokesS0Flag         = buffer_contents[17]
    out.WavelengthFlag                  = buffer_contents[18]
    if (out.WavelengthFlag < 1 and out.SpectralDataIdentifier==2):
        raise Exception('Attempted to read a non-valid TM25RAY file (WavelengthFlag < 1 and SpectralDataIdentifier == 2).') 
    out.LuminousFluxYTristimulusFlag    = buffer_contents[19]
    if ((out.SpectralDataIdentifier == 2 or out.SpectralDataIdentifier == 4)  and out.RadiantFluxStokesS0Flag==1 and out.LuminousFluxYTristimulusFlag > 0):
        raise Exception('Attempted to read a non-valid TM25RAY file (SpectralDataIdentifier == 2|4 and RadiantFluxStokesS0Flag == 1 and LuminousFluxYTristimulusFlag > 0).') 
    out.StokesFlag                      = buffer_contents[20]
    if (out.StokesFlag == 1 and out.RadiantFluxStokesS0Flag < 1):
        raise Exception('Attempted to read a non-valid TM25RAY file (StokesFlag == 1 and RadiantFluxStokesS0Flag < 1).') 
    out.TristimulusFlag                 = buffer_contents[21]
    if (out.TristimulusFlag == 1 and (out.LuminousFluxYTristimulusFlag < 1 or out.SpectralDataIdentifier != 4)):
        raise Exception('Attempted to read a non-valid TM25RAY file (TristimulusFlag == 1 and (LuminousFluxYTristimulusFlag < 1 or SpectralDataIdentifier != 4)).') 
    out.SpectrumIndexFlag               = buffer_contents[22]    
    if (out.SpectrumIndexFlag != 1 and out.SpectralDataIdentifier == 4):
        raise Exception('Attempted to read a non-valid TM25RAY file (SpectrumIndexFlag != 1 and SpectralDataIdentifier == 4).') 
    return out


def parse_description(in_buffer_generator:Generator[bytes, int, None])->Box:
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
    out.NameOfLightSource                         = decode_str(buffer_contents[0])
    out.ManufacturerOfLightSource                 = decode_str(buffer_contents[1])
    out.CreatorOfOpticalLightSourceModel          = decode_str(buffer_contents[2])
    out.CreatorOfTheRayFile                       = decode_str(buffer_contents[3])
    out.MeasurementEquipmentSimulationSoftware    = decode_str(buffer_contents[4])
    out.CameraInformation                         = decode_str(buffer_contents[5])
    out.LightSourceOperationInformation           = decode_str(buffer_contents[6])
    out.AdditionalInformation                     = decode_str(buffer_contents[7])
    out.DataReferenceToLightSourceGeometry        = decode_str(buffer_contents[8])
    return out

def parse_spectral_tables(in_buffer_generator:Generator[bytes, int, None])->Box:
    pass

# buffer_generator        = read_binary_block(r"C:\Users\dsl935\Documents\Zemax\Objects\Sources\Source Files\test.tm25ray")
buffer_generator    = read_binary_block(r"C:\Users\dsl935\Documents\Zemax\Objects\Sources\Source Files\testspect.tm25ray")
next(buffer_generator)  # start the generator
header_and_flags    = parse_header_and_flags(buffer_generator)
description         = parse_description(buffer_generator)
if not np.isnan(header_and_flags.NumberOfSpectralTables) and header_and_flags.NumberOfSpectralTables > 0 and (header_and_flags.SpectralDataIdentifier == 3 or header_and_flags.SpectralDataIdentifier == 4):
    parse_spectral_tables(buffer_generator)
if header_and_flags.SizeOfAdditionalTextBlock > 0 and header_and_flags.SizeOfAdditionalTextBlock % 32 == 0:
    pass

a = 1