import box as Box
import numpy as np

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