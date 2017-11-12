import contextlib

from maya import cmds
from maya.api import OpenMaya as om2
from maya.api import OpenMayaUI as om2ui
from zoo.libs.maya.api import nodes
from zoo.libs.maya.meta import metacamera


def createCamera(name, start, end, focalLength=35.000,
                         horizontalFilmAperture=1.682):
    # returns the camera transform
    camObj = nodes.createDagNode(name, "camera")
    camObj = [i for i in nodes.iterChildren(camObj, False, om2.MFn.kCamera)]
    # expectation that the camera was created an the transform was returned above
    # add the meta camera data
    meta = metacamera.MetaCamera(camObj[0])
    meta.focalLength = focalLength
    meta.horizontalFilmAperture = horizontalFilmAperture
    meta.shotName = name
    meta.startFrame = start
    meta.endFrame = end
    return meta


@contextlib.contextmanager
def maintainCamera(panel, camera):
    """Context Manager to allow the client to set the current modelpanel to a 
    different camera temporary before setting back to the original camera.

    :param panel: the maya model panel
    :type panel: str
    :param camera: the fullpathName of the camera.
    :type camera: str
    """
    view = om2ui.M3dView()
    currentCamera = view.getM3dViewFromModelPanel(panel)
    cmds.lookThru(panel, camera)
    yield
    cmds.lookThru(panel, currentCamera.fullPathName())


def bakeCameraMeatAnimToClone(camMeta):
    """Given a camera node which has meta data(MetaCamera), create a temporary meta camera which is a clone
    of the camera and bake per frame anim data down. The passed in camera will be renamed so that the camera clone has the
    shot name however we dont not rename the original back to the correct name. The reason for this is so the client
    can do further operations on the baked cam.

    :param camMeta: The MetaCamera instance which is attached to the camera
    :type camMeta: MetaCamera
    :return: The new Baked camera if the keys were baked. otherwise None
    :rtype: MetaCamera or None
    """
    # temp rename so that the the baked camera has the original name
    camMeta.rename("_".join([camMeta.shotName.asString(), "ORIG"]))
    bakedCam = createCamera(camMeta.shotName.asString(), camMeta.startFrame.asInt(), camMeta.endFrame.asInt())
    bakedCam.copyFrom(camMeta)

    result = cmds.copyKey(camMeta.fullPathName())
    if result == 0:
        bakedCam.delete()
        camMeta.rename(camMeta.shotName.asString())
        return
    padding = bakedCam.framePadding.asInt()
    targetName = bakedCam.fullPathName()
    cmds.pasteKey(targetName, option="replace")
    cmds.bakeResults(targetName, t=((bakedCam.startFrame.asInt() - padding), (bakedCam.endFrame.asInt() + padding)),
                     sb=1)
    return bakedCam
