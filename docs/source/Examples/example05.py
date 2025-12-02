from __future__ import annotations

from pythonAPI.StandaloneApplication.PythonStandaloneApplicationLL import *

if __name__ == '__main__':
    ZemaxApp = PythonStandaloneApplicationLL()
    # Open file
    ZemaxApp.OpenZemaxFile(ZemaxApp.ExampleZemaxFilesLL() + os.sep +r'e02_SimpleRayTrace.zmx')

    Obj1 = ZemaxApp.NCE_GetObject(1)
    Obj1Info = ZemaxApp.NCE_GetAllColumnDataOfObject(Obj1)
    Obj1Info['# Analysis Rays'] = 10
    ZemaxApp.NCE_SetAllColumnDataOfObjectFromDict(Obj1, Obj1Info)
    ZemaxApp.NCE_RunRayTrace(SaveRays=True, SaveFileName='e05_SimpleRayTrace.ZDR')
    ZDR_dict = ZemaxApp.NCE_ReadZDRFile(ZemaxApp.ExampleZemaxFilesLL() + os.sep + 'e05_SimpleRayTrace.ZRD', should_print=False)
    del ZemaxApp
    ZemaxApp = None

