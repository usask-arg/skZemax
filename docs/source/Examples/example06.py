from __future__ import annotations

from pythonAPI.StandaloneApplication.PythonStandaloneApplicationLL import *

if __name__ == '__main__':
    ZemaxApp = PythonStandaloneApplicationLL()
    # Open file
    ZemaxApp.MakeNewZemaxFile(ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e06_nsc_phase.zmx')
    ZemaxApp.System_SetNonSequentialMode()
    o1    = ZemaxApp.NCE_GetObject(1)
    o2    = ZemaxApp.NCE_InsertNewObject(2)
    ZemaxApp.NCE_ChangeObjectType(o1, 'SourcePoint')
    ZemaxApp.NCE_ChangeObjectType(o2, 'DetectorRectangle')
    o1info = ZemaxApp.NCE_GetAllColumnDataOfObject(o1)
    o2info = ZemaxApp.NCE_GetAllColumnDataOfObject(o2)
    # Adjust object settings
    o1info['# Analysis Rays'] = 1e6
    o1info['# Layout Rays'] = 10
    o1info['Cone Angle']    = 2.5
    o2info['Z Position']    = 1
    o2info['X Half Width']  = 0.1
    o2info['Y Half Width']  = 0.1
    o2info['# X Pixels'] = 100
    o2info['# Y Pixels'] = 100
    # There is a lot to this setting, so read the documentation, but in general:
    # If all the incoherent power from one or more sources falls on the same detector, then the Normalize Coherent Power switch should be checked on
    o2.TypeData.NormalizeCoherentPower = True
    # Apply settings
    ZemaxApp.NCE_SetAllColumnDataOfObjectFromDict(o1, o1info)
    ZemaxApp.NCE_SetAllColumnDataOfObjectFromDict(o2, o2info)
    # Run Raytrace
    ZemaxApp.NCE_RunRayTrace(
        SplitNSCRays=False,
        ScatterNSCRays=True,
        UsePolarization=False,
        IgnoreErrors=True,
        SaveRays=False,
        )
    # Get detector Data
    detector_xr = ZemaxApp.NCE_GetDetector_Complete(2)
    # Save and close
    ZemaxApp.SaveZemaxFile()
    ZemaxApp.Visualization_NSC_ShadedModel(save_image=True, saved_image_location=ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e06_nsc_phase_Shaded.png')

    mplot.subplot(2, 5, 1)
    detector_xr.power.plot.imshow()
    mplot.subplot(2, 5, 2)
    detector_xr.incoherent_irradiance.plot.imshow()
    mplot.subplot(2, 5, 3)
    detector_xr.incoherent_radiant_intensity.plot.imshow()
    mplot.subplot(2, 5, 4)
    detector_xr.incoherent_radiance_position.swap_dims({'y_pixel': 'y_distance', 'x_pixel': 'x_distance'}).plot.imshow()
    mplot.subplot(2, 5, 5)
    detector_xr.incoherent_radiance_angle.plot.imshow()
    mplot.subplot(2, 5, 6)
    detector_xr.coherent_irradiance.plot.imshow()
    mplot.subplot(2, 5, 7)
    detector_xr.coherent_phase.plot.imshow()
    mplot.subplot(2, 5, 8)
    detector_xr.coherent_real.plot.imshow()
    mplot.subplot(2, 5, 9)
    detector_xr.coherent_imag.plot.imshow()
    mplot.subplot(2, 5, 10)
    detector_xr.coherent_power.plot.imshow()

    mplot.gcf().set_size_inches(16, 5)
    mplot.tight_layout()
    mplot.draw()
    mplot.savefig(ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e06_nsc_phase_Detector.png', dpi = 600)

    del ZemaxApp
    ZemaxApp = None




