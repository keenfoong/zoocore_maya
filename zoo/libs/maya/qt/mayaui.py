from qt import QtWidgets, QtCore

try:
    from shiboken2 import wrapInstance as wrapinstance
except:
    from shiboken import wrapInstance as wrapinstance
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMayaUI as apiUI
from maya import cmds


def dpiScale(value):
    """Get the appropriate QSize based on maya's current dpi setting

    :param value:
    :type value: int or float
    :return:
    :rtype: int
    """
    return apiUI.MQtUtil.dpiScale(value)


def sizeByDpi(size):
    """Scales the QSize by the current dpi scaling from maya.

    :param size: The QSize to Scale by the dpi setting from maya
    :type size: QSize
    :return: The newly scaled QSize
    :rtype: QSize
    """
    return QtCore.QSize(dpiScale(size.width()), dpiScale(size.height()))


def getMayaWindow():
    """
    :return: instance, the mainWindow ptr as a QmainWindow widget
    """
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapinstance(long(ptr), QtWidgets.QMainWindow)


def mayaViewport():
    """Returns the currently active maya viewport as a widget
    :return:
    :rtype:
    """
    widget = apiUI.M3dView.active3dView().widget()
    widget = wrapinstance(long(widget), QtWidgets.QWidget)
    return widget


def fullName(widget):
    return apiUI.MQtUtil.fullName(long(widget))


def getMayaWindowName():
    """Returns the maya window objectName from QT
    :return:
    """
    return getMayaWindow().objectName()


def toQtObject(mayaName):
    """Convert a Maya ui path to a Qt object.

    :param mayaName: Maya UI Path to convert
        (Ex: "scriptEditorPanel1Window|TearOffPane|scriptEditorPanel1|testButton" )
    :return: PyQt representation of that object
    """
    ptr = apiUI.MQtUtil.findControl(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findLayout(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findMenuItem(mayaName)

    if ptr is not None:
        return wrapinstance(long(ptr), QtWidgets.QWidget)


def getOutliners():
    return [toQtObject(i) for i in cmds.getPanel(typ="outlinerPanel")]


def suppressOutput():
    """Supresses all output to the script editor
    """
    cmds.scriptEditorInfo(e=True,
                          suppressResults=True,
                          suppressErrors=True,
                          suppressWarnings=True,
                          suppressInfo=True)


def restoreOutput():
    """Restores the script editor to include all results
    """
    cmds.scriptEditorInfo(e=True,
                          suppressResults=False,
                          suppressErrors=False,
                          suppressWarnings=False,
                          suppressInfo=False)


def setChannelBoxAtTop(channelBox, value):
    """
    :param channelBox: mainChannelBox
    :type channelBox: str
    :param value:
    :type value: bool
    :example::
        setChannelBoxAtTop("mainChannelBox",True)
    """
    cmds.channelBox(channelBox, edit=True, containerAtTop=value)


def setChannelShowType(channelBox, value):
    """
    :param channelBox: mainChannelBox
    :type channelBox: str
    :param value:
    :type value: str
    :example::
        setChannelShowType("mainChannelBox", "all")
    """
    cmds.optionVar(stringValue=("cbShowType", value))
    cmds.channelBox(channelBox, edit=True, update=True)


# global to store the bootstrap maya widgets, {widgetuuid: ::class:`BootStapWidget`}
# we use this to restore or close the bootstrap widgets
BOOT_STRAPPED_WIDGETS = {}


def rebuild(objectName):
    """If the bootstrap widget exists then we reapply it to mayas layout, otherwise do nothing.

    :param objectName: the bootStrap objectName
    :type objectName: str
    """
    global BOOT_STRAPPED_WIDGETS
    wid = BOOT_STRAPPED_WIDGETS.get(objectName)
    if wid is None:
        return False
    parent = apiUI.MQtUtil.getCurrentParent()
    mixinPtr = apiUI.MQtUtil.findControl(wid.objectName())
    apiUI.MQtUtil.addWidgetToMayaLayout(long(mixinPtr), long(parent))
    return True


def bootstrapDestroyWindow(objectName):
    """Function to destroy a bootstrapped widget, this use the maya workspaceControl objectName

    :param objectName: The bootstrap Widget objectName
    :type objectName: str
    :rtype: bool
    """
    global BOOT_STRAPPED_WIDGETS
    wid = BOOT_STRAPPED_WIDGETS.get(objectName)

    if wid is not None:
        # wid.close()
        BOOT_STRAPPED_WIDGETS.pop(objectName)
        wid.close()
        return True
    return False


class BootStrapWidget(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """ Class to wrap mayas workspace dockable mixin into something useful,
    customWidget = QtWidget()
    boostrap = BootStrapWidget(customWidget, "customWidget")
    boostrap.show(dockable=True, retain=False, width=size.width(), widthSizingProperty='preferred',
                 minWidth=minSize.width(),
                 height=size.height(), x=250, y=200)

    """
    width = (cmds.optionVar(query='workspacesWidePanelInitialWidth')) * 0.75
    INITIAL_SIZE = QtCore.QSize(width, 600)
    PREFERRED_SIZE = QtCore.QSize(width, 420)
    MINIMUM_SIZE = QtCore.QSize((width * 0.95), 220)

    def __del__(self, *args, **kwargs):
        """Overriding to do nothing due to autodesk's implemention causing an internal error (c++ object already deleted),
        since they try to destroy the workspace after its QObject has already been deleted , thanks guys!!!
        """
        pass

    def __init__(self, widget, title, parent=None):

        # maya internals workouts the parent if None
        super(BootStrapWidget, self).__init__(parent=parent)
        self.preferredSize = self.PREFERRED_SIZE
        # bind this instance globally so the maya callback can talk to it
        global BOOT_STRAPPED_WIDGETS
        uid = "_".join([title, "WorkspaceControl"])
        self.setObjectName(uid)
        BOOT_STRAPPED_WIDGETS[uid] = self

        self.setWindowTitle(title)
        # create a QMainWindow frame that other windows can dock into.
        self.dockingFrame = QtWidgets.QMainWindow(self)
        self.dockingFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.dockingFrame.setWindowFlags(QtCore.Qt.Widget)
        self.dockingFrame.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks)

        self.centralWidget = widget
        widLayout = self.centralWidget.layout()
        if widLayout:
            widLayout.setContentsMargins(0, 0, 0, 0)
        self.dockingFrame.setCentralWidget(self.centralWidget)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.dockingFrame, 0)
        self.setLayout(layout)

    def setSizeHint(self, size):
        self.preferredSize = size

    def sizeHint(self):
        return self.preferredSize

    def minimumSizeHint(self):
        return self.MINIMUM_SIZE

    def close(self, *args, **kwargs):
        """Overridden to call the bootstrap user widget.close()
        """
        self.centralWidget.close()
        super(BootStrapWidget, self).close(*args, **kwargs)

    def show(self, **kwargs):
        if "widthSizingProperty" not in kwargs:
            kwargs["widthSizingProperty"] = 'free'
        if "heightProperty" not in kwargs:
            kwargs["heightProperty"] = 'free'
        kwargs["retain"] = False
        kwargs["uiScript"] = "import zoo.libs.maya.qt.mayaui as zoomayaui\nzoomayaui.rebuild({})".format(
            self.objectName())
        kwargs[
            "closeCallback"] = 'import zoo.libs.maya.qt.mayaui as zoomayaui\nzoomayaui.bootstrapDestroyWindow("{' \
                               '}")'.format(
            self.objectName())
        super(BootStrapWidget, self).show(**kwargs)

