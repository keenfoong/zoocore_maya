import os
import pprint

from zoo.libs.maya.qt import mayaui
from zoo.libs.utils import file
from zoo.libs.utils import classtypes
from zoo.libs.utils import general
from zoo.libs.utils import zlogging
from zoo.libs.command import executor
from maya import cmds

logger = zlogging.getLogger(__name__)


class InvalidJsonFileFormat(Exception):
    """Raised in case of invalid formatted json file(.mmlayout)
    """
    pass


def findLayout(layoutId):
    reg = LayoutRegistry()
    if layoutId in reg.layouts:
        return reg.layouts[layoutId]


class LayoutRegistry(object):
    LAYOUT_ENV = "ZOO_MM_LAYOUT_PATH"
    __metaclass__ = classtypes.Singleton

    def __init__(self):
        self.layouts = {}
        self.registerLayoutByEnv(LayoutRegistry.LAYOUT_ENV)

    def registerLayoutByEnv(self, env):
        """Recursively Registers all layout files with the extension .mmlayout and loads the json data with a layout
        instance then adds to the layouts cache

        :param env: the environment variable pointing to the parent directory
        :type env: str
        """
        paths = os.environ.get(env, "").split(os.pathsep)
        for p in paths:
            for root, dirs, files in os.walk(p):
                for f in files:
                    layoutFile = os.path.join(root, f)
                    try:
                        if f.endswith(".mmlayout"):
                            data = file.loadJson(layoutFile)
                            self.layouts[data["id"]] = Layout(data)
                    # If the Json data is invalid(formatted) it will raise a valueError without a file location
                    # so raise something useful
                    except ValueError:
                        raise InvalidJsonFileFormat("Layout file: {} is invalid possibly due to the "
                                                    "formatting.".format(layoutFile),
                                                    exc_info=True)

    def registerLayoutData(self, data):
        self.layouts[data["id"]] = Layout(data)


class Layout(object):
    """
    ::example:
     >>> layoutData={"items":{"N": "",
                              "NW": "",
                              "W": "",
                              "SW": "",
                              "S": "",
                              "SE": "",
                              "E": "",
                              "NE": "",
                              "generic": [{"type": "menu",
                                          "name": "Testmenu",
                                          "children": [{"type": "python",
                                                        "command": "",
                                                        "commandUi": ""}
                                                        ]
                                          ]

                              },
                    "id": "some.layout.id"}
     >>> layoutObj = Layout(layoutData)
     >>> layoutObj
    """
    executor = executor.Executor()

    def __init__(self, data):
        """
        :param data: The layout dict usually loaded from a json mmlayout file
        :type data: dict
        """
        self.data = data
        self.id = data["id"]
        self.solved = False

    def __repr__(self):
        return "Layout: {}".format(pprint.pformat(self.data))

    def __getitem__(self, item):
        """
        :param item: The name of the layout region eg. "N", "S" etc
        :type item: str
        :return: Will return a dict in cases of marking menu region(n,s,w etc) being a nested after a layout has been
        solved, a list will be returned for the generic region , str is return when the layout hasnt been solved but
        references another layout
        :rtype: list or dict or str
        """
        return self.data.get(item)

    def __iter__(self):
        """Generator that loops the layout items

        :rtype: tuple(str, dict value)
        """
        for name, data in iter(self.data.items()):
            yield name, data

    def items(self):
        """
        :return: The layout items dict
        :rtype: dict
        """
        return self.data["items"].items()

    def merge(self, layout):

        self.data = general.merge(self.data, layout.data["items"])
        self.solve()

    def validate(self, layout=None):
        """Recursively validates the layout, returning all failed items, if an item references another layout that
        layout will used be validated.

        :param layout: The layout instance to solve
        :type layout: Layout
        :return: the failed items
        :rtype: list
        """
        layout = layout or self
        failed = []
        for item, data in iter(layout["items"].items()):
            if not data:
                continue
            elif isinstance(data, Layout):
                failed.extend(self.validate(data))
            elif item == "generic":
                failed.extend(self._validateGeneric(data))
            elif data.get("type", "") == "python":
                continue
            elif data.get("type", "") == "zooCommand":
                command = self.executor.findCommand(data["command"])
                if not command:
                    failed.append(data)

            else:
                failed.append(data)
        return failed

    def _validateGeneric(self, data):
        """Validates the generic items list to ensure that all commands are valid within the executor

        :param data: the generic items list from the layout
        :type data: list
        :return: the invalid items
        :rtype: list
        """
        failed = []
        for item in iter(data):
            commandType = item["type"]
            # cant validate python commands without executing them?
            if commandType == "python":
                continue
            elif commandType == "menu":
                failed.extend(self._validateGeneric(item["children"]))
            elif commandType == "zooCommand":
                command = self.executor.findCommand(item)
                if not command:
                    failed.append(item)
                continue
            else:
                failed.append(item)

        return failed

    def solve(self):
        """Recursively solves the layout by expanding any @layout.id references which will compose a single dict ready
        for use.

        :return: Whether or not the layout was solved
        :rtype: bool
        """
        registry = LayoutRegistry()
        solved = False
        for item, data in self.data["items"].items():
            if not data:
                continue
            elif item == "generic":
                solved = True
                continue
            elif data["type"] == "layout":
                subLayout = registry.layouts.get(data["command"])
                if not subLayout:
                    logger.warning("No layout with the id {}, skipping".format(data))
                    continue
                subLayout.solve()
                self.data[item] = subLayout
                solved = True

        self.solved = solved
        return solved


class MarkingMenu(object):
    """Maya MarkingMenu wrapper object to support zoocommands and python executable code. MM layouts are defined by the
    Layout instance class
    """

    def __init__(self, layout, name, parent, commandExecutor):
        """
        :param layout: the markingMenu layout instance
        :type layout: ::class:`Layout`
        :param name:
        :type name: The markingMenu name
        :param parent: The fullpath to the parent widget
        :type parent: str
        :param commandExecutor:
        :type commandExecutor: ::class::`zoo.libs.command.executor.Executor`
        """
        self.layout = layout
        self.name = name
        self.commandExecutor = commandExecutor
        self.parent = parent
        self.popMenu = None  # the menu popup menu, gross thanks maya
        if cmds.popupMenu(name, ex=True):
            cmds.deleteUI(name)

        self.options = {"allowOptionBoxes": False,
                        "altModifier": False,
                        "button": 1,
                        "ctrlModifier": False,
                        "postMenuCommandOnce": True,
                        "shiftModifier": False}

    def asQObject(self):
        """Returns this markingMenu as a PYQT object
        :return:
        :rtype: QMenu
        """
        return mayaui.toQtObject(self.name)

    def attach(self):
        """Generate's the marking using the parent marking menu.

        :return:
        :rtype: bool
        """
        if cmds.popupMenu(self.parent, exists=True):
            self._show(self.parent, self.parent)
            return True
        return False

    def create(self):
        """Create's a new popup markingMenu parented to self.parent instance, use ::method:`attach` if you to add to
        existing markingmenu.

        :return: current instance
        :rtype: ::class:`MarkingMenu`
        """
        if cmds.popupMenu(self.name, exists=True):
            cmds.deleteUI(self.name)

        self.popMenu = cmds.popupMenu(self.name, parent=self.parent,
                                      markingMenu=True, postMenuCommand=self._show, **self.options)
        return self

    def _show(self, menu, parent):
        cmds.setParent(menu, menu=True)
        cmds.menu(menu, edit=True, deleteAllItems=True)

        self.show(self.layout, menu, parent)

    def kill(self):
        if cmds.popupMenu(self.name, ex=True):
            cmds.deleteUI(self.name)

    def _buildGeneric(self, data, menu):
        for item in data:
            if item["type"] == "zooCommand":
                command = self.commandExecutor.findCommand(item["command"])
                if command is None:
                    logger.warning("Failed To find Command: {}".format(item["command"]))
                    continue
                commandAction = command.commandAction(uiType=1, parent=menu)
                commandAction.triggered.connect(self.commandExecutor.execute)
                continue
            elif item["type"] == "menu":
                subMenu = cmds.menuItem(label=item["label"], subMenu=True)
                self._buildGeneric(item["children"], subMenu)
            elif item["type"] == "python":
                cmds.menuItem(label=item["label"], command=item["command"], parent=menu)
                optionBox = item.get("optionBox", False)
                if optionBox:
                    cmds.menuItem(parent=menu, optionBox=optionBox, command=item["commandUi"])

    def show(self, layout, menu, parent):
        for item, data in layout.items():
            if not data:
                continue
            # menu generic
            if item == "generic":
                self._buildGeneric(data, menu)
                continue
            # nested marking menu
            elif isinstance(data, Layout):
                radMenu = cmds.menuItem(label=data["id"], subMenu=True, radialPosition=item.upper())
                self.show(data, radMenu, parent)
                continue
            elif data["type"] == "zooCommand":
                # single item
                command = self.commandExecutor.findCommand(data["command"])
                if command is None:
                    logger.warning("ZooCommand by id:{} doesn't exist".format(data["command"]))
                    continue
                action = command.commandAction(1, parent=menu)
                cmds.menuItem(action.item, e=True, radialPosition=item.upper())
                action.triggered.connect(self.commandExecutor.execute)

            elif data["type"] == "python":
                cmds.menuItem(label=data["label"], optionBox=data.get("optionBox", False),
                              command=data["command"])

    def allowOptionBoxes(self):
        return cmds.popupMenu(self.name, q=True, allowOptionBoxes=True)

    def altModifier(self):
        return cmds.popupMenu(self.name, q=True, altModifier=True)

    def button(self):
        return cmds.popupMenu(self.name, q=True, button=True)

    def ctrlModifier(self):
        return cmds.popupMenu(self.name, q=True, ctrlModifier=True)

    def deleteAllItems(self):
        try:
            cmds.popupMenu(self.name, e=True, deleteAllItems=True)
        except Exception:
            return False
        return True

    def exists(self):
        return cmds.popupMenu(self.name, exists=True)

    def itemArray(self):
        return cmds.popupMenu(self.name, q=True, itemArray=True)

    def markingMenu(self):
        return cmds.popupMenu(self.name, q=True, markingMenu=True)

    def numberOfItems(self):
        return cmds.popupMenu(self.name, q=True, numberOfItems=True)

    def postMenuCommand(self, command):
        cmds.popupMenu(self.name, e=True, postMenuCommand=command)

    def postMenuCommandOnce(self, state):
        cmds.popupMenu(self.name, e=True, postMenuCommandOnce=state)

    def shiftModifier(self):
        return cmds.popupMenu(self.name, q=True, shiftModifier=True)

    def setShiftModifier(self, value):
        return cmds.popupMenu(self.name, e=True, shiftModifier=value)

    def setParent(self, parent):
        return cmds.popupMenu(self.name, e=True, parent=parent.objectName())

    def setCtrlModifier(self, value):
        return cmds.popupMenu(self.name, e=True, ctrlModifier=value)

    def setAltModifier(self, state):
        return cmds.popupMenu(self.name, e=True, altModifier=state)

    def setUseLeftMouseButton(self):
        return cmds.popupMenu(self.name, e=True, button=1)

    def setUseRightMouseButton(self):
        return cmds.popupMenu(self.name, e=True, button=2)

    def setUseMiddleMouseButton(self):
        return cmds.popupMenu(self.name, e=True, button=3)
