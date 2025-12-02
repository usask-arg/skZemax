from __future__ import annotations

from pythonAPI.StandaloneApplication.PythonStandaloneApplicationLL import *

if __name__ == '__main__':
    ZemaxApp = PythonStandaloneApplicationLL()
     # Open file
    ZemaxApp.OpenFile(ZemaxApp.SamplesDir() + os.sep + r'Sequential\Objectives\Cooke 40 degree field.zmx', False)
    fftmtf_X, fftmtf_Y = ZemaxApp.Analyses_getFFTMTF()
    ZemaxApp.AnalysesPlotting_FFTMTF(fftmtf_X, fftmtf_Y, title='MTF of: Cooke 40 degree field.zmx')
    mplot.savefig(ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e04_FFTMTF.png')
    ZemaxApp.Visualization_SEQ_2DCrossSection(save_image=True, saved_image_location=ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e04_FFTMTF_2DCrossSection.png')
    ZemaxApp.SaveZemaxFileAs(ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e04_FFTMTF.zmx')
    del ZemaxApp
    ZemaxApp = None
