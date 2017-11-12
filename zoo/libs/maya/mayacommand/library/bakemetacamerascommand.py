from zoo.libs.command import command
from zoo.libs.maya.cameras import utils


class BakeMetaCamerasCommand(command.ZooCommand):
    """Takes a source camera shape node and bakes the animation to a dummy camera to maintain the original
    """
    id = "zoo.camera.bake"
    creator = "David Sparrow"
    isUndoable = True
    uiData = {"icon": "",
              "tooltip": "Bake Camera meta node",
              "label": "Bake camera Animation",
              "color": "",
              "backgroundColor": ""
              }
    _cameras = []

    def resolveArguments(self, arguments):
        cams = arguments.get("cameras")
        valid = []
        for i in cams:
            if i.exists():
                valid.append(i)
        return {"cameras": valid}

    def doIt(self, cameras=None):
        _cameras = [None] * len(cameras)
        for i, cam in enumerate(cameras):
            _cameras[i] = utils.bakeCameraMeatAnimToClone(cameras[i])
        self._cameras = _cameras
        return _cameras

    def undoIt(self):
        for cam in self._cameras:
            if cam is not None and cam.exists():
                cam.delete()
            return True
        return False
