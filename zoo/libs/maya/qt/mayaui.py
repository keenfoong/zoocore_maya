from qt import QtWidgets, QtCore, QtGui

try:
    from shiboken2 import wrapInstance as wrapinstance, getCppPointer
except:
    from shiboken import wrapInstance as wrapinstance
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMayaUI as apiUI

from maya import cmds

mixinWorkspaceControls = dict()


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


def toQtObject(mayaName, widgetType=QtWidgets.QWidget):
    """Convert a Maya ui path to a Qt object.

    :param mayaName: Maya UI Path to convert, "scriptEditorPanel1Window|TearOffPane|scriptEditorPanel1|testButton"
    :return: PyQt representation of that object
    """
    ptr = apiUI.MQtUtil.findControl(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findLayout(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findMenuItem(mayaName)

    if ptr is not None:
        return wrapinstance(long(ptr), widgetType)


def getOutliners():
    return [toQtObject(i) for i in cmds.getPanel(typ="outlinerPanel")]

def applyScriptEditorHistorySyntax(sourceType, highlighter=None, **kwargs):
    se_edit, seRepo = highlighterEditorWidget(sourceType, **kwargs)
    se_edit.setVisible(False)
    if highlighter is None:
        highlighter = se_edit.findChild(QtGui.QSyntaxHighlighter)
    highlighter.setDocument(seRepo.document())

def highlighterEditorWidget(sourceType, **kwargs):
    se_repo = toQtObject('cmdScrollFieldReporter1', widgetType=QtWidgets.QTextEdit)
    tmp = cmds.cmdScrollFieldExecuter(sourceType=sourceType, **kwargs)
    se_edit = toQtObject(tmp, widgetType=QtWidgets.QTextEdit)
    se_edit.nativeParentWidget()
    return se_edit, se_repo


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

    .. code-block:: python

        setChannelBoxAtTop("mainChannelBox",True)
    """
    cmds.channelBox(channelBox, edit=True, containerAtTop=value)


def setChannelShowType(channelBox, value):
    """
    :param channelBox: mainChannelBox
    :type channelBox: str
    :param value:
    :type value: str

    .. code-block:: python

        setChannelShowType("mainChannelBox", "all")
    """
    cmds.optionVar(stringValue=("cbShowType", value))
    cmds.channelBox(channelBox, edit=True, update=True)


# global to store the bootstrap maya widgets, {widgetuuid: :class:`BootStapWidget`}
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

    .. code-block:: python

        customWidget = QtWidget()
        boostrap = BootStrapWidget(customWidget, "customWidget")
        boostrap.show(dockable=True, retain=False, width=size.width(), widthSizingProperty='preferred',
                     minWidth=minSize.width(),
                     height=size.height(), x=250, y=200)

    """
    width = cmds.optionVar(query='workspacesWidePanelInitialWidth') * 0.75
    INITIAL_SIZE = QtCore.QSize(width, 600)
    PREFERRED_SIZE = QtCore.QSize(width, 420)
    MINIMUM_SIZE = QtCore.QSize((width * 0.95), 220)

    def __del__(self, *args, **kwargs):
        """Overriding to do nothing due to autodesk's implemention causing an internal error (c++ object already deleted),
        since they try to destroy the workspace after its QObject has already been deleted , thanks guys!!!
        """
        pass

    def __init__(self, widget, title, uid=None, parent=None):

        # maya internals workouts the parent if None
        super(BootStrapWidget, self).__init__(parent=parent)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.preferredSize = self.PREFERRED_SIZE
        # bind this instance globally so the maya callback can talk to it
        global BOOT_STRAPPED_WIDGETS
        uid = uid or title
        self.setObjectName(uid)
        BOOT_STRAPPED_WIDGETS[uid] = self

        self.setWindowTitle(title)
        # create a QMainWindow frame that other windows can dock into.
        self.dockingFrame = QtWidgets.QMainWindow(self)
        self.dockingFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.dockingFrame.setWindowFlags(QtCore.Qt.Widget)
        self.dockingFrame.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks)

        self.centralWidget = widget
        self.dockingFrame.setCentralWidget(self.centralWidget)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.dockingFrame, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        widget.setProperty('bootstrapWidget', self)

    def setSizeHint(self, size):
        self.preferredSize = size

    def close(self, *args, **kwargs):
        """Overridden to call the bootstrap user widget.close()
        """
        self.centralWidget.close()
        super(BootStrapWidget, self).close(*args, **kwargs)

    def show(self, **kwargs):
        name = self.objectName()
        name = name + "WorkspaceControl"
        if cmds.workspaceControl(name, query=True, exists=True):
            cmds.deleteUI(name)
            cmds.workspaceControlState(name, remove=True)
        kwargs["retain"] = False
        # create the ui script which launches the custom widget, autodesk decided that string are god eeekkkkk!
        kwargs["uiScript"] = "try: import zoo.libs.maya.qt.mayaui as zoomayaui;zoomayaui.rebuild({})\nexcept ImportError: pass".format(self.objectName())

        # create the close callback string autodesk wacky design decisions again
        kwargs["closeCallback"] = 'try: import zoo.libs.maya.qt.mayaui as zoomayaui;zoomayaui.bootstrapDestroyWindow("{}")\nexcept ImportError: pass'.format(self.objectName())
        #super(BootStrapWidget, self).show(**kwargs)

        self.dockableShow(**kwargs)

    def dockableShow(self, *args, **kwargs):
        """ Copied from mayaMixin.MayaQWidgetDockableMixin().show() so we can tweak the docking settings.

        """
        # Update the dockable parameters first (if supplied)
        if len(args) or len(kwargs):
            self.setDockableParameters(*args, **kwargs)
        elif self.parent() is None:
            # Set parent to Maya main window if parent=None and no dockable parameters provided
            self._makeMayaStandaloneWindow()

        # Handle the standard setVisible() operation of show()
        QtWidgets.QWidget.setVisible(self,
                           True)  # NOTE: Explicitly calling QWidget.setVisible() as using super() breaks in PySide: super(self.__class__, self).show()

        # Handle special case if the parent is a QDockWidget (dockControl)
        print kwargs
        parent = self.parent()
        if parent:
            parentName = parent.objectName()
            if parentName and len(parentName) and cmds.workspaceControl(parentName, q=True, exists=True):
                print (parentName)
                if cmds.workspaceControl(parentName, q=True, visible=True):
                    print ("visible")
                    cmds.workspaceControl(parentName, e=True, restore=True)
                else:
                    print ("invisible")
                    if kwargs['dockable']:
                        print ("dockable")
                        script= """
from qt import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance as wrapinstance
workspaceControlPtr = apiUI.MQtUtil.getCurrentParent()
mw = wrapinstance(long(workspaceControlPtr), QtWidgets.QMainWindow)
mw.setAttribute(QtCore.Qt.WA_TranslucentBackground)
mw.setWindowFlags(mw.windowFlags() | QtCore.Qt.FramelessWindowHint)                        
                        """
                        cmds.workspaceControl(parentName, e=True, loadImmediately=True, uiScript=script, visible=True)


                    else:
                        # Create our own so we can have our own transparent background
                        ptr = apiUI.MQtUtil.getCurrentParent()
                        mw = wrapinstance(long(ptr), QtWidgets.QMainWindow)
                        mw.show()

    def setDockableParameters(self, dockable=None, floating=None, area=None, allowedArea=None, width=None,
                              widthSizingProperty=None, minWidth=None, height=None, heightSizingProperty=None,
                              x=None, y=None, retain=True, plugins=None, controls=None, uiScript=None,
                              closeCallback=None, *args, **kwargs):
        '''
        Set the dockable parameters.

        :Parameters:
            dockable (bool)
                Specify if the window is dockable (default=False)
            floating (bool)
                Should the window be floating or docked (default=True)
            area (string)
                Default area to dock into (default='left')
                Options: 'top', 'left', 'right', 'bottom'
            allowedArea (string)
                Allowed dock areas (default='all')
                Options: 'top', 'left', 'right', 'bottom', 'all'
            width (int)
                Width of the window
            height (int)
                Height of the window
            x (int)
                left edge of the window
            y (int)
                top edge of the window

        :See: show(), hide(), and setVisible()
        '''
        print "Dockable show"
        if ((dockable == True) or (dockable is None and self.isDockable())):  # == Handle docked window ==
            # By default, when making dockable, make it floating
            #   This addresses an issue on Windows with the window decorators not showing up.
            if floating is None and area is None:
                floating = True

            # Create workspaceControl if needed
            if dockable == True and not self.isDockable():
                # Retrieve original position and size
                # Position
                if x is None:
                    x = self.x()
                    # Give suitable default value if null
                    if x == 0:
                        x = 250
                if y is None:
                    y = self.y()
                    # Give suitable default value if null
                    if y == 0:
                        y = 200
                # Size
                unininitializedSize = QtCore.QSize(640, 480)  # Hardcode: (640,480) is the default size for a QWidget
                if self.size() == unininitializedSize:
                    # Get size from widget sizeHint if size not yet initialized (before the first show())
                    widgetSizeHint = self.sizeHint()
                else:
                    widgetSizeHint = self.size()  # use the current size of the widget
                if width is None:
                    width = widgetSizeHint.width()
                if height is None:
                    height = widgetSizeHint.height()
                if widthSizingProperty is None:
                    widthSizingProperty = 'free'
                if heightSizingProperty is None:
                    heightSizingProperty = 'free'

                if controls is None:
                    controls = []
                if plugins is None:
                    plugins = []

                workspaceControlName = self.objectName() + 'WorkspaceControl'
                # Set to floating if requested or if no docking area given
                if floating == True or area is None:
                    print ("begin")
                    if minWidth is None:
                        script = """
print( "dockable show")
from qt import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance as wrapinstance
workspaceControlPtr = apiUI.MQtUtil.getCurrentParent()
mw = wrapinstance(long(workspaceControlPtr), QtWidgets.QMainWindow)
mw.setAttribute(QtCore.Qt.WA_TranslucentBackground)
mw.setWindowFlags(mw.windowFlags() | QtCore.Qt.FramelessWindowHint)"""

                        workspaceControlName = cmds.workspaceControl(workspaceControlName, label=self.windowTitle(),
                                                                     retain=retain, loadImmediately=True,
                                                                     floating=True, initialWidth=width,
                                                                     widthProperty=widthSizingProperty,
                                                                     initialHeight=height,
                                                                     heightProperty=heightSizingProperty,
                                                                     requiredPlugin=plugins,
                                                                     requiredControl=controls,
                                                                     uiScript=script,
                                                                     vis=False)



                    else:
                        workspaceControlName = cmds.workspaceControl(workspaceControlName, label=self.windowTitle(),
                                                                     retain=retain, loadImmediately=True,
                                                                     floating=True, initialWidth=width,
                                                                     widthProperty=widthSizingProperty,
                                                                     minimumWidth=minWidth, initialHeight=height,
                                                                     heightProperty=heightSizingProperty,
                                                                     requiredPlugin=plugins,
                                                                     requiredControl=controls)

                else:
                    if self.parent() is None or (
                        long(getCppPointer(self.parent())[0]) == long(apiUI.MQtUtil.mainWindow())):
                        # If parented to the Maya main window or nothing, dock into the Maya main window
                        if minWidth is None:
                            workspaceControlName = cmds.workspaceControl(workspaceControlName,
                                                                         label=self.windowTitle(), retain=retain,
                                                                         loadImmediately=True,
                                                                         dockToMainWindow=(area, False),
                                                                         initialWidth=width,
                                                                         widthProperty=widthSizingProperty,
                                                                         initialHeight=height,
                                                                         heightProperty=heightSizingProperty,
                                                                         requiredPlugin=plugins,
                                                                         requiredControl=controls)
                            print ("5")
                        else:
                            workspaceControlName = cmds.workspaceControl(workspaceControlName,
                                                                         label=self.windowTitle(), retain=retain,
                                                                         loadImmediately=True,
                                                                         dockToMainWindow=(area, False),
                                                                         initialWidth=width,
                                                                         widthProperty=widthSizingProperty,
                                                                         minimumWidth=minWidth,
                                                                         initialHeight=height,
                                                                         heightProperty=heightSizingProperty,
                                                                         requiredPlugin=plugins,
                                                                         requiredControl=controls)
                    else:
                        # Otherwise, the parent should be within a workspace control - need to go up the hierarchy to find it
                        foundParentWorkspaceControl = False
                        nextParent = self.parent()
                        while nextParent is not None:
                            dockToWorkspaceControlName = nextParent.objectName()
                            if cmds.workspaceControl(dockToWorkspaceControlName, q=True, exists=True):
                                if minWidth is None:
                                    workspaceControlName = cmds.workspaceControl(workspaceControlName,
                                                                                 label=self.windowTitle(),
                                                                                 retain=retain,
                                                                                 loadImmediately=True,
                                                                                 dockToControl=(
                                                                                 dockToWorkspaceControlName, area),
                                                                                 initialWidth=width,
                                                                                 widthProperty=widthSizingProperty,
                                                                                 initialHeight=height,
                                                                                 heightProperty=heightSizingProperty,
                                                                                 requiredPlugin=plugins,
                                                                                 requiredControl=controls)
                                else:
                                    workspaceControlName = cmds.workspaceControl(workspaceControlName,
                                                                                 label=self.windowTitle(),
                                                                                 retain=retain,
                                                                                 loadImmediately=True,
                                                                                 dockToControl=(
                                                                                 dockToWorkspaceControlName, area),
                                                                                 initialWidth=width,
                                                                                 widthProperty=widthSizingProperty,
                                                                                 minimumWidth=minWidth,
                                                                                 initialHeight=height,
                                                                                 heightProperty=heightSizingProperty,
                                                                                 requiredPlugin=plugins,
                                                                                 requiredControl=controls)
                                foundParentWorkspaceControl = True
                                break
                            else:
                                nextParent = nextParent.parent()

                        if foundParentWorkspaceControl == False:
                            # If parent workspace control cannot be found, just make the workspace control a floating window
                            if minWidth is None:
                                workspaceControlName = cmds.workspaceControl(workspaceControlName,
                                                                             label=self.windowTitle(),
                                                                             retain=retain, loadImmediately=True,
                                                                             floating=True, initialWidth=width,
                                                                             widthProperty=widthSizingProperty,
                                                                             initialHeight=height,
                                                                             heightProperty=heightSizingProperty,
                                                                             requiredPlugin=plugins,
                                                                             requiredControl=controls)
                            else:
                                workspaceControlName = cmds.workspaceControl(workspaceControlName,
                                                                             label=self.windowTitle(),
                                                                             retain=retain, loadImmediately=True,
                                                                             floating=True, initialWidth=width,
                                                                             widthProperty=widthSizingProperty,
                                                                             minimumWidth=minWidth,
                                                                             initialHeight=height,
                                                                             heightProperty=heightSizingProperty,
                                                                             requiredPlugin=plugins,
                                                                             requiredControl=controls)

                currParent = apiUI.MQtUtil.getCurrentParent()
                mixinPtr = apiUI.MQtUtil.findControl(self.objectName())
                apiUI.MQtUtil.addWidgetToMayaLayout(long(mixinPtr), long(currParent))

                if uiScript is not None and len(uiScript):
                    cmds.workspaceControl(workspaceControlName, e=True, uiScript=uiScript)

                if closeCallback is not None:
                    cmds.workspaceControl(workspaceControlName, e=True, closeCommand=closeCallback)

                # Add this control to the list of controls created in Python
                global mixinWorkspaceControls
                mixinWorkspaceControls[workspaceControlName] = self

                # Hook up signals
                # dockWidget.topLevelChanged.connect(self.floatingChanged)
                # dockWidget.closeEventTriggered.connect(self.dockCloseEventTriggered)

        else:  # == Handle Standalone Window ==
            # Make standalone as needed
            if not dockable and self.isDockable():
                # Retrieve original position and size
                dockPos = self.parent().pos()
                if x == None:
                    x = dockPos.x()
                if y == None:
                    y = dockPos.y()
                if width == None:
                    width = self.width()
                if height is None:
                    height = self.height()
                # Turn into a standalone window and reposition
                currentVisibility = self.isVisible()
                self._makeMayaStandaloneWindow()  # Set the parent back to Maya and remove the parent dock widget
                self.setVisible(currentVisibility)

            # Handle position and sizing
            if (width != None) or (height != None):
                if width == None:
                    width = self.width()
                if height == None:
                    height = self.height()
                self.resize(width, height)
            if (x != None) or (y != None):
                if x is None:
                    x = self.x()
                if y == None:
                    y = self.y()
                self.move(x, y)



