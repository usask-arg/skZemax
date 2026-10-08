from __future__ import annotations

from pathlib import Path
import inspect
import os
import sys
from box import Box

from skZemax.skZemax_subfunctions._c_print import c_print as cp


def Utilities_ZemaxInstallationExampleDir(self) -> Path:
    """
    Returns directory of the default Zemax example files given with the installation.

    :return: Path to dir.
    :rtype: Path
    """
    return Path(self.TheApplication.SamplesDir)


def Utilities_ZemaxInstallationCoatingDir(self) -> Path:
    """
    Returns directory of the default Zemax coating (.zec) files given with the installation.

    :return: Path to dir.
    :rtype: Path
    """
    return Path(self.TheApplication.CoatingDir)


def Utilities_ZemaxInstallationMaterialDir(self) -> Path:
    """
    Returns directory of the default Zemax material (.agf , .bgf) files given with the installation.

    :return: Path to dir.
    :rtype: Path
    """
    return Path(self.TheApplication.GlassDir)


def Utilities_ZemaxInstallationScatterDir(self) -> Path:
    """
    Returns directory of the default Zemax scatter (.bsdf) files given with the installation.

    :return: Path to dir.
    :rtype: Path
    """
    return Path(self.TheApplication.ScatterDir)


def Utilities_ZemaxInstallationPolygonObjectDir(self) -> Path:
    """
    Returns directory of the default Zemax polygon object (.pob) files given with the installation.

    :return: Path to dir.
    :rtype: Path
    """
    return Path(self.TheApplication.ObjectsDir + os.sep + "Polygon Objects")


def Utilities_ZemaxInstallationCADObjectDir(self) -> Path:
    """
    Returns directory of the default Zemax CAD object (.stp , .stl , .igs) files given with the installation.

    :return: Path to dir.
    :rtype: str
    """
    return Path(self.TheApplication.ObjectsDir + os.sep + "CAD Files")


def Utilities_ZemaxInstallationSourceDir(self) -> Path:
    """
    Returns directory of the default Zemax CAD object (.stp , .stl , .igs) files given with the installation.

    :return: Path to dir.
    :rtype: Path
    """
    return Path(self.TheApplication.ObjectsDir + os.sep + "Sources" + os.sep + "Source Files")

def Utilities_ZemaxInstallationImageDir(self) -> Path:
    """
    Returns directory of the default Zemax images (.png , .bmp , .ima) files given with the installation.

    :return: Path to dir.
    :rtype: Path
    """
    return Path(self.TheApplication.ImagesDir)


def Utilities_skZemaxExampleDir(self) -> Path:
    """
    Returns directory of skZemax example files adapted to use skZemax.

    :return: Path to dir.
    :rtype: Path
    """
    pythondir = Path(__file__).parent.parent.parent.parent / 'docs' / 'source' / 'Examples'
    pythondir.mkdir(parents=True, exist_ok=True)
    return pythondir


def Utilities_ConfigFilesDir(self) -> Path:
    """
    Returns a skZemax default directory of Zemax configuration files.
    For instance, the ZOS-API for analyses functions does not generally work natively. To bypass this, skZemax writes - and then loads - intermediate configuration files for it.
    These files are stored in this directory.

    :return: Path to dir.
    :rtype: Path
    """
    cnfdir = Path(__file__).parent.parent / 'ZemaxConfigFiles' 
    cnfdir.mkdir(parents=True, exist_ok=True)
    return cnfdir


def Utilities_DetectorFilesDir(self) -> Path:
    """
    Returns a skZemax default directory of Zemax detector files (.DDR or .DDP files).

    :return: Absolute path to the detector files directory.
    :rtype: Path
    """
    cnfdir = Path(__file__).parent.parent / 'ZemaxDetectorFiles' 
    cnfdir.mkdir(parents=True, exist_ok=True)
    return cnfdir


def Utilities_AnalysesFilesDir(self) -> Path:
    """
    Returns a skZemax default directory of Zemax (intermediate) analyses files.

    :return: Absolute path to the analysis files directory.
    :rtype: Path
    """
    cnfdir = Path(__file__).parent.parent / 'ZemaxAnalysesFiles' 
    cnfdir.mkdir(parents=True, exist_ok=True)
    return cnfdir


def Utilities_MainProgramDir(self) -> Path:
    """
    Returns an absolute path to the directory of the first python file being run in *any* python program (sys.argv[0]).

    :return: Absolute path to the main python file being run.
    :rtype: Path
    """
    return Path(sys.argv[0]).parent


def Utilities_OpenZemaxFile(self, in_file_path: str|Path, save_first: bool = False):
    """
    Opens a Zemax file.

    :param in_file_path: Path to file.
    :type in_file_path: str|Path
    :param save_first: Indicates if one should save the current Zemax file (if any) before making the new file, defaults to False
    :type save_first: bool, optional
    """
    if self._verbose:
        cp(
            "!@lg!@OpenZemaxFile :: {} Opening Zemax file [!@lm!@{}!@lg!@].".format(
                "Saved current Zemax file." if save_first else "", in_file_path
            )
        )
    self.TheSystem.LoadFile(str(in_file_path), save_first)


def Utilities_MakeNewZemaxFile(
    self, in_file_path: str|Path, save_first: bool = False
) -> None:
    """
    Makes a new Zemax file.

    :param in_file_path: Path to file.
    :type in_file_path: str|Path
    :param save_first: Indicates if one should save the current Zemax file (if any) before making the new file, defaults to False
    :type save_first: bool, optional
    """
    self.TheSystem.New(save_first)
    self.TheSystem.SaveAs(str(in_file_path))
    if self._verbose:
        cp(
            "!@lg!@MakeNewZemaxFile :: {} New Zemax file [!@lm!@{}!@lg!@] created.".format(
                "Saved current Zemax file." if save_first else "", in_file_path
            )
        )


def Utilities_SaveZemaxFile(self) -> None:
    """
    Saves the current Zemax file
    """
    if self._verbose:
        cp("!@lg!@SaveZemaxFile :: Saving Current Zemax File.")
    self.TheSystem.Save()


def Utilities_SaveZemaxFileAs(self, in_file_path: str|Path) -> None:
    """
    Saves the current Zemax file a a new file.

    :param in_file_path: Path to file.
    :type in_file_path: str|Path
    """
    if self._verbose:
        cp(
            f"!@lg!@SaveZemaxFileAs :: Saving Current Zemax File As [!@lm!@{in_file_path}!@lg!@]."
        )
    self.TheSystem.SaveAs(str(in_file_path))


def Utilities_GetAllSystemUnits(self) -> Box:
    """
    Returns the units the current system is working in.

    :return: dict[property] = "units"
    :rtype: Box
    """
    out = Box({})
    unit_kinds = [
        x for x in dir(self.TheSystem.SystemData.Units) if "get_" in x
    ]  # and 'Prefix' not in x]
    for kind in unit_kinds:
        f = getattr(self.TheSystem.SystemData.Units, kind)
        out[kind.split("get_")[-1]] = str(f())
    return out
