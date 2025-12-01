type ZOSAPI_Tools_ILayouts = object #<- ZOSAPI.Tools.ILayouts  # The actual module is referenced by the base PythonStandaloneApplication class.


def _Visualization_SEQ_Common_(self,
                           myLayout:ZOSAPI_Tools_ILayouts,
                           start_surface_index:int,
                           end_surface_index:int,
                           save_image:bool,
                           saved_image_location:str,
                           output_pixel_width:int,
                           output_pixel_height:int,
                           number_of_rays:int,
                           delete_vignetted:bool,
                           field_index:int, 
                           wavelength_index:int, 
                           fletch_rays:bool, 
                           ray_line_thickness:str, 
                           ):
    """
    This function sets options common to all versions of sequential mode visualization.
    This function should be called by one of :func:`Visualization_SEQ_2DCrossSection`, :func:`Visualization_SEQ_3DViewer`, or :func:`Visualization_SEQ_ShadedModel`.

    :param myLayout: The layout object for rendering.
    :type myLayout: ZOSAPI_Tools_ILayouts
    :param start_surface_index: The starting surface
    :type start_surface_index: int
    :param end_surface_index: The ending surface
    :type end_surface_index: int
    :param save_image: If should save the image
    :type save_image: bool
    :param saved_image_location: Image save location
    :type saved_image_location: str
    :param output_pixel_width: Image width in pixels
    :type output_pixel_width: int
    :param output_pixel_height: Image height in pixels
    :type output_pixel_height: int
    :param number_of_rays: Number of rays to render
    :type number_of_rays: int
    :param delete_vignetted: If vignetted rays are removed from render.
    :type delete_vignetted: bool
    :param field_index: Field index.
    :type field_index: int
    :param wavelength_index: Wavelength index.
    :type wavelength_index: int
    :param fletch_rays: If rays are fletched.
    :type fletch_rays: bool
    :param ray_line_thickness: Ray line thickness.
    :type ray_line_thickness: str

    """
    
    if end_surface_index < 0:
        end_surface_index = self.LDE_GetNumberOfSurfaces() + (end_surface_index + 1)
    if output_pixel_width is not None:
        myLayout.OutputPixelWidth=int(output_pixel_width)
    if output_pixel_height is not None:
        myLayout.OutputPixelWidth=int(output_pixel_height)
    myLayout.StartSurface           = int(start_surface_index)
    myLayout.EndSurface             = int(end_surface_index)
    myLayout.SaveImageAsFile        = bool(save_image)
    myLayout.OutputFileName         = str(saved_image_location)
    myLayout.NumberOfRays           = int(number_of_rays)
    myLayout.Field                  = int(field_index)
    myLayout.Wavelength             = int(wavelength_index)
    myLayout.FletchRays             = bool(fletch_rays)
    myLayout.DeleteVignetted        = bool(delete_vignetted)
    myLayout.RaysLineThickness      = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.LineThicknessOptions, ray_line_thickness)



def Visualization_SEQ_2DCrossSection(self,
                                     start_surface_index            : int=1,
                                     end_surface_index              : int=-1,
                                     wavelength_index               : int=-1,
                                     field_index                    : int=-1,
                                     number_of_rays                 : int=7,
                                     save_image                     : bool=True,
                                     saved_image_location           : str='2DCrossSection.png',
                                     output_pixel_width             : int=3840,
                                     output_pixel_height            : int=2160,
                                     surface_line_thickness         : str='Thickest',
                                     ray_line_thickness             : str='Thickest',
                                     fletch_rays                    : bool=False,
                                     color_rays_by                  : str='Field',
                                     marginal_and_chief_ray_only    : bool=False,
                                     delete_vignetted               : bool=False,
                                     y_stretch                      : float=1.0,
                                     configuration                  : int=1):
    """
    Make and save an image of the 2D cross section of the system (see https://community.zemax.com/zos-api-12/api-layout-plot-python-4731).
    This function is meant for sequential systems.

    :param start_surface_index: Starting surface of the export, defaults to 1
    :type start_surface_index: int, optional
    :param end_surface_index: Ending surface of the export, defaults to -1
    :type end_surface_index: int, optional
    :param wavelength_index: The wavelength index to use. If set to -1, all wavelengths will be displayed, defaults to -1
    :type wavelength_index: int, optional
    :param field_index: The field index to use. If set to -1, all fields will be displayed, defaults to -1
    :type field_index: int, optional
    :param number_of_rays: Number of rays to render, defaults to 7
    :type number_of_rays: int, optional
    :param save_image: Sets saving the image as a file, defaults to True
    :type save_image: bool, optional
    :param saved_image_location: location to where the image will be saved, defaults to '2DCrossSection.png'
    :type saved_image_location: str, optional
    :param output_pixel_width: Width of the image in pixels, defaults to 3840
    :type output_pixel_width: int, optional
    :param output_pixel_height: Height of the image in pixels, defaults to 2160
    :type output_pixel_height: int, optional
    :param surface_line_thickness: Thickness to apply to surface lines. Options are: "Thinnest", "Thin", "Standard", "Thick", and "Thickest", defaults to 'Thickest'
    :type surface_line_thickness: str, optional
    :param ray_line_thickness: Thickness to apply to ray lines. Options are: "Thinnest", "Thin", "Standard", "Thick", and "Thickest", defaults to 'Thickest', defaults to 'Thickest'
    :type ray_line_thickness: str, optional
    :param fletch_rays: If rays are fletched, defaults to False
    :type fletch_rays: bool, optional
    :param color_rays_by: Scheme by which rays are colored. Options are: "Fields", "Waves", and "Wavelengths", defaults to 'Field'
    :type color_rays_by: str, optional
    :param marginal_and_chief_ray_only: Only include marginal and chief rays, defaults to False
    :type marginal_and_chief_ray_only: bool, optional
    :param delete_vignetted: Rays which are vignetted are not rendered, defaults to False
    :type delete_vignetted: bool, optional
    :param y_stretch: Stretching to apply along Y, defaults to 1.0
    :type y_stretch: float, optional
    :param configuration: Configurations to render, defaults to 1
    :type configuration: int, optional

    """

    if number_of_rays < 0:
        number_of_rays=1
    if not self.System_GetIfInSequentialMode():
        self.System_SetSequentialMode()
    myLayout = self.TheSystem.Tools.Layouts.OpenCrossSectionExport()
    _Visualization_SEQ_Common_(self, myLayout          = myLayout,
                                start_surface_index   = start_surface_index,
                                end_surface_index     = end_surface_index,
                                save_image            = save_image,
                                saved_image_location  = saved_image_location,
                                output_pixel_width    = output_pixel_width,
                                output_pixel_height   = output_pixel_height,
                                wavelength_index      = wavelength_index,
                                field_index           = field_index,
                                number_of_rays        = number_of_rays,
                                fletch_rays           = fletch_rays,
                                ray_line_thickness    = ray_line_thickness,
                                delete_vignetted      = delete_vignetted
                                )
    myLayout.ColorRaysBy                = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.ColorRaysByCrossSectionOptions, color_rays_by)
    myLayout.SurfaceLineThickness       = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.LineThicknessOptions, surface_line_thickness)
    myLayout.MarginalAndChiefRayOnly    = bool(marginal_and_chief_ray_only)
    myLayout.YStretch                   = float(y_stretch)
    myLayout.Configuration              = 2 
    myLayout.RunAndWaitForCompletion()
    myLayout.Close()

def Visualization_SEQ_3DViewer(self,
                               start_surface_index    : int=1,
                               end_surface_index      : int=-1,
                               wavelength_index       : int=-1,
                               field_index            : int=-1,
                               number_of_rays           : int=7,
                               save_image             : bool=True,
                               saved_image_location   : str='3DView.png',
                               output_pixel_width       : int=3840,
                               output_pixel_height      : int=2160,
                               surface_line_thickness   : str='Thickest',
                               ray_line_thickness      : str='Thickest',
                               fletch_rays             : bool=False,
                               delete_vignetted        : bool=False,
                               color_rays_by            : str='Field', 
                               ray_pattern_type         : str='XYFan', 
                               hide_lens_faces          : bool=False,
                               hide_lens_edges          : bool=False,
                               draw_paraxial_pupils     : bool=False,
                               camera_viewpoint_angle_X  : float=-30.0,
                               camera_viewpoint_angle_Y  : float=35.0,
                               camera_viewpoint_angle_Z  : float=45.0,
                               configuration_offset_X   : float=0.0,
                               configuration_offset_Y   : float=0.0,
                               configuration_offset_Z   : float=0.0,
                               draw_real_entrance_pupils : str='Off', 
                               draw_real_exit_pupils     : str='Off'):
    """
    Make and save an image of the system in 3d (see https://community.zemax.com/zos-api-12/api-layout-plot-python-4731).
    This function is meant for sequential systems.

    :param start_surface_index: Starting surface of the export, defaults to 1
    :type start_surface_index: int, optional
    :param end_surface_index:Ending surface of the export, defaults to -1
    :type end_surface_index: int, optional
    :param wavelength_index: he wavelength index to use. If set to -1, all wavelengths will be displayed, defaults to -1
    :type wavelength_index: int, optional
    :param field_index: The field index to use. If set to -1, all fields will be displayed, defaults to -1
    :type field_index: int, optional
    :param number_of_rays: Number of rays to render, defaults to 7
    :type number_of_rays: int, optional
    :param save_image: Sets saving the image as a file, defaults to True
    :type save_image: bool, optional
    :param saved_image_location: location to where the image will be saved, defaults to  '3DView.png'
    :type saved_image_location: str, optional
    :param output_pixel_width:  Width of the image in pixels, defaults to 3840
    :type output_pixel_width: int, optional
    :param output_pixel_height: Height of the image in pixels, defaults to 2160
    :type output_pixel_height: int, optional
    :param surface_line_thickness: Thickness to apply to surface lines. Options are: "Thinnest", "Thin", "Standard", "Thick", and "Thickest", defaults to 'Thickest'
    :type surface_line_thickness: str, optional
    :param ray_line_thickness: Thickness to apply to ray lines. Options are: "Thinnest", "Thin", "Standard", "Thick", and "Thickest", defaults to 'Thickest', defaults to 'Thickest'
    :type ray_line_thickness: str, optional
    :param fletch_rays: If rays are fletched, defaults to False
    :type fletch_rays: bool, optional
    :param delete_vignetted: Rays which are vignetted are not rendered, defaults to False
    :type delete_vignetted: bool, optional
    :param color_rays_by: Scheme by which rays are colored. Options are: "Fields", "Waves", and "Wavelengths", defaults to 'Field'
    :type color_rays_by: str, optional
    :param ray_pattern_type: Ray pattern type. Options are: 'XYFan', 'XFan', 'YFan', 'Ring', 'List', 'Random', 'Grid', defaults to 'XYFan'
    :type ray_pattern_type: str, optional
    :param hide_lens_faces: If true will hide the faces of lens, defaults to False
    :type hide_lens_faces: bool, optional
    :param hide_lens_edges: If true will hide the edges of lens, defaults to False
    :type hide_lens_edges: bool, optional
    :param draw_paraxial_pupils: If true will draw paraxial pupils , defaults to False
    :type draw_paraxial_pupils: bool, optional
    :param camera_viewpoint_angle_X: X angle of the imaged viewpoint perspective, defaults to -30.0
    :type camera_viewpoint_angle_X: float, optional
    :param camera_viewpoint_angle_Y: Y angle of the imaged viewpoint perspective, defaults to 35.0
    :type camera_viewpoint_angle_Y: float, optional
    :param camera_viewpoint_angle_Z: Z angle of the imaged viewpoint perspective, defaults to 45.0
    :type camera_viewpoint_angle_Z: float, optional
    :param configuration_offset_X: X offset of the image, defaults to 0.0
    :type configuration_offset_X: float, optional
    :param configuration_offset_Y: Y offset of the image, defaults to 0.0
    :type configuration_offset_Y: float, optional
    :param configuration_offset_Z: Z offset of the image, defaults to 0.0
    :type configuration_offset_Z: float, optional
    :param draw_real_entrance_pupils: How to draw real entrance pupil. Options are: 'Off', '4','8','16','32', defaults to 'Off'
    :type draw_real_entrance_pupils: str, optional
    :param draw_real_exit_pupils: How to draw real exit pupil. Options are: 'Off', '4','8','16','32', defaults to 'Off'
    :type draw_real_exit_pupils: str, optional
    """
    if not self.System_GetIfInSequentialMode():
        self.System_SetSequentialMode()
    myLayout = self.TheSystem.Tools.Layouts.Open3DViewerExport()
    _Visualization_SEQ_Common_(self, myLayout          = myLayout,
                                start_surface_index   = start_surface_index,
                                end_surface_index     = end_surface_index,
                                save_image            = save_image,
                                saved_image_location  = saved_image_location,
                                output_pixel_width    = output_pixel_width,
                                output_pixel_height   = output_pixel_height,
                                wavelength_index      = wavelength_index,
                                field_index           = field_index,
                                number_of_rays          = number_of_rays,
                                fletch_rays           = fletch_rays,
                                ray_line_thickness    = ray_line_thickness,
                                delete_vignetted      = delete_vignetted)
    myLayout.RayPattern               = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.General.RayPatternType, ray_pattern_type)
    myLayout.SurfaceLineThickness     = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.LineThicknessOptions, surface_line_thickness)
    myLayout.HideLensFaces            = bool(hide_lens_faces)
    myLayout.HideLensEdges            = bool(hide_lens_edges)
    myLayout.DrawParaxialPupils       = bool(draw_paraxial_pupils)
    myLayout.CameraViewpointAngleX    = float(camera_viewpoint_angle_X)
    myLayout.CameraViewpointAngleY    = float(camera_viewpoint_angle_Y)
    myLayout.CameraViewpointAngleZ    = float(camera_viewpoint_angle_Z)
    myLayout.ConfigurationOffsetX     = float(configuration_offset_X)
    myLayout.ConfigurationOffsetY     = float(configuration_offset_Y)
    myLayout.ConfigurationOffsetZ     = float(configuration_offset_Z)
    myLayout.ColorRaysBy              = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.ColorRaysByOptions, color_rays_by)
    myLayout.DrawRealEntrancePupils   = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.RealPupilOptions, draw_real_entrance_pupils)
    myLayout.DrawRealExitPupils       = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.RealPupilOptions, draw_real_exit_pupils)
    myLayout.RunAndWaitForCompletion()
    myLayout.Close()

def Visualization_SEQ_ShadedModel(self,
                               start_surface_index        : int=1,
                               end_surface_index          : int=-1,
                               wavelength_index           : int=-1,
                               field_index                : int=-1,
                               number_of_rays             : int=7,
                               save_image                 : bool=True,
                               saved_image_location       : str='ShadedModel.png',
                               output_pixel_width         : int=3840,
                               output_pixel_height        : int=2160,
                               ray_line_thickness        : str='Thickest',
                               fletch_rays                : bool=False,
                               delete_vignetted           : bool=False,
                               color_rays_by              : str='Field',
                               ray_pattern_type           : str='XYFan',
                               camera_viewpoint_angle_X  : float=-30.0,
                               camera_viewpoint_angle_Y  : float=35.0,
                               camera_viewpoint_angle_Z  : float=45.0,
                               configuration_offset_X     : float=0.0,
                               configuration_offset_Y     : float=0.0,
                               configuration_offset_Z     : float=0.0,
                               opacity                    : str='All50Percent',
                               background                 : str='White',
                               draw_section               : str='P100',
                               angular_segments           : str='128',
                               radial_segments            : str='128',
                               brightness                 : str='50'):
    """
    Make and save a Shaded model of the system
    see https://community.zemax.com/zos-api-12/api-layout-plot-python-4731

    :param start_surface_index:Starting surface of the export, defaults to 1
    :type start_surface_index: int, optional
    :param end_surface_index: Ending surface of the export, defaults to -1
    :type end_surface_index: int, optional
    :param wavelength_index: The wavelength index to use. If set to -1, all wavelengths will be displayed, defaults to -1
    :type wavelength_index: int, optional
    :param field_index: The field index to use. If set to -1, all fields will be displayed, defaults to -1
    :type field_index: int, optional
    :param number_of_rays:  Number of rays to render, defaults to 7
    :type number_of_rays: int, optional
    :param save_image: Sets saving the image as a file, defaults to True
    :type save_image: bool, optional
    :param saved_image_location: location to where the image will be saved, defaults to  'ShadedModel.png'
    :type saved_image_location: str, optional
    :param output_pixel_width: Width of the image in pixels, defaults to 3840
    :type output_pixel_width: int, optional
    :param output_pixel_height: Height of the image in pixels, defaults to 2160
    :type output_pixel_height: int, optional
    :param ray_line_thickness: Thickness to apply to surface lines. Options are: "Thinnest", "Thin", "Standard", "Thick", and "Thickest", defaults to 'Thickest'
    :type ray_line_thickness: str, optional
    :param fletch_rays: If rays are fletched, defaults to False
    :type fletch_rays: bool, optional
    :param delete_vignetted: Rays which are vignetted are not rendered, defaults to False
    :type delete_vignetted: bool, optional
    :param color_rays_by: Scheme by which rays are colored. Options are: "Fields", "Waves", and "Wavelengths", defaults to 'Field'
    :type color_rays_by: str, optional
    :param ray_pattern_type: Ray pattern to render. Options are: 'XYFan', 'XFan', 'YFan', 'Ring', 'List', 'Random', 'Grid', defaults to 'XYFan'
    :type ray_pattern_type: str, optional
    :param camera_viewpoint_angle_X: X angle of the imaged viewpoint perspective, defaults to 30.0
    :type camera_viewpoint_angle_X: float, optional
    :param camera_viewpoint_angle_Y:  Y angle of the imaged viewpoint perspective, defaults to 35.0
    :type camera_viewpoint_angle_Y: float, optional
    :param camera_viewpoint_angle_Z: Z angle of the imaged viewpoint perspective, defaults to 45.0
    :type camera_viewpoint_angle_Z: float, optional
    :param configuration_offset_X: X offset of the image, defaults to 0.0
    :type configuration_offset_X: float, optional
    :param configuration_offset_Y: Y offset of the image, defaults to 0.0
    :type configuration_offset_Y: float, optional
    :param configuration_offset_Z: Z offset of the image, defaults to 0.0
    :type configuration_offset_Z: float, optional
    :param opacity: Opacity of the render. Options are: 'Ignore', 'Consider', 'All50Percent', defaults to 'All50Percent'
    :type opacity: str, optional
    :param background: Background color of the render. Options are "White", "Black", "Red", "Green", "Blue", "DarkGreen", "DarkBlue", "Color##" (where ## = 01 - 24), and "Gradient##" (where ## = 01-10), defaults to 'White'
    :type background: str, optional
    :param draw_section: Draw section option. options are: 'P100', 'P75', 'P50', and 'P25', , defaults to 'P100'
    :type draw_section: str, optional
    :param angular_segments: Number of angular segments. Options are: '8', '16', '32', '64', '128', defaults to '128'
    :type angular_segments: str, optional
    :param radial_segments: Number of radial segments. Options are: '8', '16', '32', '64', '128', defaults to '128'
    :type radial_segments: str, optional
    :param brightness: Brightness of the render. A percentage given as a string in steps of 10, defaults to '50'
    :type brightness: str, optional

    """
    if not self.System_GetIfInSequentialMode(): #
        self.System_SetSequentialMode()
    myLayout = self.TheSystem.Tools.Layouts.OpenShadedModelExport()
    _Visualization_SEQ_Common_(self, myLayout          = myLayout,
                                start_surface_index   = start_surface_index,
                                end_surface_index     = end_surface_index,
                                save_image            = save_image,
                                saved_image_location  = saved_image_location,
                                output_pixel_width    = output_pixel_width,
                                output_pixel_height   = output_pixel_height,
                                wavelength_index      = wavelength_index,
                                field_index           = field_index,
                                number_of_rays        = number_of_rays,
                                fletch_rays           = fletch_rays,
                                ray_line_thickness   = ray_line_thickness,
                                delete_vignetted      = delete_vignetted)
    myLayout.RayPattern               = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.General.RayPatternType, ray_pattern_type)
    myLayout.CameraViewpointAngleX    = float(camera_viewpoint_angle_X)
    myLayout.CameraViewpointAngleY    = float(camera_viewpoint_angle_Y)
    myLayout.CameraViewpointAngleZ    = float(camera_viewpoint_angle_Z)
    myLayout.ConfigurationOffsetX     = float(configuration_offset_X)
    myLayout.ConfigurationOffsetY     = float(configuration_offset_Y)
    myLayout.ConfigurationOffsetZ     = float(configuration_offset_Z)
    myLayout.ColorRaysBy              = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.ColorRaysByOptions, color_rays_by)
    myLayout.Opacity                  = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.OpacityOptions, opacity)
    myLayout.Background               = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.BackgroundOptions, background)
    myLayout.DrawSection              = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.DrawSectionOptions, draw_section)
    myLayout.AngularSegments          = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.NumberSegmentsOptions, angular_segments)
    myLayout.RadialSegments           = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.NumberSegmentsOptions, radial_segments)
    myLayout.Brightness               = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.BrightnessOptions, brightness)
    myLayout.RunAndWaitForCompletion()
    myLayout.Close()

def _Visualization_NSC_Common_(self,
                           myLayout:ZOSAPI_Tools_ILayouts,
                           save_image:bool,
                           saved_image_location:str,
                           output_pixel_width:int,
                           output_pixel_height:int,
                           ray_trace_options:str,
                           color_rays_by_NSC_options:str,
                           surface_line_thickness:str,
                           rays_line_thickness:str,
                           camera_viewpoint_angle_X:float,
                           camera_viewpoint_angle_Y:float,
                           camera_viewpoint_angle_Z:float,
                           configuration_offset_X:float,
                           configuration_offset_Y:float,
                           configuration_offset_Z:float,
                           ):
    """
    Sets common settings for non-sequential visualization. Meant to be called by functions: 'func:'`Visualization_NSC_3DViewer` and :func:`Visualization_NSC_ShadedModel`

    :param myLayout: The layout object for rendering.
    :type myLayout: ZOSAPI_Tools_ILayouts
    :param save_image: If should save the image
    :type save_image: bool
    :param saved_image_location: Image save location
    :type saved_image_location: str
    :param output_pixel_width: Image width in pixels
    :type output_pixel_width: int
    :param output_pixel_height: Image height in pixels
    :type output_pixel_height: int
    :param ray_trace_options: Ray tracing options for render.
    :type ray_trace_options: str
    :param color_rays_by_NSC_options: Color scheme for render.
    :type color_rays_by_NSC_options: str
    :param surface_line_thickness: Line thickness for the surfaces
    :type surface_line_thickness: str
    :param rays_line_thickness: Line thickness for the rays.
    :type rays_line_thickness: str
    :param camera_viewpoint_angle_X: X view angle of render
    :type camera_viewpoint_angle_X: float
    :param camera_viewpoint_angle_Y: Y view angle of render
    :type camera_viewpoint_angle_Y: float
    :param camera_viewpoint_angle_Z: Z view angle of render
    :type camera_viewpoint_angle_Z: float
    :param configuration_offset_X: X view offset of render
    :type configuration_offset_X: float
    :param configuration_offset_Y: Y view offset of render
    :type configuration_offset_Y: float
    :param configuration_offset_Z: Z view offset of render
    :type configuration_offset_Z: float

    """
    if output_pixel_width is not None:
        myLayout.OutputPixelWidth=int(output_pixel_width)
    if output_pixel_height is not None:
        myLayout.OutputPixelWidth=int(output_pixel_height)

    myLayout.SaveImageAsFile          = bool(save_image)
    myLayout.OutputFileName           = str(saved_image_location)
    myLayout.CameraViewpointAngleX    = float(camera_viewpoint_angle_X)
    myLayout.CameraViewpointAngleY    = float(camera_viewpoint_angle_Y)
    myLayout.CameraViewpointAngleZ    = float(camera_viewpoint_angle_Z)
    myLayout.ConfigurationOffsetX     = float(configuration_offset_X)
    myLayout.ConfigurationOffsetY     = float(configuration_offset_Y)
    myLayout.ConfigurationOffsetZ     = float(configuration_offset_Z)
    myLayout.RayTrace                 = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.RayTraceOptions, ray_trace_options)
    myLayout.ColorRaysBy              = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.ColorRaysByNSCOptions, color_rays_by_NSC_options)
    myLayout.SurfaceLineThickness     = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.LineThicknessOptions , surface_line_thickness)
    myLayout.RaysLineThickness        = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.LineThicknessOptions , rays_line_thickness)


def Visualization_NSC_3DViewer(self,
                               save_image             : bool=True,
                               saved_image_location   : str='3DView.png',
                               output_pixel_width       : int=3840,
                               output_pixel_height      : int=2160,
                               ray_trace_options:str='UseRays', 
                               color_rays_by_NSC_options:str='SourceNumber', 
                               camera_viewpoint_angle_X  : float=-30.0,
                               camera_viewpoint_angle_Y  : float=35.0,
                               camera_viewpoint_angle_Z  : float=45.0,
                               configuration_offset_X   : float=0.0,
                               configuration_offset_Y   : float=0.0,
                               configuration_offset_Z   : float=0.0,
                               surface_line_thickness:str='Thickest',
                               rays_line_thickness:str='Thickest'):
    """
    Make and save a 3D View of the system (https://community.zemax.com/zos-api-12/api-layout-plot-python-4731).
    This function is meant for non-sequential systems.


    :param save_image: Sets saving the image as a file, defaults to True
    :type save_image: bool, optional
    :param saved_image_location: location to where the image will be saved, defaults to '3DView.png'
    :type saved_image_location: str, optional
    :param output_pixel_width: Width of the image in pixels, defaults to 3840
    :type output_pixel_width: int, optional
    :param output_pixel_height: Height of the image in pixels, defaults to 2160
    :type output_pixel_height: int, optional
    :param ray_trace_options: Ray trace rendering setting. Options are: 'UseRays' , 'LightningTraceAvgWavelength', and 'LightningTraceTrueColor', defaults to 'UseRays'
    :type ray_trace_options: str, optional
    :param color_rays_by_NSC_options: Ray coloring scheme (for non-sequential mode). Options are: 'SourceNumber' , 'WaveNumber','ConfigNumber','Wavelength','SegmentNumber', defaults to 'SourceNumber'
    :type color_rays_by_NSC_options: str, optional
    :param camera_viewpoint_angle_X: X angle of the imaged viewpoint perspective, defaults to -30.0
    :type camera_viewpoint_angle_X: float, optional
    :param camera_viewpoint_angle_Y: Y angle of the imaged viewpoint perspective, defaults to 35.0
    :type camera_viewpoint_angle_Y: float, optional
    :param camera_viewpoint_angle_Z: Z angle of the imaged viewpoint perspective, defaults to 45.0
    :type camera_viewpoint_angle_Z: float, optional
    :param configuration_offset_X: X offset of the image, defaults to 0.0
    :type configuration_offset_X: float, optional
    :param configuration_offset_Y: Y offset of the image, defaults to 0.0
    :type configuration_offset_Y: float, optional
    :param configuration_offset_Z: Z offset of the image, defaults to 0.0
    :type configuration_offset_Z: float, optional
    :param surface_line_thickness: Thickness to apply to surface lines. Options are: "Thinnest", "Thin", "Standard", "Thick", and "Thickest", defaults to 'Thickest'
    :type surface_line_thickness: str, optional
    :param rays_line_thickness:Thickness to apply to ray lines. Options are: "Thinnest", "Thin", "Standard", "Thick", and "Thickest", defaults to 'Thickest'
    :type rays_line_thickness: str, optional

    """

    if not self.System_GetIfInNonSequentialMode():
        self.System_SetNonSequentialMode()
    myLayout = self.TheSystem.Tools.Layouts.OpenNSC3DLayoutExport()
    _Visualization_NSC_Common_(self, myLayout=myLayout,
                                    save_image=save_image,
                                    saved_image_location=saved_image_location,
                                    output_pixel_width=output_pixel_width,
                                    output_pixel_height=output_pixel_height,
                                    ray_trace_options=ray_trace_options,
                                    surface_line_thickness=surface_line_thickness,
                                    rays_line_thickness=rays_line_thickness,
                                    color_rays_by_NSC_options=color_rays_by_NSC_options,
                                    camera_viewpoint_angle_X=camera_viewpoint_angle_X,
                                    camera_viewpoint_angle_Y=camera_viewpoint_angle_Y,
                                    camera_viewpoint_angle_Z=camera_viewpoint_angle_Z,
                                    configuration_offset_X=configuration_offset_X,
                                    configuration_offset_Y=configuration_offset_Y,
                                    configuration_offset_Z=configuration_offset_Z,
                                    )
    myLayout.RunAndWaitForCompletion()
    myLayout.Close()

def Visualization_NSC_ShadedModel(self,
                               save_image             : bool=True,
                               saved_image_location   : str='ShadedModel.png',
                               output_pixel_width       : int=3840,
                               output_pixel_height      : int=2160,
                               ray_trace_options        : str='UseRays', 
                               color_rays_by_NSC_options  : str='SourceNumber', 
                               detector_pixel_color_mode  : str='DoNotColorIndividualPoints', 
                               camera_viewpoint_angle_X  : float=-30.0,
                               camera_viewpoint_angle_Y  : float=35.0,
                               camera_viewpoint_angle_Z  : float=45.0,
                               configuration_offset_X   : float=0.0,
                               configuration_offset_Y   : float=0.0,
                               configuration_offset_Z   : float=0.0,
                               surface_line_thickness   : str='Thickest', 
                               rays_line_thickness      : str='Thickest', 
                               background             : str='White', 
                               brightness             : str='50', 
                               opacity                : str='50', 
                               detector_display_mode    : str='Consider' #
                               ):
    """
    Make and save a 3D shaded model of the system (https://community.zemax.com/zos-api-12/api-layout-plot-python-4731).
    This function is meant for non-sequential systems.

    :param save_image: Sets saving the image as a file, defaults to True
    :type save_image: bool, optional
    :param saved_image_location: location to where the image will be saved, defaults to'ShadedModel.png'
    :type saved_image_location: str, optional
    :param output_pixel_width: Width of the image in pixels, defaults to 3840
    :type output_pixel_width: int, optional
    :param output_pixel_height: Height of the image in pixels, defaults to 2160
    :type output_pixel_height: int, optional
    :param ray_trace_options: Ray trace rendering setting. Options are: 'UseRays' , 'LightningTraceAvgWavelength', and 'LightningTraceTrueColor', defaults to 'UseRays'
    :type ray_trace_options: str, optional
    :param color_rays_by_NSC_options: Ray coloring scheme (for non-sequential mode). Options are: 'SourceNumber' , 'WaveNumber','ConfigNumber','Wavelength','SegmentNumber', defaults to 'SourceNumber'
    :type color_rays_by_NSC_options: str, optional
    :param detector_pixel_color_mode: Pixel color setting. Options are: 'DoNotColorIndividualPoints' , 'ByRaysOnLayout','ByLastAnalysis', defaults to 'DoNotColorIndividualPoints'
    :type detector_pixel_color_mode: str, optional
    :param camera_viewpoint_angle_X: X angle of the imaged viewpoint perspective, defaults to -30.0
    :type camera_viewpoint_angle_X: float, optional
    :param camera_viewpoint_angle_Y: Y angle of the imaged viewpoint perspective, defaults to 35.0
    :type camera_viewpoint_angle_Y: float, optional
    :param camera_viewpoint_angle_Z: Z angle of the imaged viewpoint perspective, defaults to 45.0
    :type camera_viewpoint_angle_Z: float, optional
    :param configuration_offset_X: X offset of the image, defaults to 0.0
    :type configuration_offset_X: float, optional
    :param configuration_offset_Y: Y offset of the image, defaults to 0.0
    :type configuration_offset_Y: float, optional
    :param configuration_offset_Z: Z offset of the image, defaults to 0.0
    :type configuration_offset_Z: float, optional
    :param surface_line_thickness: Thickness to apply to surface lines. Options are: "Thinnest", "Thin", "Standard", "Thick", and "Thickest", defaults to 'Thickest'
    :type surface_line_thickness: str, optional
    :param rays_line_thickness: Thickness to apply to surface lines. Options are: "Thinnest", "Thin", "Standard", "Thick", and "Thickest", defaults to 'Thickest'
    :type rays_line_thickness: str, optional
    :param background: Background color of the render. Options are "White", "Black", "Red", "Green", "Blue", "DarkGreen", "DarkBlue", "Color##" (where ## = 01 - 24), and "Gradient##" (where ## = 01-10), defaults to 'White'
    :type background: str, optional
    :param brightness: Brightness of the render. A percentage given as a string in steps of 10, defaults to '50'
    :type brightness: str, optional
    :param opacity: Opacity of the render. Options are: 'Ignore', 'Consider', 'All50Percent', defaults to 'All50Percent'
    :type opacity: str, optional
    :param detector_display_mode: Detector display mode. Options are: 'Consider ', 'GreyScaleFlux', 'InverseGreyScaleFlux', 'FalseColorFlux', 'InverseFalseColorFlux', 'GreyScaleIrradiance', 'InverseGreyScaleIrradiance', 'FalseColorIrradiance', 'InverseFalseColorIrradiance', defaults to 'Consider'
    :type detector_display_mode: str, optional

    """
    
    if not self.System_GetIfInNonSequentialMode():
        self.System_SetNonSequentialMode()
    myLayout = self.TheSystem.Tools.Layouts.OpenNSCShadedModelExport()
    _Visualization_NSC_Common_(self, myLayout=myLayout,
                                    save_image=save_image,
                                    saved_image_location=saved_image_location,
                                    output_pixel_width=output_pixel_width,
                                    output_pixel_height=output_pixel_height,
                                    ray_trace_options=ray_trace_options,
                                    surface_line_thickness=surface_line_thickness,
                                    rays_line_thickness=rays_line_thickness,
                                    color_rays_by_NSC_options=color_rays_by_NSC_options,
                                    camera_viewpoint_angle_X=camera_viewpoint_angle_X,
                                    camera_viewpoint_angle_Y=camera_viewpoint_angle_Y,
                                    camera_viewpoint_angle_Z=camera_viewpoint_angle_Z,
                                    configuration_offset_X=configuration_offset_X,
                                    configuration_offset_Y=configuration_offset_Y,
                                    configuration_offset_Z=configuration_offset_Z,
                                    )
    myLayout.DetectorPixelColorMode   = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.DetectorPixelColorOptions , detector_pixel_color_mode)
    myLayout.Background               = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.BackgroundOptions, background)
    myLayout.Brightness               = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.BrightnessOptions, brightness)
    myLayout.Opacity                  = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.OpacityOptions, opacity)
    myLayout.DetectorDisplayMode      = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.Layouts.DetectorDisplayModeOptions, detector_display_mode)
    myLayout.RunAndWaitForCompletion()
    myLayout.Close()
