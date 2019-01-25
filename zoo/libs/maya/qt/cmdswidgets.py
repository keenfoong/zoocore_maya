from functools import partial

from qt import QtWidgets, QtGui

from zoo.libs.pyqt import utils
from zoo.libs.utils import colour
import maya.cmds as cmds
import maya.OpenMayaUI as mui
import shiboken2


class ThemeInputWidget(QtWidgets.QWidget):

    def __init__(self, key=None, parent=None):
        """ A generic input widget for the themes in preferences

        :param key: The stylesheet pref key eg. "FRAMELESS_TITLELABEL_COLOR"
        :param parent:
        """
        super(ThemeInputWidget, self).__init__(parent=parent)

        self.key = key

    def data(self):
        pass


class ColorCmdsWidget(ThemeInputWidget):
    """Adds a maya color picker to a pyside colored button. With cmds.colorEditor
    This color picker locks Maya until the mini window or window is closed, then it updates.  WOuld be great if it
    did it on click rather than on close window.
    It's probably preferable to use a cmds.colorSliderGrp, however it is not working yet, see other classes
    cmds.colorSliderGrp will update on any click of the color UI, not only on close
    # todo: should make double click open the full (not mini) color picker.

    """
    def __init__(self, text="", key=None, color=(255, 255, 255), parent=None, toolTip="", labelRatio=1, btnRatio=1,
                 setFixedWidth=50, spacing=5):
        """Adds a maya color picker to a pyside label and colored button. Uses cmds.colorEditor which locks Maya

        :param text: label name
        :type text: str
        :param key: The stylesheet pref key eg. "FRAMELESS_TITLELABEL_COLOR"
        :type key: basestring
        :param color: the start color of the color button in rbg 255 (255, 255, 255)
        :type color: tuple
        :param parent: the parent widegt
        :type parent: QtWidget
        :param toolTip: the tooltip on hover
        :type toolTip: str
        :param labelRatio: the width column ratio of the label/button corresponds to the ratios of labelRatio/btnRatio
        :type labelRatio: int
        :param btnRatio: the width column ratio of the label/button corresponds to the ratios of labelRatio/btnRatio
        :type btnRatio: int
        :param setFixedWidth: set the width of the color button in pixels, dpi handled
        :type setFixedWidth: int
        :param spacing: the spacing size between the label and the button in pixels, dpi handled
        :type spacing: int
        """
        super(ColorCmdsWidget, self).__init__(parent=parent, key=key)
        self.color = None
        self.colorPicker = QtWidgets.QPushButton(parent=self)
        self.color = color
        if text:
            self.label = QtWidgets.QLabel(parent=self, text=text)
        layout = utils.hBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setColor(self.color)
        if setFixedWidth:
            self.colorPicker.setFixedWidth(utils.dpiScale(setFixedWidth))
        self.colorPicker.setToolTip(toolTip)
        if text:
            layout.addWidget(self.label, labelRatio)
            self.label.setToolTip(toolTip)
            layout.addSpacing(utils.dpiScale(spacing))
        layout.addWidget(self.colorPicker, btnRatio)
        self.setLayout(layout)
        self.connections()

    def connections(self):
        self.colorPicker.clicked.connect(lambda: self.colorConnected(self.colorPicker))

    def colorConnected(self, widget):
        # todo: the window position should compensate if on the edge of the screen.
        pos = QtGui.QCursor.pos()
        rgb = colour.rgbIntToFloat(self.color)
        posX = pos.x() + utils.dpiScale(-220)
        posY = pos.y() + utils.dpiScale(-130)
        linearColorResult = cmds.colorEditor(mini=True, position=[posX, posY], rgbValue=rgb[:3])
        linearColorResult = linearColorResult.strip().replace("  ", " ").split(" ")
        linearColorResult = [float(i) for i in linearColorResult]
        rgbColorResult = colour.convertColorLinearToSrgb(linearColorResult)  # color is 0-1 float style
        self.setColor(colour.rgbFloatToInt(rgbColorResult))  # expects 255 color style

    def colorConnectedDoubleClick(self, widget):
        # todo: add to button under double click, this version differs in the mini=False cmds flag
        pos = QtGui.QCursor.pos()
        rgb = colour.rgbIntToFloat(self.color)
        posX = pos.x() + utils.dpiScale(-220)
        posY = pos.y() + utils.dpiScale(-130)
        linearColorResult = cmds.colorEditor(mini=False, position=[posX, posY], rgbValue=rgb[:3])
        linearColorResult = linearColorResult.strip().replace("  ", " ").split(" ")
        linearColorResult = [float(i) for i in linearColorResult]
        rgbColorResult = colour.convertColorLinearToSrgb(linearColorResult)  # color is 0-1 float style
        self.setColor(colour.rgbFloatToInt(rgbColorResult))  # expects 255 color style

    def setColor(self, color):
        # self.colorPicker.setStyleSheet("background-color: rgb{}; border: 0px solid darkgrey; border-radius: 0px".format(color))
        self.colorPicker.setStyleSheet("QPushButton {0} background-color: rgb{2} {1}".format("{", "}", color))
        self.color = color

    def data(self):
        col = colour.RGBToHex(self.color)

        return {self.key: col}


def cmdsColorSlider(color=(0, 0, 1), parent=None, slider=False):
    """Not Working!!
    Based on Example code from http://blog.virtualmethodstudio.com/2017/03/embed-maya-native-ui-objects-in-pyside2/

    """
    # We have our Qt Layout where we want to insert, say, a Maya viewport
    colorSliderLayout = QtWidgets.QVBoxLayout(parent)
    # We set a qt object name for this layout.
    colorSliderLayout.setObjectName('colorSliderLayout22')

    # We set the given layout as parent to carry on creating Maya UI using Maya.cmds and create the paneLayout under it.
    layout = mui.MQtUtil.fullName(long(shiboken2.getCppPointer(colorSliderLayout)[0]))  # gets the full path as str
    # todo: issue is here, can't find the layout name with Zoo UIs
    print "full layout name", layout
    cmds.setParent(layout)
    colorSliderCmds = cmds.colorSliderGrp(label='', rgb=color, columnWidth3=(0, 60, 0))
    # Find a pointer to the colorSliderCmds that we just created using Maya API
    ptr = mui.MQtUtil.findControl(colorSliderCmds)
    # Wrap the pointer into a python QObject. Note that with PyQt QObject is needed. In Shiboken we use QWidget.
    colorSliderCmdsLayoutQt = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)
    # Now that we have a QtWidget, we add it to our Qt layout
    colorSliderLayout.addWidget(colorSliderCmdsLayoutQt)
    return colorSliderLayout


def mayaWindowInQT(parent):
    """ Not working yet!

    :param parent:
    :type parent:
    :return:
    :rtype:
    """
    verticalLayout = QtWidgets.QVBoxLayout(parent)
    verticalLayout.setContentsMargins(0, 0, 0, 0)

    # need to set a name so it can be referenced by maya node path
    verticalLayout.setObjectName("mainLayout")

    # First use SIP to unwrap the layout into a pointer
    # Then get the full path to the UI in maya as a string
    layout = mui.MQtUtil.fullName(long(shiboken2.getCppPointer(verticalLayout)[0]))
    cmds.setParent(layout)

    paneLayoutName = cmds.paneLayout()

    # Find a pointer to the paneLayout that we just created
    ptr = mui.MQtUtil.findControl(paneLayoutName)

    # Wrap the pointer into a python QObject
    paneLayout = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)

    cameraName = cmds.camera()[0]
    modelPanelName = cmds.modelPanel("customModelPanelXX", label="ModelPanel Test 22", cam=cameraName)

    # Find a pointer to the modelPanel that we just created
    ptr = mui.MQtUtil.findControl(modelPanelName)

    # Wrap the pointer into a python QObject
    modelPanel = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)

    # add our QObject reference to the paneLayout to our layout
    verticalLayout.addWidget(paneLayout)
    return verticalLayout


def EmbedMayaColorSliderWindowExample():
    """ test code!!
    Based on Example code from http://blog.virtualmethodstudio.com/2017/03/embed-maya-native-ui-objects-in-pyside2/

    """
    # We create a simple window with a QWidget
    window = QtWidgets.QWidget()
    window.resize(100, 100)
    # We have our Qt Layout where we want to insert, say, a Maya viewport
    qtLayout = QtWidgets.QVBoxLayout(window)
    # We set a qt object name for this layout.
    qtLayout.setObjectName('viewportLayout')

    # We set the given layout as parent to carry on creating Maya UI using Maya.cmds and create the paneLayout under it.
    cmds.setParent('viewportLayout')

    colorSliderCmds = cmds.colorSliderGrp(label='Blue', rgb=(0, 0, 1))
    cmds.colorSliderGrp(colorSliderCmds, edit=True, columnWidth3=(0, 60, 0),
                        cc=partial(printColor, colorSliderCmds))

    # Create the model panel. I use # to generate a new panel with no conflicting name
    # modelPanelName = cmds.modelPanel("embeddedModelPanel#", cam='persp')

    # Find a pointer to the colorSliderCmds that we just created using Maya API
    ptr = mui.MQtUtil.findControl(colorSliderCmds)

    # Wrap the pointer into a python QObject. Note that with PyQt QObject is needed. In Shiboken we use QWidget.
    colorSliderCmdsLayoutQt = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)

    # Now that we have a QtWidget, we add it to our Qt layout
    qtLayout.addWidget(colorSliderCmdsLayoutQt)

    window.show()


def printColor(myColorSlider, *args):
    """ test code"""
    colorValue = cmds.colorSliderGrp(myColorSlider, q=True, rgb=True)
    print colorValue


