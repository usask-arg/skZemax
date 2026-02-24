from __future__ import annotations

import os
import winreg

import clr


class PythonStandaloneApplication:
    """
    This class is the boilerplate code provided by Zemax to create a standalone Zemax application in python.

    This boilerplate requires the 'pythonnet' module.
    The following instructions are for installing the 'pythonnet' module via pip:
    1. Ensure you are running a Python version compatible with PythonNET. Check the article "ZOS-API using Python.NET" or
    "Getting started with Python" in our knowledge base for more details.
    2. Install 'pythonnet' from pip via a command prompt (type 'cmd' from the start menu or press Windows + R and type 'cmd' then enter)

        python -m pip install pythonnet
    """

    class LicenseException(Exception):
        pass

    class ConnectionException(Exception):
        pass

    class InitializationException(Exception):
        pass

    class SystemNotPresentException(Exception):
        pass

    def __init__(self, path=None):
        # determine location of ZOSAPI_NetHelper.dll & add as reference
        aKey = winreg.OpenKey(
            winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
            r"Software\Zemax",
            0,
            winreg.KEY_READ,
        )
        zemaxData = winreg.QueryValueEx(aKey, "ZemaxRoot")
        NetHelper = os.path.join(
            os.sep, zemaxData[0], r"ZOS-API\Libraries\ZOSAPI_NetHelper.dll"
        )
        winreg.CloseKey(aKey)
        clr.AddReference(NetHelper)
        import ZOSAPI_NetHelper

        # Find the installed version of OpticStudio
        # if len(path) == 0:
        if path is None:
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize()
        else:
            # Note -- uncomment the following line to use a custom initialization path
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(path)

        # determine the ZOS root directory
        if isInitialized:
            dir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
        else:
            msg = "Unable to locate Zemax OpticStudio.  Try using a hard-coded path."
            raise PythonStandaloneApplication.InitializationException(msg)

        # add ZOS-API referencecs
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI.dll"))
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI_Interfaces.dll"))
        import ZOSAPI

        # create a reference to the API namespace
        self.ZOSAPI = ZOSAPI

        # Create the initial connection class
        self.TheConnection = ZOSAPI.ZOSAPI_Connection()

        if self.TheConnection is None:
            msg = "Unable to initialize .NET connection to ZOSAPI"
            raise PythonStandaloneApplication.ConnectionException(msg)

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            msg = "Unable to acquire ZOSAPI application"
            raise PythonStandaloneApplication.InitializationException(msg)

        if not self.TheApplication.IsValidLicenseForAPI:
            msg = "License is not valid for ZOSAPI use"
            raise PythonStandaloneApplication.LicenseException(msg)

        self.TheSystem = self.TheApplication.PrimarySystem
        if self.TheSystem is None:
            msg = "Unable to acquire Primary system"
            raise PythonStandaloneApplication.SystemNotPresentException(msg)

    def __del__(self):
        if self.TheApplication is not None:
            self.TheApplication.CloseApplication()
            self.TheApplication = None

        self.TheConnection = None

    def SamplesDir(self):
        if self.TheApplication is None:
            msg = "Unable to acquire ZOSAPI application"
            raise PythonStandaloneApplication.InitializationException(msg)

        return self.TheApplication.SamplesDir

    def ExampleConstants(self):
        if (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.PremiumEdition
        ):
            return "Premium"
        if (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.EnterpriseEdition
        ):
            return "Enterprise"
        if (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.ProfessionalEdition
        ):
            return "Professional"
        if (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.StandardEdition
        ):
            return "Standard"
        if (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.OpticStudioHPCEdition
        ):
            return "HPC"
        return "Invalid"
