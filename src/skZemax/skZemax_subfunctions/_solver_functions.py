from skZemax.skZemax_subfunctions._ZOSAPI_interface_functions import __LowLevelZemaxStringCheck__
from typing import Union
import time
from skZemax.skZemax_subfunctions._c_print import c_print as cp

type ZOSAPI_Editors_LDE_ILDERow = object #<- ZOSAPI.Editors.LDE.ILDERow # The actual module is referenced by the base PythonStandaloneApplication class.
type ZOSAPI_Editors_MCE_IMCERow = object #<- ZOSAPI.Editors.MCE.IMCERow # The actual module is referenced by the base PythonStandaloneApplication class.

######################################################
# Optimization Functions
######################################################
def Solver_QuickFocus_SpotSize(self)->None:
    """
    Invokes the Zemax QuickFocus to optimize for the radial spot size.
    """
    quickFocus = self.TheSystem.Tools.OpenQuickFocus()
    quickFocus.Criterion =  self.ZOSAPI.Tools.General.QuickFocusCriterion.SpotSizeRadial
    quickFocus.UseCentroid = True
    quickFocus.RunAndWaitForCompletion()
    quickFocus.Close()

def Solver_LocalOptimization(self, use_DampedLeastSquares:bool=True, numCores:int=None)->None:
    """
    Runs local optimization based on the merit functions.
    
    This function assumes the merits are already set up.

    :param use_DampedLeastSquares: If should use DLS - which is recommended. If false will use Othogonal Descent (OD), 
                                   which for systems with inherently noisy merit functions, such as non-sequential systems.  
                                   OD will usually outperform DLS. defaults to True
    :type use_DampedLeastSquares: bool, optional
    :param numCores: Number of computer cores to use, defaults to None (will use all)
    :type numCores: int, optional
    """
    if numCores is None:
        import multiprocessing
        numCores = multiprocessing.cpu_count()
    LocalOpt = self.TheSystem.Tools.OpenLocalOptimization()
    if use_DampedLeastSquares:
        LocalOpt.Algorithm = self.ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares
    else:
        LocalOpt.Algorithm = self.ZOSAPI.Tools.Optimization.OptimizationAlgorithm.OrthogonalDescent
    LocalOpt.Cycles = self.ZOSAPI.Tools.Optimization.OptimizationCycles.Automatic
    LocalOpt.NumberOfCores = int(numCores)
    if self._verbose: cp('!@lg!@Solver_LocalOptimization :: Running Local Optimization ...')
    LocalOpt.RunAndWaitForCompletion()
    LocalOpt.Close()
    if self._verbose: cp('!@lg!@Solver_LocalOptimization :: Done Local Optimization')

def Solver_HammerOptimization(self, secondsRunning: float=10.0):
    """
    This feature automates the repetitive optimization of a design to escape local minima in the merit function.

    The Hammer Optimization algorithm can also be used effectively on partially optimized designs that were not
    generated with Global Optimization.

    :param secondsRunning: The seconds to run the optimization for, defaults to 10.0
    :type secondsRunning: float, optional
    """
    HammerOpt = self.TheSystem.Tools.OpenHammerOptimization()
    if self._verbose:
        cp('!@lg!@Solver_HammerOptimization :: Running Hammer Optimization for [!@lm!@{:.2f}!@g!@] seconds ...'.format(secondsRunning))
        from alive_progress import alive_bar
        with alive_bar(manual=True) as bar:
            starttime = float(time.perf_counter())
            HammerOpt.Run()
            while HammerOpt.IsRunning:
                time.sleep(0.15)
                bar((float(time.perf_counter()) - starttime)/secondsRunning)
                if (float(time.perf_counter()) - starttime) >= secondsRunning:
                    HammerOpt.Cancel()
            bar(1)
    else:
        HammerOpt.RunAndWaitWithTimeout(secondsRunning)
        HammerOpt.Cancel()
    HammerOpt.WaitForCompletion()
    HammerOpt.Close()
    if self._verbose: cp('!@lg!@Solver_HammerOptimization :: Done Hammer Optimization.')

######################################################
# Solver Surface Settings
######################################################
def Solver_LDEMakeSurfacePropertyVariable(self, in_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], property:str):
    """
    Sets the property of the surface variable.

    :param in_surface: The surface to set - either an index or object.
    :type in_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param property: A string identifying the property to make variable - this will be one of the object's column properties (keys in dict of :func:`LDE_GetAllColumnDataOfSurface`).
    :type property: str
    """
    in_surface = self._convert_raw_surface_input_(in_surface, return_index=False)
    in_surface.GetCellAt(int(self.LDE_GetSurfaceColumnEnum(property, in_surface))).MakeSolveVariable()

def Solver_LDEMakeSurfacePropertyFixed(self, in_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], propty:str):
    """
    Sets the property of the surface to be fixed.

    :param in_surface: The surface to set - either an index or object.
    :type in_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param propty: A string identifying the property to make variable - this will be one of the object's column properties (keys in dict of :func:`LDE_GetAllColumnDataOfSurface`).
    :type propty: str
    """
    in_surface = self._convert_raw_surface_input_(in_surface, return_index=False)
    in_surface.GetCellAt(int(self.LDE_GetSurfaceColumnEnum(propty, in_surface))).MakeSolveFixed()

def Solver_GetNamesOfAllSolveTypes(self, print_to_console:bool=False, in_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]=None)->Union[list, dict[list]]:
    """
    This function builds a list of all the solve type settings in Zemax.
    This can be useful to look up what one may want to code as input to functions like :func:`Solver_LDESurfaceProperty_ForValue`.

    There are many combinations so it is recommended that a user see the Zemax decimation first (the ISolve interfaces in the ZOS-API help and the main help PDF section 2.3.1.4. Solve Types).

    If one just wants to see the solve types only, this function will run very quickly and can be called with in_surface=None.

    If in_surface is not None, then this function will look up all possible solves and the parameters which can be set for the given surface.
    This is not recommended as it may take time on the order of minutes to execute, but it is here if you can find it helpful.

    :param print_to_console: If True will print to console, defaults to False
    :type print_to_console: bool, optional
    :param in_surface: If a surface (index or object) if given, will look up all solves/parameters of the surface, defaults to None
    :type in_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], optional
    :return: If in_surface=None, then a list is returned with only the names of the solve types. If a surface is given, then the information is returned as dict of lists formatted as: dict[solve_type]['surface_property'] = [parameters]
    :rtype: Union[list, dict]
    """
    solve_types = [x for x in __LowLevelZemaxStringCheck__(self, in_obj=self.ZOSAPI.Editors.SolveType, extra_exclude_filter='_')]
    if in_surface is not None:
        # Disable verbose for the solve type search on the surface.
        saved_verbose_state = bool(self._verbose)
        self._verbose = False
        # Make the output dict
        out = dict()
        # Look up the solvers - and param configurations - for the given surface
        in_surface = self._convert_raw_surface_input_(in_surface, return_index=False)
        surf_props = [x for x in self.LDE_GetAllColumnDataOfSurface(in_surface).keys()]
        # For each surface property, find what the params you can solve for.
        # Doing a brute force search aftering making the solvers, because ZOS-API functions like GetAvailableSolveTypes() and GetNumberOfSolveTypes() seems to either not work
        # or are expected to work only after the solver has been created at least once. Maybe there is still a better way than this....
        from alive_progress import alive_bar
        bar_counts = 0
        total_bar_length = float(len(solve_types)*len(surf_props))
        cp('\n!@lg!@Solver_GetNamesOfAllSolveTypes :: Finding all solves and parameters for the given surface type ...')
        with alive_bar(manual=True) as bar:
            for solve in solve_types:
                out[solve] = dict()
                for prop in surf_props:
                    cell_solve_data = in_surface.GetCellAt(int(self.LDE_GetSurfaceColumnEnum(prop, in_surface))).CreateSolveType(self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.SolveType, solve))
                    solver_params = [x for x in __LowLevelZemaxStringCheck__(self, self._CheckIfStringValidInDir_(cell_solve_data, '_S_' + solve, extra_exclude_filter='get_'), extra_exclude_filter='_S_') if 'get_' not in x and 'set_' not in x and x != 'Type' and x != 'IsValid']
                    if len(solver_params) > 0:
                        out[solve][prop] = solver_params
                    bar_counts += 1
                    bar(float(bar_counts)/total_bar_length)
            bar(1)
        # Remove any empty elements of the dict and restore verbose state
        out = {k: v for k, v in out.items() if v}
        self._verbose = saved_verbose_state
        if print_to_console:
            cp('\n!@lg!@Solver_GetNamesOfAllSolveTypes :: Names of all Solve Types and their Parameters for the given Surface:')
            for SolveKey in out.keys():
                cp('   !@lc!@Solve Type: ' + str(SolveKey))
                for SolveSurface in out[SolveKey].keys():
                    cp('        !@lb!@Surface Property: ' + SolveSurface)
                    cp('            !@lm!@Parameters: ')
                    for SolveParameter in out[SolveKey][SolveSurface]:
                        cp('               !@lm!@' + str(SolveParameter))
            cp('\n')
        return out
    else:
        # Not looking through surfaces, just print (if asked to) and return the list of solver names.
        if print_to_console:
            cp('\n!@lg!@Solver_GetNamesOfAllSolveTypes :: Names of all Solve Types:')
            [cp('   !@lm!@' + str(x)) for x in solve_types]
            cp('\n')
        return solve_types

def Solver_LDESurfaceProperty_ForValue(self, in_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow], property:Union[str,int], solve_type:str, params:dict):
    """
    Solves the property of the surface for a the parameters of the solve type.

    There are a fair number of combinations/settings which this function can implement.
    It is recommended that the user refer to the documentation of Zemax (the ISolve interfaces in the ZOS-API help and the main help PDF section 2.3.1.4. Solve Types).
    However, to compliment this, skZemax provides :func:`Solver_GetNamesOfAllSolveTypes` to help one look up the information in python - but this is not recommend over reading the documentation.

    :param in_surface: The surface to set - either an index or object.
    :type in_surface: Union[int, ZOSAPI_Editors_LDE_ILDERow]
    :param property:  A string identifying the property to make variable - this will be one of the object's column properties (keys in dict of :func:`LDE_GetAllColumnDataOfSurface`).
    :type property: Union[str,int]
    :param solve_type: the solve type to use. See output of :func:`Solver_GetNamesOfAllSolveTypes` with in_surface=None.
    :type solve_type: str
    :param params: The dict of params should have the properties and values for this solve. See :func:`Solver_GetNamesOfAllSolveTypes` with in_surface=in_surface.
    :type params: dict
    """
    in_surface = self._convert_raw_surface_input_(in_surface, return_index=False)
    # Get 'property' cell, i.e. RadiusCell or ThicknessCell, etc
    CellPropertyCallback = in_surface.GetCellAt(int(self.LDE_GetSurfaceColumnEnum(property, in_surface)))
    # On that property cell, invoke the solver of type 'value'. I.e. FNumber or Position
    Solver = CellPropertyCallback.CreateSolveType(self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.SolveType, solve_type))
    # Get out the '_S_' parameters of that solver (settings of this solver)
    SolverParamCallback = self._CheckIfStringValidInDir_(Solver, '_S_' + solve_type, extra_exclude_filter='get_')
    # Set the properties to be solved for (from the params dict).
    for key in params:
        self._SetAttrByStringIfValid_(in_obj=SolverParamCallback, in_string=key, extra_exclude_filter='get_', in_value=params[key])
    # Set the solver
    CellPropertyCallback.SetSolveData(Solver)

##############################################################
# Solver Settings - multi-configuration
##############################################################
def Solver_MCEMakeConfigOpVariable(self, in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow], config_number:int)->ZOSAPI_Editors_MCE_IMCERow:
    """
    Sets the property of the ZOSAPI_Editors_MCE_IMCERow (MCE operand) for the configuration number to a variable solve.

    In more plane terms, this will apply an MCE operand to different (multi-)configuration numbers of Zemax.

    :param in_op: the MCR operand (either index or object)
    :type in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow]
    :param config_number: The Zemax (multi-)configuration number.
    :type config_number: int
    :return: The operand object.
    :rtype: ZOSAPI_Editors_MCE_IMCERow
    """
    in_op = self._convert_raw_MCEOper_input_(in_op, return_index=False)
    solvetype = in_op.GetOperandCell(config_number).CreateSolveType(self.ZOSAPI.Editors.SolveType.Variable)
    in_op.GetOperandCell(config_number).SetSolveData(solvetype)
    return in_op

    ''''''
def Solver_MCEMakeConfigOp_ForValue(self, in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow], config_number:int, solve_type:str, params:dict)->ZOSAPI_Editors_MCE_IMCERow:
    """
    Sets the property property of the ZOSAPI_Editors_MCE_IMCERow (MCE operand) for the configuration number to a solve for value.
    
    This is the Zemax (multi-)configuration version of :func:`Solver_LDESurfaceProperty_ForValue`. 
    So see that function for more detail.

    :param in_op: the MCR operand (either index or object)
    :type in_op: Union[int, ZOSAPI_Editors_MCE_IMCERow]
    :param config_number: The Zemax (multi-)configuration number.
    :type config_number: int
    :param solve_type: the solve type to use. 
    :type value: str
    :param params: The dict of params should have the properties and values for this solve. 
    :type params: dict

    :return: The MCR operand object.
    :rtype: ZOSAPI_Editors_MCE_IMCERow
    """
    in_op = self._convert_raw_MCEOper_input_(in_op, return_index=False)
    Solver = in_op.GetOperandCell(config_number).CreateSolveType(self._CheckIfStringValidInDir_(self.ZOSAPI.Editors.SolveType, solve_type))
    SolverParamCallback = self._CheckIfStringValidInDir_(Solver, '_S_' + solve_type, extra_exclude_filter='get_')
    for key in params:
        self._SetAttrByStringIfValid_(in_obj=SolverParamCallback, in_string=key, extra_exclude_filter='get_', in_value=params[key])
    in_op.GetOperandCell(config_number).SetSolveData(Solver)
    return in_op


