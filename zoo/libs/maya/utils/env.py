import sys
import os
import platform

from maya.OpenMaya import MGlobal
from maya.api import OpenMaya as om2
from zoo.libs.utils import zlogging
from zoo.libs.maya.api import nodes

logger = zlogging.zooLogger


def getMayaLocation(mayaVersion):
    """Gets the generic maya location where maya is installed

    :param mayaVersion: The version of maya to find
    :type mayaVersion: int
    :return: The folder path to the maya install folder
    :rtype: str
    """
    location = os.environ.get("MAYA_LOCATION", "")
    if location:
        return location
    if platform.system() == "Windows":
        location = os.path.join("C:\\", "Program Files", "Autodesk", "Maya%s" % mayaVersion)
    elif platform.system() == "Darwin":
        return os.path.join("/Applications", "Autodesk", "maya{0}".format(mayaVersion), "Maya.app", "Contents")
    else:
        location = os.path.join("usr", "autodesk", "maya{0}- x64".format(mayaVersion))

    return location


def mayaScriptPaths():
    """Returns a list of maya script paths, received from the MAYA_SCRIPT_PATH environment
    
    :rtype: list(str)
    """
    try:
        return os.environ["MAYA_SCRIPT_PATH"].split(os.path.pathsep)
    except KeyError:
        logger.debug("Could not find MAYA_SCRIPT_PATH in environ")
        raise


def mayaModulePaths():
    """Returns a list of maya module paths, received from the MAYA_MODULE_PATH environment

    :rtype: list(str)
    """
    try:
        return os.environ["MAYA_MODULE_PATH"].split(os.path.pathsep)
    except KeyError:
        logger.debug("Could not find MAYA_MODULE_PATH in environ")
        raise


def mayaPluginPaths():
    """Returns a list of maya plugin paths, received from the MAYA_PLUG_IN_PATH environment

    :rtype: list(str)
    """
    try:
        return os.environ["MAYA_PLUG_IN_PATH"].split(os.path.pathsep)
    except KeyError:
        logger.debug("Could not find MAYA_PLUG_IN_PATH in environ")
        raise


def pythonPath():
    """Return a list of paths, received from the PYTHONPATH evironment

    :return: a list of paths
    :rtype: list(str)
    """
    try:
        return os.environ["PYTHONPATH"].split(os.path.pathsep)
    except KeyError:
        logger.debug("Could not find PYTHONPATH in environ")
        raise


def mayaIconPath():
    """Returns the xbmlangpath environment as a list of path
    
    :rtype: list(str)
    """
    try:
        paths = os.environ["XBMLANGPATH"].split(os.path.pathsep)
    except KeyError:
        logger.debug("Could not find XBMLANGPATH in environ")
        raise
    return paths


def getEnvironment():
    """Gets maya main environment variable and returns as a dict

    :return: dict
    """
    data = {"MAYA_SCRIPT_PATH": mayaScriptPaths(),
            "MAYA_PLUG_IN_PATH": mayaPluginPaths(),
            "MAYA_MODULE_IN_PATH": mayaModulePaths(),
            "PYTHONPATH": pythonPath(),
            "XBMLANGPATH": mayaIconPath(),
            "sys.path": sys.path.split(os.pathsep),
            "PATH": os.environ["PATH"].split(os.pathsep)}
    return data


def printEnvironment():
    """logs the maya environment to the logger
    """
    logger.info("\nMAYA_SCRIPT_PATHs are: \n %s" % mayaScriptPaths())
    logger.info("\nMAYA_PLUG_IN_PATHs are: \n %s" % mayaPluginPaths())
    logger.info("\nMAYA_MODULE_PATHs are: \n %s" % mayaModulePaths())
    logger.info("\nPYTHONPATHs are: \n %s" % pythonPath())
    logger.info("\nXBMLANGPATHs are: \n %s" % mayaIconPath())
    logger.info("\nsys.paths are: \n %s" % sys.path.split(os.pathsep))


def mayapy(mayaVersion):
    """Returns the location of the mayapy exe path from the mayaversion

    :param mayaVersion: the maya version the workwith
    :type mayaVersion: int
    :return: the mayapy exe file path
    :rtype str
    """
    pyexe = os.path.join(getMayaLocation(mayaVersion), "bin", "mayapy")
    if platform.system() == "Windows":
        pyexe += ".exe"
    return pyexe


def isMayapy():
    """Returns True if the current executable is mayapy

    :return: bool
    """

    if MGlobal.mayaState() == MGlobal.kLibraryApp:
        return True
    return False


def mayaVersion():
    """Returns maya's currently active maya version ie. 2016

    :return: maya version
    :rtype: int
    """
    return int(MGlobal.mayaVersion())


def apiVersion():
    """Returns maya's currently active maya api version ie. 201610

    :return: Maya api version
    :rtype: str
    """
    return MGlobal.apiVersion()


def globalWidthHeight():
    fn = om2.MFnDependencyNode(nodes.asMObject("defaultResolution"))
    width, height = fn.findPlug("width", False).asInt(), fn.findPlug("height", False).asInt()
    return width, height, float(width) / float(height)


def setOverscan(camera, state):
    fn = om2.MFnDependencyNode(camera)
    overscan = fn.findPlug("overscan", False)
    overscan.setFloat(state)


def setCameraClipPlanes(camera, nearClip, farClip):
    fn = om2.MFnDependencyNode(camera)
    fn.findPlug("nearClipPlane", False).setFloat(nearClip)
    fn.findPlug("farClipPlane", False).setFloat(farClip)
