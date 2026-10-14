import box as Box
import numpy as np
import pandas as pd
import struct
import warnings

# IEEE 754 binary32 signaling NaN (exponent all ones, quiet bit 0, non-zero payload), little-endian.
# TM-25 (§4.5.3) requires missing/not-provided float values to be signaling NaNs; quiet NaNs (what np.nan packs to) make the file invalid.
_TM25RAY_SIGNALING_NAN_BYTES_ = struct.pack('<I', 0x7FA00000)

def _float32_to_TM25RAY_bytes_(value:float)->bytes:
    """Packs a float as 4 little-endian binary32 bytes, writing any NaN as a signaling NaN.

    This is needed because ``struct.pack('<f', np.nan)`` produces a *quiet* NaN (0x7FC00000), which TM-25 (§4.5.3)
    defines as invalid. TM-25 uses signaling NaNs to mean "missing" or "not provided" (e.g. the Minimum/Maximum
    Wavelength header fields when the Spectral Data Identifier is 0 or 1). When read back with ``struct.unpack('<f', ...)``
    the signaling NaN becomes an ordinary Python ``nan``, so ``np.isnan`` checks keep working.

    :param value: Value to pack. Any NaN (quiet or signaling) is written as a signaling NaN.
    :type value: float
    :return: The 4-byte little-endian representation.
    :rtype: bytes
    """
    if np.isnan(value):
        return _TM25RAY_SIGNALING_NAN_BYTES_
    return struct.pack('<f', value)

def _header_and_flags_error_checking_(header_and_flags:Box)->Box:
    """Does error checking on the header and flag information of a TM25RAY file, following the error conditions of
    ANSI/IES TM-25-20(R25) §4.7.1 and §4.7.2 (section numbers are given with each check below).

    Where the general flag descriptions (§4.7.2.3/§4.7.2.5, which only mention Spectral Data Identifier options 2 and 4)
    and the ray field definitions (§4.8.1.7/§4.8.1.9, which cover options 1-4) differ, the more relaxed flag rule is enforced:
    for Spectral Data Identifier 2 or 4, radiant flux must be present per ray and luminous flux must be absent (error).
    For options 1 or 3 the same combination only fails the stricter ray field rule, so a warning is issued instead,
    since other software may apply the stricter rule and reject the file.

    A file giving neither a Total Luminous Flux nor a Total Radiant Flux is still valid (§4.7.1.4-5); a warning is issued
    instead of an error, since the software using the file is expected to ask the user for a flux value.

    :param header_and_flags: Header and flag information (output of :func:`_parse_header_and_flags_` for instance).
    :type header_and_flags: Box
    :raises Exception: FileType != TM25 (§4.7.1.1)
    :raises Exception: FileVersion != 2013 (§4.7.1.2)
    :raises Exception: Any known data flag is not 0 or 1 (§4.7.2)
    :raises Exception: NumberOfRays < 1 (§4.7.1.6)
    :raises Exception: SpectralDataIdentifier < 0 or SpectralDataIdentifier > 4 (§4.7.1.9)
    :raises Exception: SpectralDataIdentifier == 1 and SingleWavelength is not a positive number (§4.7.1.10)
    :raises Exception: SpectralDataIdentifier == 3|4 and NumberOfSpectralTables < 1 (§4.7.1.13)
    :raises Exception: NumberOfAdditionalRayDataItemsPerRay < 0 (§4.7.1.14)
    :raises Exception: SizeOfAdditionalTextBlock < 0 or SizeOfAdditionalTextBlock % 32 != 0 (§4.7.1.15)
    :raises Exception: PositionFlag != 1 or DirectionFlag != 1 (§4.7.2.1-2)
    :raises Exception: RadiantFluxStokesS0Flag == 0 and LuminousFluxYTristimulusFlag == 0 (§4.7.2.3, §4.7.2.5)
    :raises Exception: WavelengthFlag < 1 and SpectralDataIdentifier == 2 (§4.7.2.4)
    :raises Exception: SpectralDataIdentifier == 2|4 and RadiantFluxStokesS0Flag != 1 (§4.7.2.3); warns for 1|3 (§4.8.1.7)
    :raises Exception: SpectralDataIdentifier == 2|4 and LuminousFluxYTristimulusFlag != 0 (§4.7.2.5); warns for 1|3 (§4.8.1.9)
    :raises Exception: StokesFlag == 1 and RadiantFluxStokesS0Flag < 1 (§4.7.2.6)
    :raises Exception: TristimulusFlag == 1 and (LuminousFluxYTristimulusFlag < 1 or SpectralDataIdentifier != 0) (§4.7.2.7)
    :raises Exception: SpectrumIndexFlag == 1 is not equivalent to SpectralDataIdentifier == 4 (§4.7.2.8)
    :return: Passes back the given input unaltered.
    :rtype: Box
    """
    known_flags = ['PositionFlag', 'DirectionFlag', 'RadiantFluxStokesS0Flag', 'WavelengthFlag', 'LuminousFluxYTristimulusFlag', 'StokesFlag', 'TristimulusFlag', 'SpectrumIndexFlag']
    if header_and_flags.FileType != 'TM25':
        raise Exception('Non-valid TM25RAY file (FileType != TM25).')
    if header_and_flags.FileVersion != 2013:
        raise Exception('Non-valid TM25RAY file (FileVersion != 2013).')
    for flag in known_flags:
        if header_and_flags[flag] not in (0, 1):
            raise Exception(f'Non-valid TM25RAY file ({flag} is not 0 or 1).')
    if (np.isnan(header_and_flags.TotalLuminousFlux) or header_and_flags.TotalLuminousFlux <=0) and (np.isnan(header_and_flags.TotalRadiantFlux) or header_and_flags.TotalRadiantFlux <=0):
        warnings.warn('TM25RAY file gives neither a TotalLuminousFlux nor a TotalRadiantFlux. The file is still valid (TM-25 §4.7.1.4-5), but a flux value must be supplied by the user.')
    if header_and_flags.NumberOfRays < 1:
        raise Exception('Non-valid TM25RAY file (NumberOfRays < 1).')
    if header_and_flags.SpectralDataIdentifier < 0 or header_and_flags.SpectralDataIdentifier > 4:
        raise Exception('Non-valid TM25RAY file (SpectralDataIdentifier < 0 or SpectralDataIdentifier > 4).')
    if header_and_flags.SpectralDataIdentifier == 1 and not (header_and_flags.SingleWavelength > 0):
        raise Exception('Non-valid TM25RAY file (SpectralDataIdentifier == 1 and SingleWavelength is not a positive number).')
    if header_and_flags.SpectralDataIdentifier in (3, 4) and header_and_flags.NumberOfSpectralTables < 1:
        raise Exception('Non-valid TM25RAY file (SpectralDataIdentifier == 3|4 and NumberOfSpectralTables < 1).')
    if header_and_flags.NumberOfAdditionalRayDataItemsPerRay < 0:
        raise Exception('Non-valid TM25RAY file (NumberOfAdditionalRayDataItemsPerRay < 0).')
    if header_and_flags.SizeOfAdditionalTextBlock < 0 or header_and_flags.SizeOfAdditionalTextBlock % 32 != 0:
        raise Exception('Non-valid TM25RAY file (SizeOfAdditionalTextBlock < 0 or SizeOfAdditionalTextBlock % 32 != 0).')
    if header_and_flags.PositionFlag != 1:
        raise Exception('Non-valid TM25RAY file (PositionFlag != 1).')
    if header_and_flags.DirectionFlag != 1:
        raise Exception('Non-valid TM25RAY file (DirectionFlag != 1).')
    if header_and_flags.RadiantFluxStokesS0Flag == 0 and header_and_flags.LuminousFluxYTristimulusFlag == 0:
        raise Exception('Non-valid TM25RAY file (Neither RadiantFluxStokesS0Flag nor LuminousFluxYTristimulusFlag is set).')
    if header_and_flags.WavelengthFlag < 1 and header_and_flags.SpectralDataIdentifier==2:
        raise Exception('Non-valid TM25RAY file (WavelengthFlag < 1 and SpectralDataIdentifier == 2).')
    if header_and_flags.SpectralDataIdentifier in (2, 4) and header_and_flags.RadiantFluxStokesS0Flag != 1:
        raise Exception('Non-valid TM25RAY file (SpectralDataIdentifier == 2|4 and RadiantFluxStokesS0Flag != 1).')
    if header_and_flags.SpectralDataIdentifier in (2, 4) and header_and_flags.LuminousFluxYTristimulusFlag != 0:
        raise Exception('Non-valid TM25RAY file (SpectralDataIdentifier == 2|4 and LuminousFluxYTristimulusFlag != 0).')
    if header_and_flags.SpectralDataIdentifier in (1, 3) and header_and_flags.RadiantFluxStokesS0Flag != 1:
        warnings.warn('TM25RAY file has SpectralDataIdentifier == 1|3 without per-ray radiant flux (RadiantFluxStokesS0Flag != 1). '
                      'This is allowed by TM-25 §4.7.2.3 but not by the stricter §4.8.1.7, so other software may reject the file.')
    if header_and_flags.SpectralDataIdentifier in (1, 3) and header_and_flags.LuminousFluxYTristimulusFlag != 0:
        warnings.warn('TM25RAY file has SpectralDataIdentifier == 1|3 with per-ray luminous flux (LuminousFluxYTristimulusFlag == 1). '
                      'This is allowed by TM-25 §4.7.2.5 but not by the stricter §4.8.1.9, so other software may reject the file.')
    if header_and_flags.StokesFlag == 1 and header_and_flags.RadiantFluxStokesS0Flag < 1:
        raise Exception('Non-valid TM25RAY file (StokesFlag == 1 and RadiantFluxStokesS0Flag < 1).')
    if header_and_flags.TristimulusFlag == 1 and (header_and_flags.LuminousFluxYTristimulusFlag < 1 or header_and_flags.SpectralDataIdentifier != 0):
        raise Exception('Non-valid TM25RAY file (TristimulusFlag == 1 and (LuminousFluxYTristimulusFlag < 1 or SpectralDataIdentifier != 0)).')
    if (header_and_flags.SpectrumIndexFlag == 1) != (header_and_flags.SpectralDataIdentifier == 4):
        raise Exception('Non-valid TM25RAY file (SpectrumIndexFlag must be 1 if and only if SpectralDataIdentifier == 4).')
    return header_and_flags

def _ray_data_error_checking_(RayData:pd.DataFrame, header_and_flags:Box)->pd.DataFrame:
    """Does error checking on the per-ray data of a TM25RAY file, following the error conditions of
    ANSI/IES TM-25-20(R25) §4.8.1. It is used both when reading and before writing a file.

    The columns are looked up by their canonical names (as produced by :func:`_define_ray_block_contents_from_header_and_flags_`),
    e.g. ``StokesS1`` or ``PolarizationEllipseMajorAxis_XDirectionCosine``. The checks are:

        - no NaN values in any ray data line (§4.8.1, signaling NaNs are fatal in ray data),
        - if ``StokesFlag == 1``: each of S1, S2, S3 is within [-1, 1] and S1² + S2² + S3² <= 1 (§4.8.1.10-12),
          the polarization ellipse major axis vector is normalized and is orthogonal to the ray direction (§4.8.1.13-15),
        - if ``SpectrumIndexFlag == 1``: every spectrum index is an integer between 1 and NumberOfSpectralTables (§4.8.1.18).

    A tolerance of 1e-3 is used for the normalization and orthogonality checks, matching the 0.999-1.001 round-off
    window TM-25 gives for direction cosines (§4.8.1.4-6) and leaving room for single-precision storage.
    Non-normalized ray direction cosines are *not* an error (§4.8.1.4-6) and are not checked.

    :param RayData: Ray data with canonical column names, one row per ray.
    :type RayData: pd.DataFrame
    :param header_and_flags: Header and flag information describing the ray data.
    :type header_and_flags: Box
    :raises Exception: If any of the checks above fail.
    :return: Passes back the given RayData unaltered.
    :rtype: pd.DataFrame
    """
    tol = 1e-3
    if RayData is None or RayData.empty:
        return RayData
    if RayData.isna().to_numpy().any():
        raise Exception('Non-valid TM25RAY file (NaN found in ray data lines).')
    if header_and_flags.StokesFlag == 1:
        S = RayData[['StokesS1', 'StokesS2', 'StokesS3']].to_numpy(dtype=float)
        if np.any(np.abs(S) > 1 + tol) or np.any(np.sum(S**2, axis=1) > 1 + tol):
            raise Exception('Non-valid TM25RAY file (non-normalized Stokes vector: S1, S2, S3 must be in [-1, 1] with S1² + S2² + S3² <= 1).')
        M = RayData[['PolarizationEllipseMajorAxis_XDirectionCosine', 'PolarizationEllipseMajorAxis_YDirectionCosine', 'PolarizationEllipseMajorAxis_ZDirectionCosine']].to_numpy(dtype=float)
        if np.any(np.abs(np.sum(M**2, axis=1) - 1) > tol):
            raise Exception('Non-valid TM25RAY file (non-normalized polarization ellipse major axis vector).')
        k = RayData[['XDirectionCosine', 'YDirectionCosine', 'ZDirectionCosine']].to_numpy(dtype=float)
        k = k / np.linalg.norm(k, axis=1, keepdims=True)
        if np.any(np.abs(np.sum(M * k, axis=1)) > tol):
            raise Exception('Non-valid TM25RAY file (polarization ellipse major axis is not orthogonal to the ray direction).')
    if header_and_flags.SpectrumIndexFlag == 1:
        idx = RayData['SpectrumIndex'].to_numpy(dtype=float)
        if np.any(idx != np.round(idx)) or np.any(idx < 1) or np.any(idx > header_and_flags.NumberOfSpectralTables):
            raise Exception('Non-valid TM25RAY file (SpectrumIndex must be an integer between 1 and NumberOfSpectralTables).')
    return RayData