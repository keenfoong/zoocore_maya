import contextlib

from zoo.libs.maya.utils import general
from maya import cmds, mel
from maya.api import OpenMaya as om2
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs


@contextlib.contextmanager
def exportContext(rootNode):
    changed = []
    for i in nodes.iterChildren(rootNode, recursive=True):
        dp = om2.MFnDependencyNode(i)
        plug = dp.findPlug("visibility", False)
        with plugs.setLockedContext(plug):
            if plug.asFloat() != 1.0:
                plugs.setPlugValue(plug, 1.0)
                changed.append(dp)
    yield
    for i in iter(changed):
        plug = i.findPlug("visibility", False)
        with plugs.setLockedContext(plug):
            plugs.setPlugValue(plug, 0.0)


def exportSceneAsFbx(filePath):
    filePath = filePath.replace("/", "\\")
    mel.eval("FBXExportSmoothingGroups -v true;")
    mel.eval("FBXExportHardEdges -v true;")
    mel.eval("FBXExportTangents -v true;")
    mel.eval("FBXExportSmoothMesh -v false;")
    mel.eval("FBXExportInstances -v true;")
    # Animation
    mel.eval("FBXExportBakeComplexAnimation -v false;")
    mel.eval("FBXExportUseSceneName -v false;")
    mel.eval("FBXExportQuaternion -v euler;")
    mel.eval("FBXExportShapes -v true;")
    mel.eval("FBXExportSkins -v true;")
    mel.eval("FBXExportConstraints -v true;")
    mel.eval("FBXExportCameras -v true;")
    mel.eval("FBXExportLights -v true;")
    mel.eval("FBXExportEmbeddedTextures -v false;")
    mel.eval("FBXExportInputConnections -v true;")
    mel.eval("FBXExportUpAxis {};".format(general.upAxis()))
    mel.eval('FBXExport -f "{}";'.format(filePath.replace("\\", "/")))  # this maya is retarded
    return filePath


def exportAbc(filePath, sceneNode, frameRange="1 1", visibility=True, creases=True, uvSets=True, dataFormat="ogawa"):
    filePath = filePath.replace("/", "\\")
    command = "-frameRange {} -dataFormat {}".format(frameRange, dataFormat)
    if visibility:
        command += " -writeVisibility"
    if creases:
        command += " -writeCreases"
    if uvSets:
        command += " -writeUVSets"
    command += " -root {} -file {}".format(sceneNode, filePath)
    cmds.AbcExport(j=command)
    return filePath


def exportObj(filePath, sceneNode):
    filePath = filePath.replace("/", "\\")
    cmds.select(sceneNode)
    cmds.file(filePath, force=True, options="groups=0;ptgroups=0;materials=0;smoothing=1;normals=1", typ="OBJexport",
              pr=True,
              es=True)
    cmds.select(cl=True)
    return filePath


def importAlembic(filePath):
    cmds.AbcImport(filePath, mode="import")
    return filePath


def importObj(filePath):
    cmds.file(filePath, i=True, type="OBJ", ignoreVersion=True, mergeNamespacesOnClash=False, options="mo=1;lo=0")
    return filePath


def importFbx(filepath, cameras=False, lights=False):
    filepath = filepath.replace("/", "\\")
    mel.eval("FBXImportMode -v add;")
    mel.eval("FBXImportMergeAnimationLayers -v false;")
    mel.eval("FBXImportProtectDrivenKeys -v false;")
    mel.eval("FBXImportConvertDeformingNullsToJoint -v false;")
    mel.eval("FBXImportMergeBackNullPivots -v false;")
    mel.eval("FBXImportSetLockedAttribute -v true;")
    mel.eval("FBXImportConstraints -v false;")
    mel.eval("FBXImportLights -v {};".format(str(lights).lower()))
    mel.eval("FBXImportCameras -v {};".format(str(cameras).lower()))
    mel.eval("FBXImportHardEdges -v true;")
    mel.eval("FBXImportShapes -v true;")
    mel.eval("FBXImportUnlockNormals -v true;")
    mel.eval('FBXImport -f "{}";'.format(filepath.replace("\\", "/")))  # stupid autodesk and there mel crap

    return True


def exportFbx(filePath, sceneNode, version="FBX201600"):
    filePath = filePath.replace("/", "\\")

    with exportContext(nodes.asMObject(sceneNode)):
        mel.eval("FBXResetExport ;")
        mel.eval("FBXExportSmoothingGroups -v true;")
        mel.eval("FBXExportHardEdges -v true;")
        mel.eval("FBXExportTangents -v true;")
        mel.eval("FBXExportSmoothMesh -v false;")
        mel.eval("FBXExportInstances -v true;")
        # Animation
        mel.eval("FBXExportBakeComplexAnimation -v true;")
        mel.eval("FBXExportApplyConstantKeyReducer -v true;")
        mel.eval("FBXExportUseSceneName -v false;")
        mel.eval("FBXExportQuaternion -v euler;")
        mel.eval("FBXExportShapes -v true;")
        mel.eval("FBXExportSkins -v true;")
        mel.eval("FBXExportConstraints -v false;")
        mel.eval("FBXExportCameras -v true;")
        mel.eval("FBXExportLights -v true;")
        mel.eval("FBXExportEmbeddedTextures -v false;")
        mel.eval("FBXExportInputConnections -v false;")
        mel.eval("FBXExportUpAxis {};".format(general.upAxis()))
        mel.eval("FBXExportFileVersion -v {};".format(version))
        cmds.select(sceneNode)
        mel.eval('FBXExport -f "{}" -s;'.format(filePath.replace("\\", "/")))  # this maya is retarded
        cmds.select(cl=True)
    return filePath
