from __future__ import annotations
import inspect
import os
import sys
from skZemax.skZemax_subfunctions._c_print import c_print as cp


def Utilities_ZemaxInstallationExampleDir(self)->str:
    """
    Returns directory of the default Zemax example files given with the installation.

    :return: Path to dir.
    :rtype: str
    """
    return self.TheApplication.SamplesDir

def Utilities_ZemaxInstallationCoatingDir(self)->str:
    """
    Returns directory of the default Zemax coating (.zec) files given with the installation.

    :return: Path to dir.
    :rtype: str
    """
    return self.TheApplication.CoatingDir

def Utilities_ZemaxInstallationMaterialDir(self)->str:
    """
    Returns directory of the default Zemax material (.agf , .bgf) files given with the installation.

    :return: Path to dir.
    :rtype: str
    """
    return self.TheApplication.GlassDir

def Utilities_ZemaxInstallationScatterDir(self)->str:
    """
    Returns directory of the default Zemax scatter (.bsdf) files given with the installation.

    :return: Path to dir.
    :rtype: str
    """
    return self.TheApplication.ScatterDir

def Utilities_ZemaxInstallationPolygonObjectDir(self)->str:
    """
    Returns directory of the default Zemax polygon object (.pob) files given with the installation.

    :return: Path to dir.
    :rtype: str
    """
    return self.TheApplication.ObjectsDir + os.sep + 'Polygon Objects'

def Utilities_ZemaxInstallationCADObjectDir(self)->str:
    """
    Returns directory of the default Zemax CAD object (.stp , .stl , .igs) files given with the installation.

    :return: Path to dir.
    :rtype: str
    """
    return self.TheApplication.ObjectsDir + os.sep + 'CAD Files'

def Utilities_ZemaxInstallationImageDir(self)->str:
    """
    Returns directory of the default Zemax images (.png , .bmp , .ima) files given with the installation.

    :return: Path to dir.
    :rtype: str
    """
    return self.TheApplication.ImagesDir

def Utilities_skZemaxExampleDir(self)->str:
    """
    Returns directory of skZemax example files adapted to use skZemax.

    :return: Path to dir.
    :rtype: str
    """
    pythondir = os.path.abspath(os.sep.join(os.path.abspath(inspect.getfile(Utilities_skZemaxExampleDir)).split(os.sep)[0:-1]) + os.sep + '..'+ os.sep + '..'+ os.sep + '..' + os.sep + "docs" + os.sep + "source" + os.sep + "Examples")
    if not os.path.exists(pythondir):
        os.makedirs(pythondir)
    return pythondir

def Utilities_ConfigFilesDir(self)->str:
    """
    Returns a skZemax default directory of Zemax configuration files.
    For instance, the ZOS-API for analyses functions does not generally work natively. To bypass this, skZemax writes - and then loads - intermediate configuration files for it.
    These files are stored in this directory.

    :return: Path to dir.
    :rtype: str
    """
    cnfdir = os.path.abspath(os.sep.join(os.path.abspath(inspect.getfile(Utilities_ConfigFilesDir)).split(os.sep)[0:-1]) + os.sep + '..' + os.sep + 'ZemaxConfigFiles')
    # creates a new directory
    if not os.path.exists(cnfdir):
       os.makedirs(cnfdir)
    return cnfdir

def Utilities_DetectorFilesDir(self)->str:
    """
    Returns a skZemax default directory of Zemax detector files (.DDR or .DDP files).

    :return: Absolute path to the detector files directory.
    :rtype: str
    """
    cnfdir = os.path.abspath(os.sep.join(os.path.abspath(inspect.getfile(Utilities_DetectorFilesDir)).split(os.sep)[0:-1]) + os.sep + '..' + os.sep + 'ZemaxDetectorFiles')
    # creates a new directory
    if not os.path.exists(cnfdir):
       os.makedirs(cnfdir)
    return cnfdir

def Utilities_AnalysesFilesDir(self)->str:
    """
    Returns a skZemax default directory of Zemax (intermediate) analyses files.

    :return: Absolute path to the analysis files directory.
    :rtype: str
    """
    cnfdir = os.path.abspath(os.sep.join(os.path.abspath(inspect.getfile(Utilities_DetectorFilesDir)).split(os.sep)[0:-1]) + os.sep + '..' + os.sep + 'ZemaxAnalysesFiles')
    # creates a new directory
    if not os.path.exists(cnfdir):
       os.makedirs(cnfdir)
    return cnfdir

def Utilities_MainProgramDir(self)->str:
    """
    Returns an absolute path to the directory of the first python file being run in *any* python program (sys.argv[0]).

    :return: Absolute path to the main python file being run. 
    :rtype: str
    """
    return os.path.abspath(os.path.dirname(sys.argv[0]))


def Utilities_OpenZemaxFile(self,in_file_path:str, save_first:bool=False):
    """
    Opens a Zemax file.

    :param in_file_path: Path to file.
    :type in_file_path: str
    :param save_first: Indicates if one should save the current Zemax file (if any) before making the new file, defaults to False
    :type save_first: bool, optional
    """
    if self._verbose: cp('!@lg!@OpenZemaxFile :: %s Opening Zemax file [!@lm!@%s!@lg!@].'
                            % ('Saved current Zemax file.' if save_first else '', in_file_path))
    self.TheSystem.LoadFile(in_file_path, save_first)

def Utilities_MakeNewZemaxFile(self,in_file_path:str, save_first:bool=False)->None:
    """
    Makes a new Zemax file. 

    :param in_file_path: Path to file.
    :type in_file_path: str
    :param save_first: Indicates if one should save the current Zemax file (if any) before making the new file, defaults to False
    :type save_first: bool, optional
    """
    self.TheSystem.New(save_first)
    self.TheSystem.SaveAs(str(in_file_path))
    if self._verbose: cp('!@lg!@MakeNewZemaxFile :: %s New Zemax file [!@lm!@%s!@lg!@] created.'
                            % ('Saved current Zemax file.' if save_first else '', in_file_path))

def Utilities_SaveZemaxFile(self)->None:
    """
    Saves the current Zemax file
    """
    if self._verbose: cp('!@lg!@SaveZemaxFile :: Saving Current Zemax File.')
    self.TheSystem.Save()

def Utilities_SaveZemaxFileAs(self, in_file_path:str)->None:
    """
    Saves the current Zemax file a a new file.

    :param in_file_path: Path to file.
    :type in_file_path: str
    """
    if self._verbose: cp('!@lg!@SaveZemaxFileAs :: Saving Current Zemax File As [!@lm!@%s!@lg!@].'%in_file_path)
    self.TheSystem.SaveAs(str(in_file_path))

def Utilities_GetAllSystemUnits(self)->dict:
    """
    Returns the units the current system is working in.

    :return: dict[property] = "units"
    :rtype: dict
    """
    out = dict()
    unit_kinds = [x for x in dir(self.TheSystem.SystemData.Units) if 'get_' in x] # and 'Prefix' not in x]
    for kind in unit_kinds:
        f = getattr(self.TheSystem.SystemData.Units, kind)
        out[kind.split('get_')[-1]] = str(f())
    return out




