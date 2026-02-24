from __future__ import annotations

import inspect
import os

import clr

from skZemax.skZemax_subfunctions._app import PythonStandaloneApplication


class skZemaxClass(PythonStandaloneApplication):
    def __init__(self, path=None, verbose: bool = True):
        """
        This class provides encapsulation and ease-of-use to the standard Zemax API calls.

        To use this class (or the Zemax API in general), the user may find it helpful to have some familiarity with the ZOS-API.
        The beast place for documentation is to open Zemax and click on 'Help->ZOS-API Syntax Help' and 'Help->Help PDF'.

        Args:
            path (_type_, optional): Path to the installed version of OpticStudio. Defaults to None (automatically find).
            verbose (bool, optional): _description_. Defaults to True.
        """
        super().__init__(path=path)
        self._verbose = verbose
        # To make implementation of raytracing faster, skZemax uses the .dll the 'Help->Help PDF' directs you to:
        # https://optics.ansys.com/hc/en-us/articles/42661765866899-Batch-Processing-of-Ray-Trace-Data-using-ZOS-API-in-MATLAB-or-Python
        # Importing it here
        clr.AddReference(
            os.path.abspath(
                os.sep.join(
                    os.path.abspath(inspect.getfile(skZemaxClass)).split(os.sep)[0:-1]
                )
                + os.sep
                + "ZemaxRaytraceSupplement"
                + os.sep
                + "RayTrace.dll"
            )
        )
        import BatchRayTrace

        self.BatchRayTrace = BatchRayTrace

    # Adding skZemax_subfunctions to skZemaxClass
    from skZemax.skZemax_subfunctions._analyses_functions import (
        Analyses_ExtractSectionOfTextFile,
        Analyses_FFTMTF,
        Analyses_Footprint,
        Analyses_GetNamesOfAllAnalyses,
        Analyses_ReportSurfacePrescription,
        Analyses_ReportSystemPrescription,
        Analyses_RunAnalysesAndGetResults,
        _Analyses_GetZOSObjectAndSettings_,
        _Analysis_SetZOSObjectSettingsByBinaryAlteration_,
        _Analysis_SetZOSObjectSettingsByDict_,
    )
    from skZemax.skZemax_subfunctions._analyses_plotting_functions import (
        AnalysesPlotting_FFTMTF,
        AnalysesPlotting_LinePlotByField,
        AnalysisPlotting_Footprint,
    )
    from skZemax.skZemax_subfunctions._CAD_functions import (
        CAD_ExportSequentialCadSTPFileAs,
    )
    from skZemax.skZemax_subfunctions._field_functions import (
        Field_ClearVignettingFactors,
        Field_DeleteField,
        Field_GetAllDataOfField,
        Field_GetField,
        Field_GetFieldType,
        Field_GetNormalization,
        Field_SetAllDataOfFieldFromDict,
        Field_SetFieldType,
        Field_SetNormalization,
        Field_SetVignettingFactors,
        Fields_AddField,
        Fields_GetNumberOfFields,
        _convert_raw_field_input_,
    )
    from skZemax.skZemax_subfunctions._LDE_functions import (
        LDE_AddNewSurface,
        LDE_BuildRayTraceNormalizedUnpolarizedRays,
        LDE_ChangeApertureToCircular,
        LDE_ChangeApertureToCircularObscuration,
        LDE_ChangeApertureToFloating,
        LDE_ChangeApertureToRectangular,
        LDE_ChangeSurfaceType,
        LDE_CheckIfSurfaceIsStop,
        LDE_CopyAndInsertSurfacesFromFile,
        LDE_GetAllColumnDataOfSurface,
        LDE_GetApertureAsCircularObscurationType,
        LDE_GetApertureAsCircularType,
        LDE_GetApertureAsRectangularType,
        LDE_GetApertureTypeSettings,
        LDE_GetNamesOfAllApertureTypes,
        LDE_GetNamesOfAllSurfaceTypes,
        LDE_GetNumberOfSurfaces,
        LDE_GetObjectRotationAndPositionMatrices,
        LDE_GetStopSurface,
        LDE_GetSurface,
        LDE_GetSurfaceApertureType,
        LDE_GetSurfaceColumnEnum,
        LDE_InsertNewSurface,
        LDE_RemoveSurface,
        LDE_RunRayTrace,
        LDE_SetAllColumnDataOfSurfaceFromDict,
        LDE_SetSurfaceAsStop,
        LDE_SetTiltDecenterAfterSurfaceMode,
        LDE_SetTiltDecenterOfSurface,
        _convert_raw_surface_input_,
        _LDE_GetSurfaceCalls_,
        _LDE_GetSurfaceColumns_,
        _run_NormUnPol_raytrace_,
    )
    from skZemax.skZemax_subfunctions._MCE_functions import (
        MCE_AddConfig,
        MCE_AddConfigOperand,
        MCE_DeleteConfig,
        MCE_DeleteConfigOperand,
        MCE_GetConfigOperand,
        MCE_GetCurrentConfig,
        MCE_GetCurrentNumOperands,
        MCE_GetNumberOfConfigs,
        MCE_InsertConfig,
        MCE_InsertConfigOperand,
        MCE_MakeAllSingleConfig,
        MCE_SetActiveConfig,
        MCE_SetOperand,
        _convert_raw_MCEOper_input_,
    )
    from skZemax.skZemax_subfunctions._MFE_functions import (
        MFE_AddNewOperand,
        MFE_GetNumberOfOperands,
        MFE_GetOperand,
        MFE_GetOperandValues,
        MFE_InsertNewOperand,
        MFE_SetOperand,
        _convert_raw_operand_input_,
    )
    from skZemax.skZemax_subfunctions._NCE_detector_functions import (
        NCE_GetDetectorComplete,
        NCE_GetDetectorLocations,
        NCE_LoadDetectorInZemaxFormat,
        NCE_SaveDetectorInZemaxFormat,
        _detector_file_name_checker_,
        _NCE_CheckDetector_GetInfo_,
        _NCE_GetDetector_InfoAndImage_Coherent_,
        _NCE_GetDetector_InfoAndImage_Incoherent_,
        _NCE_GetDetector_InfoAndImage_Polar_,
        _NCE_GetPolDet_Complete_,
        _NCE_GetRectDet_Complete_,
    )
    from skZemax.skZemax_subfunctions._NCE_functions import (
        NCE_AddNewObject,
        NCE_ChangeObjectType,
        NCE_ColocateObject,
        NCE_GetAllColumnDataOfObject,
        NCE_GetNumberOfObjects,
        NCE_GetObject,
        NCE_GetObjectColumnEnum,
        NCE_GetObjectRotationAndPositionMatrices,
        NCE_InsertNewObject,
        NCE_ReadZDRFile,
        NCE_RemoveObject,
        NCE_RunRayTrace,
        NCE_SetAllColumnDataOfObjectFromDict,
        _convert_raw_obj_input_,
        _NCE_GetObjectCellCalls_,
        _NCE_GetObjectColumns_,
    )
    from skZemax.skZemax_subfunctions._rayaiming_functions import (
        RayAiming_GetNamesOfAllAimingMethods,
        RayAiming_GetNamesOfAllAimingProperties,
        RayAiming_SetAimingMethod,
        RayAiming_SetAimingProperty,
    )
    from skZemax.skZemax_subfunctions._solver_functions import (
        Solver_GetNamesOfAllSolveTypes,
        Solver_HammerOptimization,
        Solver_LDEMakeSurfacePropertyFixed,
        Solver_LDEMakeSurfacePropertyVariable,
        Solver_LDESurfaceProperty_ForValue,
        Solver_LocalOptimization,
        Solver_MCEMakeConfigOp_ForValue,
        Solver_MCEMakeConfigOpVariable,
        Solver_QuickFocus_SpotSize,
    )
    from skZemax.skZemax_subfunctions._system_functions import (
        System_AddMaterialCatalog,
        System_ConvertSequentialToNonSequential,
        System_GetIfInNonSequentialMode,
        System_GetIfInSequentialMode,
        System_GetMode,
        System_GetNamesOfAllApertureSettings,
        System_GetNamesOfAllMaterialCatalogs,
        System_Lockdown,
        System_SetAdvancedProperty,
        System_SetApertureProperty,
        System_SetEnvironmentProperty,
        System_SetGlobalCoordinateReferenceSurface,
        System_SetNonSequentialMode,
        System_SetPolarizationProperty,
        System_SetSequentialMode,
    )
    from skZemax.skZemax_subfunctions._utility_functions import (
        Utilities_AnalysesFilesDir,
        Utilities_ConfigFilesDir,
        Utilities_DetectorFilesDir,
        Utilities_GetAllSystemUnits,
        Utilities_MainProgramDir,
        Utilities_MakeNewZemaxFile,
        Utilities_OpenZemaxFile,
        Utilities_SaveZemaxFile,
        Utilities_SaveZemaxFileAs,
        Utilities_skZemaxExampleDir,
        Utilities_ZemaxInstallationCADObjectDir,
        Utilities_ZemaxInstallationCoatingDir,
        Utilities_ZemaxInstallationExampleDir,
        Utilities_ZemaxInstallationImageDir,
        Utilities_ZemaxInstallationMaterialDir,
        Utilities_ZemaxInstallationPolygonObjectDir,
        Utilities_ZemaxInstallationScatterDir,
    )
    from skZemax.skZemax_subfunctions._visualization_functions import (
        Visualization_NSC_3DViewer,
        Visualization_NSC_ShadedModel,
        Visualization_SEQ_2DCrossSection,
        Visualization_SEQ_3DViewer,
        Visualization_SEQ_ShadedModel,
        _Visualization_NSC_Common_,
        _Visualization_SEQ_Common_,
    )
    from skZemax.skZemax_subfunctions._wavelength_functions import (
        Wavelength_AddWavelength,
        Wavelength_GetNamesOfAllPresets,
        Wavelength_GetNumberOfWavelengths,
        Wavelength_GetPrimaryWavelength,
        Wavelength_GetWavelength,
        Wavelength_RemoveWavelength,
        Wavelength_SelectWavelengthPreset,
        Wavelength_SetPrimaryWavelength,
        _convert_raw_wavelength_input_,
    )
    from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import (
        __LowLevelZemaxStringCheck__,
        _CheckIfStringValidInDir_,
        _convert_raw_input_worker_,
        _ctype_to_numpy_,
        _SetAttrByStringIfValid_,
    )


if __name__ == "__main__":
    import numpy as np

    skZemax = skZemaxClass()
    # skZemax.Utilities_OpenZemaxFile(skZemax.SamplesDir() + os.sep + r'Non-sequential\Miscellaneous\Digital_projector_flys_eye_homogenizer.zmx', False)
    # skZemax.Utilities_OpenZemaxFile(skZemax.Utilities_skZemaxExampleDir() + os.sep + r'e01_new_file_and_quickfocus.zmx', False)
    skZemax.Utilities_MainProgramDir()
    skZemax.Utilities_OpenZemaxFile(
        r"E:\_OfficerRepositories\ZemaxRepos\skzemax_show\src\skZemax_SHOW\skSHS_end_to_end_files\BVI\Front_End\SHOW_FrontEnd_V15_stockLenses_2025_02_02.zmx",
        False,
    )
    ray_trace = skZemax.LDE_RunRayTrace(
        ray_trace_rays=skZemax.LDE_BuildRayTraceNormalizedUnpolarizedRays(
            Hx=np.array([0]), Hy=np.array([0]), Px=np.array([0.0]), Py=np.array([0.0]), wavelengths=None, should_meshgrid=False,
        )
    )
    # ray_trace = skZemax.LDE_RunRayTrace(skZemax.LDE_BuildRayTraceNormalizedUnpolarizedRays(Hx=np.array([0]),
    #                                            Hy=np.array([0]),
    #                                            Px=np.cos(np.linspace(0, 2 * np.pi, 150, endpoint=False)),
    #                                            Py=np.sin(np.linspace(0, 2 * np.pi, 150, endpoint=False)), do_all_surfaces_to_ending=False))
    ray_trace.sel(surf=30).reset_coords("wavelengths_idx", drop=True).plot.scatter(
        x="X", y="Y"
    )
    import matplotlib.pyplot as plt
    plt.show()
    # Close
    del skZemax
    skZemax = None
