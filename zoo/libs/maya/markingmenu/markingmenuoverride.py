import re

from maya import cmds, mel

from zoo.libs.maya import triggered
from zoo.libs.utils import path
from zoo.libs.utils import zlogging

logger = zlogging.zooLogger


def setup():
    """
    Installs modifications to the dagProcMenu script for the current session
    """
    try:
        dagMenuScriptpath = path.findFirstInEnv('dagMenuProc.mel', 'MAYA_SCRIPT_PATH')
        polyCutUVOptionsPopupScriptpath = path.findFirstInEnv('polyCutUVOptionsPopup.mel', 'MAYA_SCRIPT_PATH')
    except:
        logger.warning("Cannot find the dagMenuProc.mel script - aborting auto-override!")
        return
    tmpScriptpath = path.Path(cmds.internalVar(usd=True)) / 'zooDagMenuProc_override.mel'

    def writeZooLines(fStream, parentVarStr, objectVarStr):
        fStream.write('\n/// ZOO MODS ########################\n')
        fStream.write('\tsetParent -m $parent;\n')
        fStream.write('\tmenuItem -d 1;\n')
        fStream.write('\tpython("from zoo.libs.maya.markingmenu import markingmenu_validate");\n')
        fStream.write(
            """\tint $killState = python("markingmenu_validate.validateAndBuild('{}', '{}')");\n""".format(parentVarStr,
                                                                                                           objectVarStr))
        fStream.write('\tif($killState) return;\n')
        fStream.write('/// END ZOO MODS ####################\n\n')

    globalProcDefRex = re.compile(
        "^global +proc +dagMenuProc *\(*string *(\$[a-zA-Z0-9_]+), *string *(\$[a-zA-Z0-9_]+) *\)")
    with open(dagMenuScriptpath) as f:
        dagMenuScriptLineIter = iter(f)
        with open(tmpScriptpath, 'w') as f2:
            hasDagMenuProcBeenSetup = False
            for line in dagMenuScriptLineIter:
                f2.write(line)

                globalProcDefSearch = globalProcDefRex.search(line)
                if globalProcDefSearch:
                    parentVarStr, objectVarStr = globalProcDefSearch.groups()

                    if '{' in line:
                        writeZooLines(f2, parentVarStr, objectVarStr)
                        hasDagMenuProcBeenSetup = True

                    if not hasDagMenuProcBeenSetup:
                        for line in dagMenuScriptLineIter:
                            f2.write(line)
                            if '{' in line:
                                writeZooLines(f2, parentVarStr, objectVarStr)
                                hasDagMenuProcBeenSetup = True
                                break

        if not hasDagMenuProcBeenSetup:
            logger.error("Couldn't auto setup dagMenuProc!", exc_info=1)
            return
        mel.eval('source "{}";'.format(polyCutUVOptionsPopupScriptpath))
        # NOTE: this needs to be done twice to actually take...  go figure
        mel.eval('source "{}";'.format(tmpScriptpath))
    # Now delete the tmp script - we don't want the "mess"
    tmpScriptpath.delete()

    # The dag menu customizations are centered around triggered, so load it up!
    triggered.Load()
