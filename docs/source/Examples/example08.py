from __future__ import annotations

from pythonAPI.StandaloneApplication.PythonStandaloneApplicationLL import *

if __name__ == '__main__':
    ZemaxApp = PythonStandaloneApplicationLL()

    # Open file
    ZemaxApp.OpenFile(ZemaxApp.SamplesDir() + os.sep + r'Non-sequential\Scattering\ABg scattering surface.zmx', False)
    # Delete unnecessary object from NCE
    ZemaxApp.NCE_RemoveObject(3)
    # Add detector co-located with another general object
    ZemaxApp.NCE_InsertNewObject(3)
    ZemaxApp.NCE_ChangeObjectType(3, 'DetectorPolar')
    # Set the detector polar radial size to 20
    obj3_info = ZemaxApp.NCE_GetAllColumnDataOfObject(3)
    obj3_info['Radial Size'] = 20.0
    ZemaxApp.NCE_SetAllColumnDataOfObjectFromDict(3, obj3_info)
    # Co-locate object 3 with object 2 (here, could alternatively use Ref Object flag)
    # need to use placeholders for out parameters
    ZemaxApp.NCE_ColocateObject(in_objToChange=3, in_ReferenceObj=2, use_reference_flag=False)
    # Remove ABSORB material from object 4
    o4_info = ZemaxApp.NCE_GetAllColumnDataOfObject(4)
    o4_info['Material'] = ''
    ZemaxApp.NCE_SetAllColumnDataOfObjectFromDict(4, o4_info)
    # Do a raytrace
    ZemaxApp.NCE_RunRayTrace(ScatterNSCRays=True,
                             UsePolarization=False,
                             SplitNSCRays=False,
                             IgnoreErrors=True)

    # Don't need to do this, but as example, save the detector ray trace data in Zemax file formats and then load it again
    ZemaxApp.NCE_SaveDetectorInZemaxFormat(3, ZemaxApp.DetectorFiles()+os.sep+'e08_NSCEDetectorDataPol')
    ZemaxApp.NCE_SaveDetectorInZemaxFormat(4, ZemaxApp.DetectorFiles()+os.sep+'e08_NSCEDetectorDataRect')
    ZemaxApp.NCE_LoadDetectorInZemaxFormat(3, ZemaxApp.DetectorFiles()+os.sep+'e08_NSCEDetectorDataPol')
    ZemaxApp.NCE_LoadDetectorInZemaxFormat(4, ZemaxApp.DetectorFiles()+os.sep+'e08_NSCEDetectorDataRect')

    polarDet_xr = ZemaxApp.NCE_GetDetector_Complete(3)
    rectDet_xr = ZemaxApp.NCE_GetDetector_Complete(4)

    fig = mplot.figure(figsize=(13.5, 5.5))
    ax1 = mplot.subplot(121, projection = 'polar')
    ax2 = mplot.subplot(122)
    polarDet_xr.power.plot.pcolormesh(ax=ax1)
    rectDet_xr.power.plot.imshow(ax=ax2)
    mplot.savefig(ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e08_NSCEDetectorData_Detectors.png')

    ZemaxApp.Visualization_NSC_3DViewer(save_image=True, saved_image_location=ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e08_NSCEDetectorData_3DView.png')
    ZemaxApp.SaveZemaxFileAs(ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e08_NSCEDetectorData.zmx')

    del ZemaxApp
    ZemaxApp = None

