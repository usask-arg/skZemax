from typing import Union
from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import __LowLevelZemaxStringCheck__
from skZemax.skZemax_subfunctions._NCE_functions import _convert_raw_obj_input_, NCE_GetNumberOfObjects
from skZemax.skZemax_subfunctions._c_print import c_print as cp
import numpy as np
import xarray as xr
import os
type ZOSAPI_Editors_NCE_INCERow         = object #<- ZOSAPI.Editors.NCE.INCERow # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Editors_NCE_ObjectColumn    = object #<- ZOSAPI.Editors.NCE.ObjectColumn # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Editors_NCE_IEditorCell     = object #<- ZOSAPI.Editors.IEditorCell # The actual module is referenced by the base PythonStandaloneApplication class.

def _NCE_CheckDetector_GetInfo_(self, in_Object:int)->tuple[dict, int, int]:
    """
    A NCE worker function which gets basic information about a (nominal rectangular) detector.

    :param in_Object: An NCE object identified by an index.
    :type in_Object: int
    :return: tuple of detector's dict column data, number of detector rows, and number of detector columns
    :rtype: tuple[dict, int, int]
    """
    isDet, Nrows, Ncols = self.TheSystem.NCE.GetDetectorDimensions(in_Object, 0, 0)
    if not isDet:
        if self._verbose: cp('!@ly!@_NCE_CheckDetector_GetInfo_ :: NCE object at index of [!@lm!@{}!@ly!@] is not a detector.'.format(in_Object))
        return None, None, None
    detector_info  = self.NCE_GetAllColumnDataOfObject(self.NCE_GetObject(in_Object))
    return detector_info, Nrows, Ncols

def _NCE_GetDetector_InfoAndImage_Incoherent_(self, in_Object: int, data_type:int=1)->tuple[dict, np.ndarray]:
    """
    Looks up a surface/object of NCE, checks if it is a detector, and if it is will return info and image (all/Incoherent info).

    For Detector Rectangles, Detector Surfaces, and all faceted detectors

    data_type: int -- NOTE taken from documentation. I have not tested the following beyond flux 
    (I'm also not sure the numbers for facted detectors are right):

        0: flux <- Power (Watts) by default
        1: flux/area <- Irradiance (Watts/cm^2) by default
        2: flux/solid angle pixel <- Radiant Intensity (Watts/sr) by default - not radiance which is W/(area*sr)
        Note - only values 0 and 1 (for flux and flux/area) are supported for faceted detectors.

        For faceted detectors
        4: absorbed flux
        5: absorbed flux/area

        For Detector Volumes
        0: incident flux
        1: absorbed flux
        2: absorbed flux/unit volume

    :param in_Object: An NCE object identified by an index.
    :type in_Object: int
    :param data_type: The data type as described above, defaults to 1
    :type data_type: int, optional
    :return: tuple of detector dict column information, and an array of the detector image
    :rtype: tuple[dict, np.ndarray]
    """
    detector_info, Nrows, Ncols = self._NCE_CheckDetector_GetInfo_(in_Object)
    if detector_info is not None:
        detector_image = self.TheSystem.NCE.GetAllDetectorDataSafe(in_Object, data_type)
        # text output & FOR loops for OpticStudio will invert the vertical image
        # place plt.show() after clean up to release OpticStudio from memory
        detector_image = np.flipud(np.array(list(detector_image)).reshape(Nrows, Ncols))
        return detector_info, detector_image
    return None, None


def _NCE_GetDetector_InfoAndImage_Coherent_(self, in_Object: int, data_type:str)->tuple[dict, np.ndarray]:
    """
    Similar to :func:`_NCE_GetDetector_InfoAndImage_Incoherent_` but gets coherent data of the detector.

    :param in_Object: An NCE object identified by an index.
    :type in_Object: int
    :param data_type: Options are: 'Real', 'Imaginary', 'Amplitude', 'Power'
    :type data_type: str
    :return: tuple of detector dict column information, and an array of the detector image
    :rtype: tuple[dict, np.ndarray]
    """
    detector_info, Nrows, Ncols = self._NCE_CheckDetector_GetInfo_(in_Object)
    if detector_info is not None:
        detector_image = self.TheSystem.NCE.GetAllCoherentDataSafe(in_Object,
                                                                   self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.NCE.DetectorDataType, data_type))
        # text output & FOR loops for OpticStudio will invert the vertical image.
        detector_image = np.flipud(np.array(list(detector_image)).reshape(Nrows, Ncols))
        return detector_info, detector_image
    return None, None

def _NCE_GetRectDet_Complete_(self, in_RetDet: int)->xr.Dataset:
    """
    Runs both :func:`_NCE_GetDetector_InfoAndImage_Incoherent_` and :func:`_NCE_GetDetector_InfoAndImage_Coherent_` to build all detector data with units as applicable.
    This assumes (at least by naming convention) that the detector object at index in_RetDet is not a faceted detector or detector volume.
    I.e. this function is intended for things like rectangular detectors.

    :param in_RetDet: An NCE object identified by an index.
    :type in_RetDet: int
    :return: An xarray of all detector information
    :rtype: xr.Dataset
    """
    # Get all detector data.
    det_info, Incoherent_detector_incho_power   = self._NCE_GetDetector_InfoAndImage_Incoherent_(in_RetDet, 0)
    _, Incoherent_detector_incho_irrad          = self._NCE_GetDetector_InfoAndImage_Incoherent_(in_RetDet, 1)
    _, Incoherent_detector_incho_radinten       = self._NCE_GetDetector_InfoAndImage_Incoherent_(in_RetDet, 2)
    _, Coherent_Real_detector_image             = self._NCE_GetDetector_InfoAndImage_Coherent_(in_RetDet, 'Real')
    _, Coherent_Img_detector_image              = self._NCE_GetDetector_InfoAndImage_Coherent_(in_RetDet, 'Imag')
    _, Coherent_Amp_detector_image              = self._NCE_GetDetector_InfoAndImage_Coherent_(in_RetDet, 'Amp')
    _, Coherent_Power_detector_image            = self._NCE_GetDetector_InfoAndImage_Coherent_(in_RetDet, 'Power')
    # Saving netcdfs doesn't like '#' in the attrs, so replace them with 'Num' in the detector information
    keys = [x for x in det_info.keys()]
    for key in keys:
        det_info[key.replace('#', 'Num')] = det_info.pop(key)
    # Build System units as it concerns the detector data:
    unit_dict                                   = self.Utilities_GetAllSystemUnits()
    area_units                                  = unit_dict['AnalysisUnits'].split('Per')[-1].replace('Sq', '^2')
    det_unit_data                               = dict()
    prefix                                      = unit_dict['SourceUnitPrefix'] if 'None' not in unit_dict['SourceUnitPrefix'] else ''
    det_unit_data['Power Units']                = prefix+unit_dict['SourceUnits']
    prefix                                      = unit_dict['AnalysisUnitPrefix'] if 'None' not in unit_dict['AnalysisUnitPrefix'] else ''
    # The value returned by the Zemax API for the AnalysisUnits doesn't seem to be correct (It always returns Watts/cm^2 - regaurdless of units set in system)
    # Note that this is just a label issue. Values in the detector are still correct for the units of the system. I make this label as correct as I (currently) can.
    # The only thing which may be wrong is the area.
    det_unit_data['Irradiance Units']           = prefix+unit_dict['AnalysisUnits'].replace('Per', '/').replace('Sq', '^2').replace('Watts', det_unit_data['Power Units'] )
    det_unit_data['Radiant Intensity Units']    = det_unit_data['Power Units'] + '/Sr'
    det_unit_data['Radiance Units']             = det_unit_data['Power Units'] + '/' + area_units + '/Sr'
    det_unit_data['Phase Units']                = 'Degrees'
    det_unit_data['Distance Units']             = unit_dict['LensUnits']
    # Build images as Zemax does (according to their documentation). I have compared this with the actual Zemax UI and it seems to be correct.
    phase = np.flipud(np.arctan2(Coherent_Img_detector_image, Coherent_Real_detector_image) * 180 / np.pi)
    # Coherent Radiance is built in one of two ways depending on normalization (and if more than one pixel).
    if self.NCE_GetObject(in_RetDet).TypeData.NormalizeCoherentPower and np.prod(Incoherent_detector_incho_irrad.shape) > 1:
         Coherent_irrad = (np.nansum(Incoherent_detector_incho_irrad)/np.nansum(Coherent_Amp_detector_image**2))*(Coherent_Real_detector_image**2 + Coherent_Img_detector_image**2)
    else:
         Coherent_irrad = Incoherent_detector_incho_irrad*((Coherent_Real_detector_image**2 + Coherent_Img_detector_image**2)/(Coherent_Amp_detector_image**2))
    # Make the incoherent radiance as a function of position (Zemax assumes full hemisphere despite what the detector actually does).
    Inchoerent_radiance_position = Incoherent_detector_incho_irrad/(2*np.pi)
    # Make the incoherent radiance as a function of angle.
    area_of_detector    = float(det_info['X Half Width'])*2*float(det_info['Y Half Width'])*2
    # Making the assumption that angle maps to distance linearly (which I think Zemax does too).
    x_angles    = np.linspace(float(det_info['X Angle Min']), float(det_info['X Angle Max']), int(det_info['Num X Pixels']))
    y_angles    = np.linspace(float(det_info['Y Angle Min']), float(det_info['Y Angle Max']), int(det_info['Num Y Pixels']))
    XANG, YANG  = np.meshgrid(x_angles, y_angles)
    angle_grid  = np.sqrt(XANG**2 + YANG**2)
    Incoherent_radiance_angle = Incoherent_detector_incho_radinten/(area_of_detector*np.cos(np.deg2rad(angle_grid)))
    # Make Statistics
    stat_dict                                           = dict()
    stat_dict['Total Power']                            = '%0.4E' % np.nansum(Incoherent_detector_incho_power)
    stat_dict['Peak Power']                             = '%0.4E' % np.nanmax(Incoherent_detector_incho_power)
    stat_dict['Total Incoherent Irradiance']            = '%0.4E' % np.nansum(Incoherent_detector_incho_irrad)
    stat_dict['Peak Incoherent Irradiance']             = '%0.4E' % np.nanmax(Incoherent_detector_incho_irrad)
    stat_dict['Total Incoherent Radiative Intensity']   = '%0.4E' % np.nansum(Incoherent_detector_incho_radinten)
    stat_dict['Peak Incoherent Radiative Intensity']    = '%0.4E' % np.nanmax(Incoherent_detector_incho_radinten)
    stat_dict['Total Incoherent Radiance Position']     = '%0.4E' % np.nansum(Inchoerent_radiance_position)
    stat_dict['Peak Incoherent Radiance Position']      = '%0.4E' % np.nanmax(Inchoerent_radiance_position)
    stat_dict['Total Incoherent Radiance Angular']      = '%0.4E' % np.nansum(Incoherent_radiance_angle)
    stat_dict['Peak Incoherent Radiance Angular']       = '%0.4E' % np.nanmax(Incoherent_radiance_angle)
    stat_dict['Total Coherent Intensity']               = '%0.4E' % np.nansum(Coherent_irrad)
    stat_dict['Peak Coherent Intensity']                = '%0.4E' % np.nanmax(Coherent_irrad)
    stat_dict['Detector Index']                         = str(in_RetDet)
    stat_dict['X Pitch']                                = (2*float(det_info['X Half Width']))/float(det_info['Num X Pixels'])
    stat_dict['Y Pitch']                                = (2*float(det_info['Y Half Width']))/float(det_info['Num Y Pixels'])

    out = xr.Dataset(
        {
                'power'                           : (('y_pixel', 'x_pixel'), Incoherent_detector_incho_power.astype(float)),
                'incoherent_irradiance'           : (('y_pixel', 'x_pixel'), Incoherent_detector_incho_irrad.astype(float)),
                'incoherent_radiant_intensity'    : (('y_pixel', 'x_pixel'), Incoherent_detector_incho_radinten.astype(float)),
                'incoherent_radiance_position'    : (('y_pixel', 'x_pixel'), Inchoerent_radiance_position.astype(float)),
                'incoherent_radiance_angle'       : (('y_angle', 'x_angle'), Incoherent_radiance_angle.astype(float)),
                'detector_fov_angles'             : (('y_angle', 'x_angle'), angle_grid.astype(float)),
                'coherent_irradiance'             : (('y_pixel', 'x_pixel'), Coherent_irrad.astype(float)),
                'coherent_phase'                  : (('y_pixel', 'x_pixel'), phase.astype(float)),
                'coherent_real'                   : (('y_pixel', 'x_pixel'), Coherent_Real_detector_image.astype(float)),
                'coherent_imag'                   : (('y_pixel', 'x_pixel'), Coherent_Img_detector_image.astype(float)),
                'coherent_amp'                    : (('y_pixel', 'x_pixel'), Coherent_Amp_detector_image.astype(float)),
                'coherent_power'                  : (('y_pixel', 'x_pixel'), Coherent_Power_detector_image.astype(float)),
        },
        coords =
        {
                "y_pixel"   : ('y_pixel', np.arange(0, Incoherent_detector_incho_power.shape[0], 1).astype(int)),
                "y_distance": ('y_pixel',  np.linspace(-float(det_info['Y Half Width']), float(det_info['Y Half Width']), int(det_info['Num Y Pixels']))),
                "y_angle"   : ('y_angle',y_angles.astype(int)),
                "x_pixel"   : ('x_pixel', np.arange(0, Incoherent_detector_incho_power.shape[1], 1).astype(int)),
                "x_distance": ('x_pixel',  np.linspace(-float(det_info['X Half Width']), float(det_info['X Half Width']), int(det_info['Num X Pixels']))),
                "x_angle"   : ('x_angle',x_angles.astype(int)),
        })
    out.attrs = det_unit_data | stat_dict | det_info
    return out

def _NCE_GetDetector_InfoAndImage_Polar_(self, in_Object: int, data_type:str='Power')->tuple[dict, np.ndarray]:
    """
    Looks up a surface/object of NCE, checks if it is a detector, and if it is will return info and image.
    this function is for Polar Detectors.

    :param in_Object: An NCE object identified by an index.
    :type in_Object: int
    :param data_type: Options are: "Power", "PowerSolidAngle", "Lumens", "LumensSolidAngle", "Cx", "Cy", "u_T", "u_V", "TriX", "TriY", "TriZ", defaults to "Power"
    :type data_type: str, optional
    :return:  tuple of detector dict column information, and an array of the detector image
    :rtype: tuple[dict, np.ndarray]
    """
    detector_info, Nangles, Nradius = self._NCE_CheckDetector_GetInfo_(in_Object)
    if detector_info is not None:
        detector_image = self.TheSystem.NCE.GetAllPolarDetectorDataSafe(in_Object,
                                                                        self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.NCE.PolarDetectorDataType, data_type))
        # text output & FOR loops for OpticStudio will invert the vertical image.
        detector_image = np.flipud(np.array(list(detector_image)).reshape(Nangles, Nradius))
        return detector_info, detector_image
    return None, None

def _NCE_GetPolDet_Complete_(self, in_PolDet: int)->xr.Dataset:
    """
    Runs both _NCE_GetDetector_InfoAndImage_Incoherent_() and _NCE_GetDetector_InfoAndImage_Coherent_() to build all detector data with units as applicable.
    This assumes (at least by naming convention) that the detector object at index in_PolDet is not a faceted detector or detector volume.
    I.e. this function is intended for things like polar detectors.

    :param in_PolDet: An NCE object identified by an index.
    :type in_PolDet: int
    :return: An xarray of all detector information
    :rtype: xr.Dataset
    """
    # Get all detector data.
    det_info, Polar_Power   = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'Power')
    _, PolarPowerSr         = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'PowerSolidAngle')
    _, PolarLumens          = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'Lumens')
    _, PolarLumensSr        = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'LumensSolidAngle')
    _, PolarTriX            = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'TriX')
    _, PolarTriY            = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'TriY')
    _, PolarTriZ            = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'TriZ')
    _, PolarCx              = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'Cx')
    _, PolarCy              = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'Cy')
    _, PolaruT              = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'u_T')
    _, PolaruV              = self._NCE_GetDetector_InfoAndImage_Polar_(in_PolDet, 'u_V')

    # Saving netcdfs doesn't like '#' in the attrs, so replace them with 'Num' in the detector information
    keys = [x for x in det_info.keys()]
    for key in keys:
        det_info[key.replace('#', 'Num')] = det_info.pop(key)
    # Build System units as it concerns the detector data:
    unit_dict                                   = self.Utilities_GetAllSystemUnits()
    det_unit_data                               = dict()
    prefix                                      = unit_dict['SourceUnitPrefix'] if 'None' not in unit_dict['SourceUnitPrefix'] else ''
    det_unit_data['Power Units']                = prefix+unit_dict['SourceUnits']
    det_unit_data['Radiant Intensity Units']    = det_unit_data['Power Units'] + '/Sr'
    det_unit_data['Photopic Flux']              = 'Lumens'
    det_unit_data['Photopic Intensity']         = 'Lumens/Sr'
    # Build Polar Coords
    increment  = float(det_info['Maximum Angle'])/(int(det_info['Num Radial Pixels'])-1)
    polar_degs_pixel_start = (np.arange(0,int(det_info['Num Radial Pixels']),1)-0.5)*increment
    polar_degs_pixel_start[0] = 0
    polar_degs_pixel_end = np.roll(np.copy(polar_degs_pixel_start),-1)
    polar_degs_pixel_end[-1] = float(det_info['Maximum Angle'])
    azimuthal_degs      = np.arange(-180+(360/int(det_info['Num Angular Pixels'])), 180+0.01, 360/int(det_info['Num Angular Pixels']))

    # THGETA,RAD = np.meshgrid(azimuthal_degs,polar_degs_pixel_end)
    # fig = mplot.figure(figsize=[5,5])
    # # ax = fig.add_axes([0.1,0.1,0.8,0.8],polar=True)
    # mplot.axes(projection='polar')
    # mplot.pcolormesh(np.deg2rad(THGETA),RAD,Polar_Power.T,edgecolors='face')

    # Make Statistics
    stat_dict                                 = dict()
    stat_dict['Total Power']                  = '%0.4E' % np.nansum(Polar_Power)
    stat_dict['Peak Power']                   = '%0.4E' % np.nanmax(Polar_Power)
    stat_dict['Total Radiative Intensity']    = '%0.4E' % np.nansum(PolarPowerSr)
    stat_dict['Peak Radiative Intensity']     = '%0.4E' % np.nanmax(PolarPowerSr)
    stat_dict['Total Photopic Power']         = '%0.4E' % np.nansum(PolarLumens)
    stat_dict['Peak Photopic Power']          = '%0.4E' % np.nanmax(PolarLumens)
    stat_dict['Total Photopic Intensity']     = '%0.4E' % np.nansum(PolarLumensSr)
    stat_dict['Peak Photopic Intensity']      = '%0.4E' % np.nanmax(PolarLumensSr)
    stat_dict['Detector Index']               = str(in_PolDet)

    out = xr.Dataset(
        {
                'power'               : (('radial_angle', 'azimuthal_angle'), Polar_Power.astype(float).T),
                'radiant_intensity'   : (('radial_angle', 'azimuthal_angle'), PolarPowerSr.astype(float).T),
                'photopic_flux'       : (('radial_angle', 'azimuthal_angle'), PolarLumens.astype(float).T),
                'photopic_intensity'  : (('radial_angle', 'azimuthal_angle'), PolarLumensSr.astype(float).T),
                'tristimulus_x'       : (('radial_angle', 'azimuthal_angle'), PolarTriX.astype(float).T),
                'tristimulus_y'       : (('radial_angle', 'azimuthal_angle'), PolarTriY.astype(float).T),
                'tristimulus_z'       : (('radial_angle', 'azimuthal_angle'), PolarTriZ.astype(float).T),
                'Cx'                  : (('radial_angle', 'azimuthal_angle'), PolarCx.astype(float).T),
                'Cy'                  : (('radial_angle', 'azimuthal_angle'), PolarCy.astype(float).T),
                'uT'                  : (('radial_angle', 'azimuthal_angle'), PolaruT.astype(float).T),
                'uV'                  : (('radial_angle', 'azimuthal_angle'), PolaruV.astype(float).T),
        },
        coords =
        {
                "azimuthal_deg"             : ('azimuthal_angle', azimuthal_degs.astype(float)),
                "azimuthal_angle"           : ('azimuthal_angle', np.deg2rad(azimuthal_degs.astype(float))),
                "radial_deg"                : ('radial_angle', polar_degs_pixel_end.astype(float)),
                "radial_angle"              : ('radial_angle', np.deg2rad(polar_degs_pixel_end.astype(float))),
                "radial_deg_start_of_bin"   : ('radial_angle', polar_degs_pixel_start.astype(float)),
                "radial_rad_start_of_bin"   : ('radial_angle', np.deg2rad(polar_degs_pixel_start.astype(float))),
        })
    out.attrs = det_unit_data | stat_dict | det_info
    return out

def NCE_GetDetectorLocations(self)->list:
    """
    This function looks through each NCE object in the system and checks if it is a detector. 
    If it is, it returns the object's index in a list.

    :return: A list of NCE object indicies indicating the indices of detectors.
    :rtype: list
    """
    return [x for x in range(self.NCE_GetNumberOfObjects()) if self.TheSystem.NCE.GetDetectorDimensions(x, 0, 0)[0]]


def NCE_GetDetectorComplete(self, in_Object: Union[int, ZOSAPI_Editors_NCE_INCERow])->xr.Dataset:
    """
    This is the recommended and primariy function to get detector information of a Non-sequential ray trace.

    :param in_Object: An NCE (detector) object specifed as either an index or an NCE object itself.
    :type in_Object: Union[int, ZOSAPI_Editors_NCE_INCERow]
    :return: An xarray of the detector infomraiton.
    :rtype: xr.Dataset
    """
    in_Object       = self._convert_raw_obj_input_(in_Object, return_index=False)
    if 'DetectorRectangle'.lower() in str(in_Object.Type).lower():
        return self._NCE_GetRectDet_Complete_(self._convert_raw_obj_input_(in_Object, return_index=True))
    if 'DetectorPolar'.lower() in str(in_Object.Type).lower():
        return self._NCE_GetPolDet_Complete_(self._convert_raw_obj_input_(in_Object, return_index=True))

def _detector_file_name_checker_(self, in_Object: Union[int, ZOSAPI_Editors_NCE_INCERow], in_file_name:str)->str:
    """
    An NCE detector function working for making the right extensions in saved detector file names.

    :param in_Object: An NCE (detector) object specifed as either an index or an NCE object itself.
    :type in_Object: Union[int, ZOSAPI_Editors_NCE_INCERow]
    :param in_file_name: File name of detector data to save.
    :type in_file_name: str
    :return: a formatted file name
    :rtype: str
    """
    in_Object       = self._convert_raw_obj_input_(in_Object, return_index=False)
    if 'DetectorRectangle'.lower() in str(in_Object.Type).lower():
        if '.ddr' not in in_file_name[-4::].lower():
            in_file_name += '.DDR'
    if 'DetectorColor'.lower() in str(in_Object.Type).lower():
        if '.ddc' not in in_file_name[-4::].lower():
            in_file_name += '.DDC'
    if 'DetectorPolar'.lower() in str(in_Object.Type).lower():
        if '.ddp' not in in_file_name[-4::].lower():
            in_file_name += '.DDP'
    if 'DetectorPVolume'.lower() in str(in_Object.Type).lower():
        if '.ddv' not in in_file_name[-4::].lower():
            in_file_name += '.DDV'
    return os.path.abspath(in_file_name) 

def NCE_SaveDetectorInZemaxFormat(self, in_Object: Union[int, ZOSAPI_Editors_NCE_INCERow], in_file_name:str)->None:
    """
    Saves detector data in Zemax format (i.e. DDP or DDR).

    :param in_Object: An NCE (detector) object specifed as either an index or an NCE object itself.
    :type in_Object: Union[int, ZOSAPI_Editors_NCE_INCERow]
    :param in_file_name:  File name of detector data to save.
    :type in_file_name: str
    """
    in_file_name = self._detector_file_name_checker_(in_Object=in_Object, in_file_name=in_file_name)
    self.TheSystem.NCE.SaveDetector(self._convert_raw_obj_input_(in_Object, return_index=True), in_file_name)

def NCE_LoadDetectorInZemaxFormat(self, in_Object: Union[int, ZOSAPI_Editors_NCE_INCERow], in_file_name:str, sum_to_current_data:bool=False)->None:
    """
    Loads detector data in Zemax format (i.e. DDP or DDR). 

    :param in_Object: An NCE (detector) object specifed as either an index or an NCE object itself.
    :type in_Object: Union[int, ZOSAPI_Editors_NCE_INCERow]
    :param in_file_name: File name of detector data to load.
    :type in_file_name: str
    :param sum_to_current_data:  If set to true then the data from the file is summed to the existing detector data, else the detector is cleared first, defaults to False
    :type sum_to_current_data: bool, optional
    """
    in_file_name = self._detector_file_name_checker_(in_Object=in_Object, in_file_name=in_file_name)
    self.TheSystem.NCE.LoadDetector(self._convert_raw_obj_input_(in_Object, return_index=True), in_file_name, sum_to_current_data)

