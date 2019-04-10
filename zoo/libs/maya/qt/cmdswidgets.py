from qt import QtCore, QtWidgets, QtGui

from zoo.libs.pyqt import utils
from zoo.libs.utils import colour
import maya.cmds as cmds


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
    This color picker locks Maya until the mini window or window is closed, then it updates.  Would be great if it
    did it on click rather than on close window.
    It's probably preferable to use a cmds.colorSliderGrp, however it is not working yet, see other classes
    cmds.colorSliderGrp will update on any click of the color UI, not only on close
    # todo: should make double click open the full (not mini) color picker.
    """
    colorChanged = QtCore.Signal()
    colorClicked = QtCore.Signal()

    def __init__(self, text="", key=None, color=(255, 255, 255), parent=None, toolTip="", labelRatio=1, btnRatio=1,
                 setFixedWidth=50, spacing=5):
        """Adds a maya color picker to a pyside label and colored button. Uses cmds.colorEditor which locks Maya

        :param text: label name
        :type text: str
        :param key: The stylesheet pref key eg. "FRAMELESS_TITLELABEL_COLOR"
        :type key: basestring
        :param color: the start color of the color button in rbg 255 (255, 255, 255) Color is srgb not linear
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
        self.disableState = False
        self.color = None
        self.colorPicker = QtWidgets.QPushButton(parent=self)
        self.color = color
        if text:
            self.label = QtWidgets.QLabel(parent=self, text=text)
        else:
            self.label = None
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

    def text(self):
        """returns the label name as a string

        :return labelName: the text name of the label
        :rtype labelName: str
        """
        if self.label:
            return self.label.text()
        return ""

    def connections(self):
        self.colorPicker.clicked.connect(lambda: self.colorConnected(self.colorPicker))

    def setDisabled(self, state):
        """Disable the label text (make it grey)"""
        self.label.setDisabled(state)
        self.disableState = state

    def colorConnected(self, widget):
        # todo: the window position should compensate if on the edge of the screen.
        self.colorClicked.emit()
        if self.disableState:
            return
        pos = QtGui.QCursor.pos()
        srgb = colour.rgbIntToFloat(self.color)
        linearRgb = colour.convertColorSrgbToLinear(srgb)
        posX = pos.x() + utils.dpiScale(-220)
        posY = pos.y() + utils.dpiScale(-130)
        linearColorResult = cmds.colorEditor(mini=True, position=[posX, posY], rgbValue=linearRgb[:3])
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
        linearColorResult = map(float, linearColorResult)
        rgbColorResult = colour.convertColorLinearToSrgb(linearColorResult)  # color is 0-1 float style
        self.setColor(colour.rgbFloatToInt(rgbColorResult))  # expects 255 color style

    def setColor(self, color):
        """Sets color, requires rgb color 255"""
        # todo: stylesheet add border options
        # self.colorPicker.setStyleSheet("background-color: rgb{}; border: 0px solid darkgrey;
        # border-radius: 0px".format(color))
        self.color = colour.rgbIntRound(color)
        self.colorPicker.setStyleSheet("QPushButton {0} background-color: rgb{2} {1}".format("{", "}", self.color))
        self.colorChanged.emit()

    def setColorFloat(self, rgbList):
        """Sets the color of the button as per a rgb list in 0-1 range

        :param rgbList: r g b color in 0-1.0 range eg [1.0, 0.0, 0.0]
        :type rgbList: list
        """
        return self.setColor(colour.rgbFloatToInt(rgbList))

    def rgbColor(self):
        """returns rgb tuple with 0-255 ranges Eg (128, 255, 12)
        """
        return self.color

    def rgbColorFloat(self):
        """returns rgb tuple with 0-1.0 float ranges Eg (1.0, .5, .6666)
        """
        return tuple(float(i) / 255 for i in self.color)

    def hexColor(self):
        """Returns hex color (6 letters) of the current color"""
        return colour.hexToRGB(self.color)

    def data(self):
        col = colour.RGBToHex(self.color)

        return {self.key: col}
