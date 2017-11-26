import os

from zoo.libs.maya.utils import general
from zoo.libs.utils import zlogging

logger = zlogging.zooLogger


def zooMayaStartUp():
    _setupPlugins()
    _setupIcons()


def _setupPlugins():
    """
    sets up paths for plugins (both binary and python ones) and loads them
    @todo add plugins from all basepaths generically
    """
    basePaths = os.environ['MAYA_PLUG_IN_PATH'].split(os.pathsep)
    extraPaths = os.path.join(os.path.dirname(__file__), "plugins")
    if extraPaths not in basePaths:
        basePaths.append(extraPaths)
        # Set the plug-in path
        os.environ["MAYA_PLUG_IN_PATH"] = os.pathsep.join(basePaths)
    general.loadPlugin("undo.py")


def _setupIcons():
    """
    sets up paths for icons
    """
    basePaths = os.environ['XBMLANGPATH'].split(os.pathsep)
    icons = str(os.path.join(os.environ.get("ZOO_BASE", "").split(os.pathsep)[0], 'icons'))
    if icons not in basePaths:
        basePaths.append(icons)
        os.environ['XBMLANGPATH'] = os.pathsep.join(basePaths)
