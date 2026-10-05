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
    _write_ray_data_
)
from pathlib import Path
from box import Box
import pandas as pd
import struct
from skZemax.skZemaxClass import skZemaxClass 

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

def write_TM25RAY_file(path_to_file:str|Path, RayData:pd.DataFrame, SpectralTables:pd.DataFrame=pd.DataFrame(), AdditionalTextBlock:str='')->None:
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

if __name__ == '__main__':
    import os
    pd.set_option("display.width", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", None)
    skZ = skZemaxClass()
    ZemaxTest = read_TM25RAY_file(skZ.Utilities_ZemaxInstallationSourceDir() + os.sep + "test.tm25ray")
    write_TM25RAY_file(path_to_file=skZ.Utilities_ZemaxInstallationSourceDir() + os.sep + 'testwrite.tm25ray', 
                       RayData=ZemaxTest.RayData, SpectralTables=ZemaxTest.SpectralTables, AdditionalTextBlock=ZemaxTest.AdditionalTextBlock)
    ZemaxTestAgain = read_TM25RAY_file(skZ.Utilities_ZemaxInstallationSourceDir() + os.sep + 'testwrite.tm25ray')

    del skZ
    skZ = None