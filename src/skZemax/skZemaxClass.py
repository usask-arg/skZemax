from __future__ import annotations
from skZemax.skZemax_subfunctions._app import PythonStandaloneApplication

class skZemaxClass(PythonStandaloneApplication):
    def __init__(self, path=None, verbose:bool=True):

        """
        This class provides encapsulation and ease-of-use to the standard Zemax API calls.

        To use this class (or the Zemax API in general), the user may find it helpful to have some familiarity with the ZOS-API. 
        The beast place for documentation is to open Zemax and click on 'Help->ZOS-API Syntax Help' and 'Help->Help PDF'.

        Args:
            path (_type_, optional): Path to the installed version of OpticStudio. Defaults to None (automatically find).
            verbose (bool, optional): _description_. Defaults to True.
        """
        super(skZemaxClass, self).__init__(path=path)
        self._verbose = verbose
    from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import _CheckIfStringValidInDir_, _convert_raw_input_worker_, _SetAttrByStringIfValid_, __LowLevelZemaxStringCheck__
    from skZemax.skZemax_subfunctions._analyses_functions import Analyses_FFTMTF, Analyses_GetNamesOfAllAnalyses, Analyses_ReportSurfacePrescription, Analyses_ReportSystemPrescription, \
        Analyses_RunAnalysesAndGetResults, _Analyses_GetZOSObjectAndSettings_, _Analysis_SetZOSObjectSettingsByBinaryAlteration_, _Analysis_SetZOSObjectSettingsByDict_
    from skZemax.skZemax_subfunctions._analyses_plotting_functions import AnalysesPlotting_FFTMTF, AnalysesPlotting_LinePlotByField
    from skZemax.skZemax_subfunctions._CAD_functions import CAD_ExportSequentialCadSTPFileAs
    from skZemax.skZemax_subfunctions._field_functions import _convert_raw_field_input_, Field_DeleteField, Field_GetField, Fields_AddField, Fields_GetNumberOfFields
    from skZemax.skZemax_subfunctions._LDE_functions import LDE_AddNewSurface, LDE_ChangeApertureToCircular, LDE_ChangeApertureToCircularObscuration, LDE_ChangeApertureToFloating, \
        LDE_ChangeApertureToRectangular, LDE_ChangeSurfaceType, LDE_CheckIfSurfaceIsStop, LDE_CopyAndInsertSurfacesFromFile, LDE_GetAllColumnDataOfSurface, LDE_GetApertureTypeSettings,  \
        LDE_GetNamesOfAllApertureTypes, LDE_GetNamesOfAllSurfaceTypes, LDE_GetNumberOfSurfaces, LDE_GetSurface, LDE_GetSurfaceColumnEnum, LDE_InsertNewSurface, LDE_RemoveSurface, \
        LDE_SetAllColumnDataOfSurfaceFromDict, LDE_SetSurfaceAsStop, LDE_SetTiltDecenterAfterSurfaceMode, LDE_SetTiltDecenterOfSurface, _LDE_GetSurfaceCalls_, _LDE_GetSurfaceColumns_, _convert_raw_surface_input_
    from skZemax.skZemax_subfunctions._MCE_functions import MCE_AddConfig, MCE_AddConfigOperand, MCE_DeleteConfig, MCE_DeleteConfigOperand, MCE_GetConfigOperand, MCE_GetCurrentConfig, MCE_GetCurrentNumOperands, \
        MCE_GetNumberOfConfigs, MCE_InsertConfig, MCE_InsertConfigOperand, MCE_MakeAllSingleConfig, MCE_SetActiveConfig, MCE_SetOperand, _convert_raw_MCEOper_input_
    from skZemax.skZemax_subfunctions._MFE_functions import MFE_AddNewOperand, MFE_GetNumberOfOperands, MFE_GetOperand, MFE_GetOperandValues, MFE_InsertNewOperand, MFE_SetOperand, _convert_raw_operand_input_
    from skZemax.skZemax_subfunctions._NCE_detector_functions import NCE_GetDetectorComplete, NCE_GetDetectorLocations, NCE_LoadDetectorInZemaxFormat, NCE_SaveDetectorInZemaxFormat, _detector_file_name_checker_, \
        _NCE_CheckDetector_GetInfo_, _NCE_GetDetector_InfoAndImage_Coherent_, _NCE_GetDetector_InfoAndImage_Incoherent_, _NCE_GetDetector_InfoAndImage_Polar_, _NCE_GetPolDet_Complete_, _NCE_GetRectDet_Complete_
    from skZemax.skZemax_subfunctions._NCE_functions import NCE_RunRayTrace, NCE_AddNewObject, NCE_ChangeObjectType, NCE_ColocateObject, NCE_GetAllColumnDataOfObject, NCE_GetNumberOfObjects, NCE_GetObject, \
        NCE_GetObjectColumnEnum, NCE_GetObjectRotationAndPositionMatrices, NCE_InsertNewObject, NCE_ReadZDRFile, NCE_RemoveObject, NCE_SetAllColumnDataOfObjectFromDict, _convert_raw_obj_input_, _NCE_GetObjectCellCalls_, _NCE_GetObjectColumns_
    from skZemax.skZemax_subfunctions._rayaiming_functions import RayAiming_GetNamesOfAllAimingMethods, RayAiming_GetNamesOfAllAimingProperties, RayAiming_SetAimingMethod, RayAiming_SetAimingProperty
    from skZemax.skZemax_subfunctions._solver_functions import Solver_GetNamesOfAllSolveTypes, Solver_HammerOptimization, Solver_LDEMakeSurfacePropertyFixed, Solver_LDEMakeSurfacePropertyVariable, \
        Solver_LDESurfaceProperty_ForValue, Solver_LocalOptimization, Solver_MCEMakeConfigOp_ForValue, Solver_MCEMakeConfigOpVariable, Solver_QuickFocus_SpotSize
    from skZemax.skZemax_subfunctions._system_functions import System_GetNamesOfAllMaterialCatalogs, System_AddMaterialCatalog, System_GetIfInNonSequentialMode, System_GetIfInSequentialMode, \
        System_GetMode, System_GetNamesOfAllApertureSettings, System_Lockdown, System_SetApertureProperty, System_SetGlobalCoordinateReferenceSurface, System_SetNonSequentialMode, System_SetSequentialMode, \
            System_ConvertSequentialToNonSequential
    from skZemax.skZemax_subfunctions._utility_functions import Utilities_skZemaxExampleDir, Utilities_ConfigFilesDir, Utilities_DetectorFilesDir, Utilities_OpenZemaxFile, Utilities_MakeNewZemaxFile, \
        Utilities_SaveZemaxFile, Utilities_SaveZemaxFileAs, Utilities_GetAllSystemUnits, Utilities_AnalysesFilesDir, Utilities_MainProgramDir, Utilities_ZemaxInstallationExampleDir, \
            Utilities_ZemaxInstallationCADObjectDir, Utilities_ZemaxInstallationCoatingDir, Utilities_ZemaxInstallationImageDir, Utilities_ZemaxInstallationMaterialDir, Utilities_ZemaxInstallationPolygonObjectDir, \
                Utilities_ZemaxInstallationScatterDir
    from skZemax.skZemax_subfunctions._visualization_functions import Visualization_NSC_3DViewer, Visualization_NSC_ShadedModel, Visualization_SEQ_2DCrossSection, Visualization_SEQ_3DViewer, \
        Visualization_SEQ_ShadedModel, _Visualization_NSC_Common_, _Visualization_SEQ_Common_
    from skZemax.skZemax_subfunctions._wavelength_functions import Wavelength_SelectWavelengthPreset, Wavelength_AddWavelength, Wavelength_GetNamesOfAllPresets, Wavelength_GetNumberOfWavelengths, \
        Wavelength_GetWavelength, Wavelength_RemoveWavelength, _convert_raw_wavelength_input_
    
if __name__ == '__main__':
    import os
    skZemax = skZemaxClass()
    # skZemax.Utilities_OpenZemaxFile(skZemax.SamplesDir() + os.sep + r'Non-sequential\Miscellaneous\Digital_projector_flys_eye_homogenizer.zmx', False)
    skZemax.Utilities_OpenZemaxFile(skZemax.Utilities_skZemaxExampleDir() + os.sep + r'e01_new_file_and_quickfocus.zmx', False)
    skZemax.Analyses_ReportSurfacePrescription(2)
