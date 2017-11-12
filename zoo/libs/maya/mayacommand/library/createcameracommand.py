from zoo.libs.command import command

from zoo.libs.maya.cameras import utils


class CreateCameraCommand(command.ZooCommand):
    """This command Create a standard camera and adds the node as a MetaCamera
    """
    id = "zoo.meta.camera.create"
    creator = "David Sparrow"
    isUndoable = True
    uiData = {"icon": "camera",
              "tooltip": "Create camera",
              "label": "Create Camera",
              "color": "",
              "backgroundColor": ""
              }
    _meta = None

    def resolveArguments(self, arguments):
        name = arguments.get("name")
        if not name:
            self.cancel("Please provide a name")

        return arguments

    def doIt(self, name="", start=0, end=1, focalLength=35.000, horizontalFilmAperture=54.43,
             shotId=0, preset=None, aspectRatio=1.78, lockedOff=False, framePadding=10, frameRate=30):
        """

        :param name:
        :type name:
        :param start:
        :type start:
        :param end:
        :type end:
        :param focalLength:
        :type focalLength:
        :param horizontalFilmAperture:
        :type horizontalFilmAperture:
        :param shotId: the shotId value, could be from a database
        :type shotId: int
        :param preset: the camera lens preset
        :type preset: str
        :param aspectRatio: the camera aspectRatio
        :type aspectRatio: float
        :param lockedOff: is this camera production locked
        :type lockedOff:  bool
        :param frameRate: the FPS value
        :type frameRate: int or float
        :param framePadding: the frame padding setting
        :type framePadding: int
        :return:
        :rtype:
        """
        self._meta = utils.createCamera(name, start, end, focalLength, horizontalFilmAperture)
        self._meta.shotId = shotId
        self._meta.preset = preset or ""
        self._meta.aspectRatio = aspectRatio
        self._meta.lockedOff = lockedOff
        self._meta.framePadding = framePadding
        self._meta.frameRate = float(frameRate)
        return self._meta

    def undoIt(self):
        if self._meta is not None and self._meta.exists():
            self._meta.delete()
            return True
        return False

