from maya.api import OpenMaya as om2

from zoo.libs.maya.meta import base
from zoo.libs.maya.api import attrtypes, nodes


class MetaCamera(base.MetaBase):
    icon = "camera"

    def __init__(self, node=None, name=None, initDefaults=True):
        super(MetaCamera, self).__init__(node, name, initDefaults)
        self.camMfn.findPlug("horizontalFilmAperture", False).isLocked = True
        self.camMfn.findPlug("verticalFilmAperture", False).isLocked = True

    def _createInScene(self, node, name):
        if node is None:
            name = "_".join([name or self.__class__.__name__, "meta"])
            node= nodes.createDagNode(name, "camera")
        self._handle = om2.MObjectHandle(node)
        if node.hasFn(om2.MFn.kDagNode):
            self._mfn = om2.MFnDagNode(node)
        else:
            self._mfn = om2.MFnDependencyNode(node)

        if node.hasFn(om2.MFn.kTransform):
            node = list(nodes.iterChildren(self.mobject(), False, om2.MFn.kCamera))[0]
        self.camMfn = om2.MFnCamera(node)
    def _initMeta(self):
        super(MetaCamera, self)._initMeta()
        self.addAttribute("isCamera", True, attrtypes.kMFnNumericBoolean)
        self.addAttribute("startFrame", 0, attrtypes.kMFnNumericInt)
        self.addAttribute("endFrame", 0, attrtypes.kMFnNumericInt)
        self.addAttribute("framePadding", 10, attrtypes.kMFnNumericInt)
        self.addAttribute("shotName", "", attrtypes.kMFnDataString)
        self.addAttribute("camera_version", 1, attrtypes.kMFnNumericInt)

    @property
    def aspectRatio(self):
        return self.camMfn.aspectRatio()

    @aspectRatio.setter
    def aspectRatio(self, value):
        vPlug = self.camMfn.findPlug("verticalFilmAperture", False)
        hPlug = self.camMfn.findPlug("horizontalFilmAperture", False)
        vPlug.isLocked = False
        hPlug.isLocked = False
        self.camMfn.setAspectRatio(value)
        vPlug.isLocked = True
        hPlug.isLocked = True

    @property
    def focalLength(self):
        return self.camMfn.focalLength

    @focalLength.setter
    def focalLength(self, value):
        self.camMfn.focalLength = value

    @property
    def verticalFilmAperture(self):
        return self.camMfn.verticalFilmAperture

    @verticalFilmAperture.setter
    def verticalFilmAperture(self, value):
        vPlug = self.camMfn.findPlug("verticalFilmAperture", False)
        hPlug = self.camMfn.findPlug("horizontalFilmAperture", False)
        vPlug.isLocked = False
        hPlug.isLocked = False
        self.camMfn.verticalFilmAperture = value
        vPlug.isLocked = True
        hPlug.isLocked = True

    @property
    def horizontalFilmAperture(self):
        return self.camMfn.horizontalFilmAperture

    @horizontalFilmAperture.setter
    def horizontalFilmAperture(self, value):
        vPlug = self.camMfn.findPlug("verticalFilmAperture", False)
        hPlug = self.camMfn.findPlug("horizontalFilmAperture", False)
        vPlug.isLocked = False
        hPlug.isLocked = False
        self.camMfn.horizontalFilmAperture = value
        vPlug.isLocked = True
        hPlug.isLocked = True

    @property
    def filmFit(self):
        return self.camMfn.filmFit

    @filmFit.setter
    def filmFit(self, value):
        self.camMfn.filmFit = int(value)

    def copyFrom(self, metaCamera):
        self.lockedOff = metaCamera.lockedOff.asBool()
        self.startFrame = metaCamera.startFrame.asInt()
        self.endFrame = metaCamera.endFrame.asInt()
        self.framePadding = metaCamera.framePadding.asInt()
        self.shotName = metaCamera.shotName.asString()
        self.camera_version = metaCamera.camera_version.asInt()
        self.shotgun_context = metaCamera.shotgun_context.asString()
        self.filmFit = float(metaCamera.filmFit)
        self.aspectRatio = float(metaCamera.aspectRatio)
        self.focalLength = float(metaCamera.focalLength)
        self.verticalFilmAperture = float(metaCamera.verticalFilmAperture)
