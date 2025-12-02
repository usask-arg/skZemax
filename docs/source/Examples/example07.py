from __future__ import annotations

from pythonAPI.StandaloneApplication.PythonStandaloneApplicationLL import *

if __name__ == '__main__':
    ZemaxApp = PythonStandaloneApplicationLL()
    # Open file
    ZemaxApp.OpenFile(ZemaxApp.SamplesDir() + os.sep + r'Sequential\Objectives\Cooke 40 degree field.zmx', False)
    # Lockdown the sample sheet to do new things with it...
    ZemaxApp.System_Lockdown(usePrecisionRounding=True, decimalPrecision=2)
    # recreate the functionality of the tilt/decenter elements tool
    # apply coordinate breaks around the 2nd lens element (surf 3/4)
    ZemaxApp.LDE_ChangeSurfaceType(ZemaxApp.LDE_InsertNewSurface(3), 'CoordinateBreak')
    ZemaxApp.LDE_ChangeSurfaceType(ZemaxApp.LDE_InsertNewSurface(6), 'CoordinateBreak')
    ZemaxApp.LDE_GetSurface(3).Comment='CB1'
    ZemaxApp.LDE_GetSurface(6).Comment='CB2'
    # insert a dummy surface after 2nd CB
    ZemaxApp.LDE_InsertNewSurface(7).Thickness = ZemaxApp.LDE_GetSurface(5).Thickness # the dummy carries the original thickness
    ZemaxApp.LDE_GetSurface(7).Comment='Dummy'
    # we're going to play with the STOP surface position, so let's put STOP on surf 1
    ZemaxApp.LDE_SetSurfaceAsStop(1)
    # create position solve
    ZemaxApp.Solver_LDESurfaceProperty_ForValue(in_surface=5,
                                             property="thickness", solve_type='position', params={'FromSurface': 3,
                                                                                             'Length': 0})
    # create pickup solve
    ZemaxApp.Solver_LDESurfaceProperty_ForValue(in_surface=6,
                                             property="thickness", solve_type='surfacepickup', params={'Surface': 5,
                                                                                             'ScaleFactor': -1,
                                                                                             'Offset':0,
                                                                                             'Column': ZemaxApp.LDE_GetSurfaceColumnEnum('Thickness')})
    # set pickup solves for coordinate break tilt/decenter parameter cells
    # these parameters are columns 12-16 in the Lens Data Editor (parameters 1-5)
    #
    # Note, I convert names into parameter index with ZemaxApp.LDE_GetSurfaceColumnEnum().
    surf6 = ZemaxApp.LDE_GetSurface(6)
    surf3 = ZemaxApp.LDE_GetSurface(3)
    for prop in ["Decenter X", "Decenter Y", "Par3", "Par4", "Par5"]: # Switching to Par# notation for example, but can be "Tilt About X/Y/Z" instead.
        ZemaxApp.Solver_LDESurfaceProperty_ForValue(in_surface=surf6,
                                                property=prop, solve_type='surfacepickup', params={'Surface': 3,
                                                                                                'ScaleFactor': -1,
                                                                                                'Offset':0,
                                                                                                'Column': ZemaxApp.LDE_GetSurfaceColumnEnum(prop, surf3)}) # Don't need surf3 input for 'Par#' names
    # assign random tilt/decenter values (the pickups above should undo the tilt/decenter)
    for par in ['Par1', 'Par2', 'Par3', 'Par4', 'Par5']:
        surf3.GetCellAt(int(ZemaxApp.LDE_GetSurfaceColumnEnum(par))).DoubleValue = np.random.uniform(-0.1, .01)
    # also, set the 'order' flag for CB#2
    surf6.GetCellAt(int(ZemaxApp.LDE_GetSurfaceColumnEnum('Order', surf6))).IntegerValue = 1

    # We now get the global rotation matrix at surface 5.
    # This is done through the operand 'GLCR' which  only uses two input parameters:
    #   the surface number, and the rotation matrix entry number.
    # The API call to get the operand needs 8 inputs, so we will use zeros as the dummies that don't matter.
    # The 3 x 3 R matrix has 9 components. If Data is 1, GLCR returns R[1][1], if Data is 2, GLCR returns R[1][2], etc... through Data = 9 returning R[3][3].
    GLCR_params = np.array([[5, x+1, 0, 0, 0, 0, 0, 0] for x in range(9)]) # Index 'x' is for element of rotation matrix
    R = ZemaxApp.MFE_GetOperandValues('GLCR', GLCR_params)
    R = R.reshape(3,3)

    ZemaxApp.Visualization_SEQ_ShadedModel(save_image=True, saved_image_location=ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e07_TiltDecenterAndMFOperand_Shaded.png')
    ZemaxApp.SaveZemaxFileAs(ZemaxApp.ExampleZemaxFilesLL() + os.sep + r'e07_TiltDecenterAndMFOperand.zmx')
    del ZemaxApp
    ZemaxApp = None

