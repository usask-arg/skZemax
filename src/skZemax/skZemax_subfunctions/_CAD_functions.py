from skZemax.skZemax_subfunctions._c_print import c_print as cp

def CAD_ExportSequentialCadSTPFileAs(self, 
                                     in_file_path:str,
                                     first_surface:int=1,
                                     last_surface:int=None,
                                     number_of_rays:int=7,
                                     ray_pattern:str='XYFan',
                                     delete_vignetted:bool=False,
                                     configuration_number:int=None,
                                     wavelength_num:int=None,
                                     field_num:int=None,
                                     export_dummy:bool=False,
                                     solid_surfaces:bool=True,
                                     )->None:
    """
    Exports a cad file of the current optical system.

    :param in_file_path: File path to save the CAD file to.
    :type in_file_path: str
    :param first_surface: First surface to include in the CAD, defaults to 1
    :type first_surface: int, optional
    :param last_surface: Last surface to include in the CAD, defaults to None
    :type last_surface: int, optional
    :param number_of_rays: Number of rays to trace in the CAD, defaults to 7
    :type number_of_rays: int, optional
    :param ray_pattern: Ray pattern to export, defaults to 'XYFan'
    :type ray_pattern: str, optional
    :param delete_vignetted: If should remove vignetted rays from the CAD, defaults to False
    :type delete_vignetted: bool, optional
    :param configuration_number: Configuration to export in the CAD, defaults to None
    :type configuration_number: int, optional
    :param wavelength_num:  Wavelength index to use in CAD, defaults to None
    :type wavelength_num: int, optional
    :param field_num: Field index to use in CAD, defaults to None
    :type field_num: int, optional
    :param export_dummy: If you want to export dummy surfaces, defaults to False
    :type export_dummy: bool, optional
    :param solid_surfaces: If you want to export surfaces as solids in the CAD file, defaults to True
    :type solid_surfaces: bool, optional
    """

    if self.System_GetIfInSequentialMode():
        in_file_path = in_file_path.split('.')[0] + ".STP"
        if last_surface is None:
            last_surface = self.LDE_GetNumberOfSurfaces()-1
        CadTool                       = self.TheSystem.Tools.OpenExportCAD()
        CadTool.FirstSurface          = int(first_surface)
        CadTool.LastSurface           = int(last_surface)
        CadTool.NumberOfRays          = int(number_of_rays)
        CadTool.RayPattern            = self._CheckIfStringValidInDir_(self.ZOSAPI.Tools.General.RayPatternType, ray_pattern)
        CadTool.DeleteVignetted       = bool(delete_vignetted)
        CadTool.ExportDummySurfaces   = bool(export_dummy)
        CadTool.SurfacesAsSolids      = bool(solid_surfaces)
        if configuration_number is None:
             CadTool.SetCurrentConfiguration()
        else:
            CadTool.Configuration = int(configuration_number)
        if wavelength_num is None:
            CadTool.SetWavelengthAll()
        else:
            CadTool.Wavelength = int(wavelength_num)
        if field_num is None:
            CadTool.SetFieldAll()
        else:
            CadTool.Field = int(field_num)
        CadTool.OutputFileName = in_file_path
        if self._verbose: cp('!@lg!@ExportSequentialCadSTPFileAs :: Exporting Zemax CAD File As [!@lm!@%s!@lg!@].'%in_file_path)
        CadTool.RunAndWaitForCompletion()
        CadTool.Close()
