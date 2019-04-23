from functools import partial
from shiboken2 import wrapInstance

from qt import QtCore, QtWidgets, QtGui

import maya.cmds as cmds
import maya.OpenMayaUI as om1

from zoo.libs.pyqt import utils
from zoo.libs.pyqt.widgets import layouts
from zoo.libs.utils import colour
from zoo.libs.pyqt.widgetspro import extendedbutton


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

    a menu can be added to this widget
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
        self._color = None
        self.colorPicker = extendedbutton.ExtendedButtonSimpleMenu(parent=self)
        self._color = color
        if text:
            self.label = layouts.Label(text, parent, toolTip=toolTip)  # supports menu
        else:
            self.label = None
        layout = layouts.hBoxLayout(self)
        self.setColorSrgbInt(self._color)
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
        srgb = colour.rgbIntToFloat(self._color)
        linearRgb = colour.convertColorSrgbToLinear(srgb)
        posX = pos.x() + utils.dpiScale(-220)
        posY = pos.y() + utils.dpiScale(-130)
        linearColorResult = cmds.colorEditor(mini=True, position=[posX, posY], rgbValue=linearRgb[:3])
        linearColorResult = linearColorResult.strip().replace("  ", " ").split(" ")
        linearColorResult = [float(i) for i in linearColorResult]
        rgbColorResult = colour.convertColorLinearToSrgb(linearColorResult)  # color is 0-1 float style
        self.setColorSrgbInt(colour.rgbFloatToInt(rgbColorResult))  # expects 255 color style

    def colorConnectedDoubleClick(self, widget):
        # todo: add to button under double click, this version differs in the mini=False cmds flag
        pos = QtGui.QCursor.pos()
        rgb = colour.rgbIntToFloat(self._color)
        posX = pos.x() + utils.dpiScale(-220)
        posY = pos.y() + utils.dpiScale(-130)
        linearColorResult = cmds.colorEditor(mini=False, position=[posX, posY], rgbValue=rgb[:3])
        linearColorResult = linearColorResult.strip().replace("  ", " ").split(" ")
        linearColorResult = map(float, linearColorResult)
        rgbColorResult = colour.convertColorLinearToSrgb(linearColorResult)  # color is 0-1 float style
        self.setColorSrgbInt(colour.rgbFloatToInt(rgbColorResult))  # expects 255 color style

    def setColorSrgbInt(self, color):
        """Sets color, requires rgb color 255"""
        # todo: stylesheet add border options
        # self.colorPicker.setStyleSheet("background-color: rgb{}; border: 0px solid darkgrey;
        # border-radius: 0px".format(color))
        self._color = colour.rgbIntRound(color)
        self.colorPicker.setStyleSheet("QPushButton {0} background-color: rgb{2} {1}".format("{", "}", self._color))
        self.colorChanged.emit()

    def setColorSrgbFloat(self, rgbList):
        """Sets the color of the button as per a rgb list in 0-1 range

        :param rgbList: r g b color in 0-1.0 range eg [1.0, 0.0, 0.0]
        :type rgbList: list
        """
        return self.setColorSrgbInt(colour.rgbFloatToInt(rgbList))

    def colorSrgbInt(self):
        """returns rgb tuple with 0-255 ranges Eg (128, 255, 12)
        """
        return self._color

    def colorSrgbFloat(self):
        """returns srgb tuple with 0-1.0 float ranges Eg (1.0, .5, .6666)
        """
        return tuple(float(i) / 255 for i in self._color)

    def hexColor(self):
        """Returns hex color (6 letters) of the current color"""
        return colour.hexToRGB(self._color)

    def data(self):
        col = colour.RGBToHex(self._color)

        return {self.key: col}

    # ----------
    # MENUS
    # ----------

    def setMenu(self, menu, modeList=None, mouseButton=QtCore.Qt.RightButton):
        """Add the left/middle/right click menu by passing in a QMenu

        If a modeList is passed in then create/reset the menu to the modeList:

            [("icon1", "menuName1"), ("icon2", "menuName2")]

        If no modelist the menu won't change

        :param menu: the Qt menu to show on middle click
        :type menu: QtWidgets.QMenu
        :param modeList: a list of menu modes (tuples) eg [("icon1", "menuName1"), ("icon2", "menuName2")]
        :type modeList: list(tuple(str))
        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        """
        if mouseButton != QtCore.Qt.LeftButton:  # don't create an edit menu if left mouse button menu
            self.colorPicker.setMenu(menu, mouseButton=mouseButton)
        # only add the action list (menu items) to the label, as the line edit uses the same menu
        self.label.setMenu(menu, modeList=modeList, mouseButton=mouseButton)

    def addActionList(self, modes, mouseButton=QtCore.Qt.RightButton):
        """resets the appropriate mouse click menu with the incoming modes

            modeList: [("icon1", "menuName1"), ("icon2", "menuName2"), ("icon3", "menuName3")]

        resets the lists and menus:

            self.menuIconList: ["icon1", "icon2", "icon3"]
            self.menuIconList: ["menuName1", "menuName2", "menuName3"]

        :param modes: a list of menu modes (tuples) eg [("icon1", "menuName1"), ("icon2", "menuName2")]
        :type modes: list(tuple(str))
        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        """
        # only add the action list (menu items) to the label, as the line edit uses the same menu
        if self.label:
            self.label.addActionList(modes, mouseButton=mouseButton)
        else:
            self.colorPicker.addActionList(modes, mouseButton=mouseButton)


class MayaColorSlider(QtWidgets.QWidget, layouts.MenuCreateClickMethods):
    colorChanged = QtCore.Signal(tuple)
    colorClicked = QtCore.Signal()  # not really needed

    def __init__(self, text="", color=(1, 1, 1), parent=None, colorWidth=120, colorHeight=22, toolTip="blah",
                 labelRatio=50, btnRatio=50, spacing=5):
        """Custom embedded cmds widget written Chris Zurbrigg see his tutorials http://zurbrigg.com/tutorials

        :param color:
        :type color:
        :param parent:
        :type parent:
        """
        super(MayaColorSlider, self).__init__(parent)
        self.setObjectName("CustomColorButton")
        self.btnRatio = btnRatio
        self.colorWidth = colorWidth
        # create widgets

        if text:
            self.label = layouts.Label(text, parent, toolTip=toolTip)  # supports menu
        else:
            self.label = None
        self.main_layout = layouts.hBoxLayout(self)

        if text:
            self.main_layout.addWidget(self.label, labelRatio)
            self.label.setToolTip(toolTip)
            self.main_layout.addSpacing(utils.dpiScale(spacing))

        self._createControl()  # creates self._color_widget which is the color picker and adds it to the layout
        self._color_widget.setToolTip(toolTip)
        # color widget setup
        self._colorLinear = color
        self._updateColor()

        if colorHeight:
            self.setHeight(colorHeight)

        self.setLayout(self.main_layout)

    def _createControl(self):
        """Creates the Maya color slider control, hides the slider and converts the widget so it can be Qt embedded

        Credit to Chris Zurbrigg see his tutorials http://zurbrigg.com/tutorials for solving various embed issues
        """

        # 1) Create the colorSliderGrp """
        window = cmds.window()
        # color_slider_name
        #  width=1 is the pixel width of the slider which is hidden,
        #  columnWidth specifies col 1 width from the kwargs
        color_slider_name = cmds.colorSliderGrp(width=1, columnWidth=[1, self.colorWidth])

        # 2) Find the colorSliderGrp widget
        self._color_slider_obj = om1.MQtUtil.findControl(color_slider_name)
        if self._color_slider_obj:
            self._color_slider_widget = wrapInstance(long(self._color_slider_obj), QtWidgets.QWidget)

            # 3) Reparent the colorSliderGrp widget to this widget
            self.main_layout.addWidget(self._color_slider_widget, self.btnRatio)

            # 4) Identify/store the colorSliderGrp's child widgets (and hide if necessary)
            self._slider_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "slider")
            if self._slider_widget:
                self._slider_widget.hide()

            self._color_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "port")
            cmds.colorSliderGrp(self._getFullName(), e=True, changeCommand=partial(self._onColorChanged))

        cmds.deleteUI(window, window=True)

    def _getFullName(self):
        return om1.MQtUtil.fullName(long(self._color_slider_obj))

    def _updateColor(self):
        """Updates the color on the color picker widget, usually Maya will perform this auto but Zoo stylesheeting
        causes issues so we overwrite the widget directly with self._color_widget.setStyleSheet()
        """
        colorSrgbFloat = colour.convertColorLinearToSrgb(self._colorLinear)
        colorSrgbInt = colour.rgbFloatToInt(colorSrgbFloat)
        cmds.colorSliderGrp(self._getFullName(), edit=True, rgbValue=(self._colorLinear[0],
                                                                      self._colorLinear[1],
                                                                      self._colorLinear[2]))
        self._color_widget.setStyleSheet("QLabel {} background-color: rgb{} {}".format("{", str(colorSrgbInt), "}"))

    def _onColorChanged(self, *args):
        """Gets the current color slider color and emits it
        """
        self._colorLinear = self.colorLinearFloat()
        self._updateColor()
        self.colorChanged.emit(self._colorLinear)
        self.colorClicked.emit()

    def setWidth(self, width):
        """sets the size of the color widget, dpi scale handled, will scale with cmds as pyside has issues overriding
        *Not Tested should work"""
        self.colorWidth = width
        cmds.colorSliderGrp(e=True, columnWidth=[1, self.colorWidth])

    def setHeight(self, height):
        """sets the size of the color widget, dpi scale handled"""
        self._color_widget.setFixedHeight(utils.dpiScale(height))
        self._color_slider_widget.setFixedHeight(utils.dpiScale(height))

    def setDisabled(self, disabled=True):
        # disables the color widget so it cannot be clicked
        enabled = not disabled
        cmds.colorSliderGrp(self._getFullName(), e=True, enable=enabled)
        self.label.setDisabled(disabled)

    def setEnabled(self, enabled=True):
        # enables the color widget so it can be clicked
        cmds.colorSliderGrp(self._getFullName(), e=True, enable=enabled)
        self.label.setDisabled(not enabled)

    def setDisabledLabel(self, disabled=True):
        # disables the color widget label only, the color picker will work as per normal
        self.label.setDisabled(disabled)

    def setColorLinearFloat(self, color, noEmit=True):
        """Sets the color as linear color in 0-1.0 float ranges Eg (1.0, .5, .6666)
        emits the color as a Srgb Int color Eg (0, 255, 134)"""
        cmds.colorSliderGrp(self._getFullName(), edit=True, rgbValue=(color[0], color[1], color[2]))
        self._colorLinear = color
        self._updateColor()
        if not noEmit:
            self._onColorChanged()  # emits and updates the color swatch

    def setColorSrgbFloat(self, color, noEmit=True):
        """sets the color as srgb tuple with 0-1.0 float ranges Eg (1.0, .5, .6666)
        emits the color as a Srgb Int color Eg (0, 255, 134)"""
        colorLinearFloat = colour.convertColorSrgbToLinear(color)
        self._colorLinear = colorLinearFloat
        self._updateColor()
        if not noEmit:
            self._onColorChanged()  # emits and updates the color swatch

    def setColorSrgbInt(self, color, noEmit=True):
        """sets the color as srgb Int tuple with 0-255 float ranges Eg (0, 255, 134)
        emits the color as a Srgb Int color Eg (0, 255, 134)"""
        colorSrgbFloat = colour.rgbIntToFloat(color)
        colorLinearFloat = colour.convertColorSrgbToLinear(colorSrgbFloat)
        self._colorLinear = colorLinearFloat
        self._updateColor()
        if not noEmit:
            self._onColorChanged()  # emits and updates the color swatch

    def colorLinearFloat(self):
        """returns the color of the color picker in linear color
        With 0-1.0 float ranges Eg (1.0, .5, .6666), the color is in Linear color, not SRGB
        """
        self._colorLinear = cmds.colorSliderGrp(self._getFullName(), q=True, rgbValue=True)
        return self._colorLinear

    def colorSrgbInt(self):
        """returns rgb tuple with 0-255 ranges Eg (128, 255, 12)
        """
        return colour.rgbFloatToInt(self.colorSrgbInt())

    def colorSrgbFloat(self):
        """returns rgb tuple with 0-1.0 float ranges Eg (1.0, .5, .6666)
        """
        return colour.convertColorLinearToSrgb(self._colorLinear)

    # ----------
    # MENUS
    # ----------

    def setMenu(self, menu, modeList=None, mouseButton=QtCore.Qt.RightButton):
        """Add the left/middle/right click menu by passing in a QMenu,

        **Note: only works on the label currently

        If a modeList is passed in then create/reset the menu to the modeList:

            [("icon1", "menuName1"), ("icon2", "menuName2")]

        If no modelist the menu won't change

        :param menu: the Qt menu to show on middle click
        :type menu: QtWidgets.QMenu
        :param modeList: a list of menu modes (tuples) eg [("icon1", "menuName1"), ("icon2", "menuName2")]
        :type modeList: list(tuple(str))
        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        """
        # if mouseButton != QtCore.Qt.LeftButton:  # don't create an edit menu if left mouse button menu
            # self.colorPicker.setMenu(menu, mouseButton=mouseButton)
        # only add the action list (menu items) to the label, as the line edit uses the same menu
        self.label.setMenu(menu, modeList=modeList, mouseButton=mouseButton)

    def addActionList(self, modes, mouseButton=QtCore.Qt.RightButton):
        """resets the appropriate mouse click menu with the incoming modes

        **Note: only works on the label currently

            modeList: [("icon1", "menuName1"), ("icon2", "menuName2"), ("icon3", "menuName3")]

        resets the lists and menus:

            self.menuIconList: ["icon1", "icon2", "icon3"]
            self.menuIconList: ["menuName1", "menuName2", "menuName3"]

        :param modes: a list of menu modes (tuples) eg [("icon1", "menuName1"), ("icon2", "menuName2")]
        :type modes: list(tuple(str))
        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        """
        # only add the action list (menu items) to the label, as the line edit uses the same menu
        if self.label:
            self.label.addActionList(modes, mouseButton=mouseButton)
        # else:
            # self.colorPicker.addActionList(modes, mouseButton=mouseButton)

