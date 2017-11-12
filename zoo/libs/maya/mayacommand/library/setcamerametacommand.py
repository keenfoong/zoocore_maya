from zoo.libs.command import command

from zoo.libs.maya.meta import metacamera
from maya.api import OpenMaya as om2


class SetCameraMetaCommand(command.ZooCommand):
    """This command Sets the meta data on a camera
    """
    id = "zoo.meta.camera.setMetaSettings"
    creator = "David Sparrow"
    isUndoable = True
    uiData = {"icon": "camera",
              "tooltip": "Set camera settings",
              "label": "Set Camera Settings",
              "color": "",
              "backgroundColor": ""
              }
    _settings = {}

    def resolveArguments(self, arguments):
        metaNode = arguments.get("metaNode")
        if not metaNode :
            self.cancel("Please provide at least one metaNode!")
        if isinstance(metaNode, om2.MObject):
            metaNode = metacamera.MetaCamera(metaNode)
        args = {"metaNode": metaNode,
                "shotName": arguments.get("shotName")}
        start = arguments.get("startFrame")
        end = arguments.get("startFrame")
        if start is not None:
            args["start"] = int(start)
        if end is not None:
            args["end"] = int(end)

        return args

    def doIt(self, metaNode=None, startFrame=None, endFrame=None, shotName=None):
        if startFrame is not None:
            self._settings["startFrame"] = metaNode.startFrame.asInt()
            metaNode.startFrame = startFrame
        if endFrame is not None:
            self._settings["endFrame"] = metaNode.endFrame.asBool()
            metaNode.endFrame = endFrame
        if shotName is not None:
            self._settings["shotName"] = metaNode.shotName.asBool()
            metaNode.shotName = shotName
        self._settings["metaNode"] = metaNode

    def undoIt(self):
        if self._settings:
            startFrame = self._settings.get("startFrame")
            endFrame = self._settings.get("endFrame")
            shotName = self._settings.get("shotName")
            metaNode = self._settings["metaNode"]
            if startFrame is not None:
                metaNode.startFrame = startFrame
            if endFrame is not None:
                metaNode.endFrame = endFrame
            if shotName is not None:
                metaNode.shotName = shotName

            return True
        return False