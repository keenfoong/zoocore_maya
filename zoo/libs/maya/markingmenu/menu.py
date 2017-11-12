import os
import pprint

from zoo.libs.pyqt.embed import mayaui
from zoo.libs.utils import file
from zoo.libs.utils import classtypes
from zoo.libs.utils import general
from zoo.libs.utils import zlogging
from zoo.libs.command import executor
from maya import cmds

logger = zlogging.getLogger(__name__)


class LayoutRegistry(object):
    __metaclass__ = classtypes.Singleton

    def __init__(self):
        self.layouts = {}

    def registryLayoutByEnv(self, env):
        """Recursively Registers all layout files with the extension .mmlayout and loads the json data with a layout
        instance then adds to the layouts cache

        :param env: the environment variable pointing to the parent directory
        :type env: str
        """
        paths = os.environ[env].split(os.pathsep)
        for p in paths:
            for root, dirs, files in os.walk(p):
                for f in files:
                    if f.endswith(".mmlayout"):
                        data = file.loadJson(os.path.join(root, f))
                        self.layouts[data["id"]] = Layout(data)


class Layout(object):
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
        for item, data in iter(layout):
            if isinstance(data, Layout):
                failed.extend(self.validate(data))
            elif item == "generic":
                failed.extend(self._validateGeneric(data))
            command = self.executor.findCommand(data)
            if not command:
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
            if isinstance(item, basestring):
                command = self.executor.findCommand(item)
                if not command:
                    failed.append(item)
                continue
            elif isinstance(item, dict):
                failed.extend(self._validateGeneric(item["generic"]))
        return failed

    def solve(self):
        """Recursively solves the layout by expanding any @layout.id references which will compose a single dict ready
        for use.

        :return: Whether or not the layout was solved
        :rtype: bool
        """
        registry = LayoutRegistry()
        solved = False
        for item, data in self.data.items():
            if isinstance(data, basestring) and data.startswith("@"):
                subLayout = registry.layouts.get(data)
                if not subLayout:
                    logger.warning("No layout with the id {}, skipping".format(data))
                    continue
                subLayout.solve()
                self.data[item] = subLayout
                solved = True
        self.solved = solved
        return solved


class MarkingMenu(object):
    """Maya MarkingMenu wrapper object to support zoocommands. MM layouts are defined by the Layout instance class
    """
    def __init__(self, layout, name, parent, commandExecutor):
        self.layout = layout
        self.name = name
        self.description = ""
        self.commandExecutor = commandExecutor
        self.parent = parent
        self.popMenu = None  # the menu popup menu, gross thanks maya

        self.options = {"allowOptionBoxes": False,
                        "altModifier": False,
                        "button": 1,
                        "ctrlModifier": False,
                        "postMenuCommandOnce": True,
                        "shiftModifier": False}

    def asQObject(self):
        return mayaui.toQtObject(self.name)

    def create(self):
        if cmds.popupMenu(self.name, exists=True):
            cmds.deleteUI(self.name)

        self.popMenu = cmds.popupMenu(self.name, parent=self.parent,
                                      markingMenu=True, postMenuCommand=self._show, **self.options)
        return self

    def _show(self, menu, parent):
        cmds.setParent(menu, m=True)
        cmds.menu(menu, e=True, dai=True)
        self.show(self.layout, menu, parent)

    def kill(self):
        if cmds.popupMenu(self.name, ex=True):
            cmds.deleteUI(self.name)

    def _buildGeneric(self, data, menu, parent):
        for item in data:
            if isinstance(item, basestring):
                command = self.commandExecutor.findCommand(item)
                uiData = command.uiData
                uiData.create(parent=menu)
                uiData.triggered.connect(self.commandExecutor.execute)
                continue
            elif item["type"] == "menu":
                subMenu = cmds.menuItem(label=item["label"], subMenu=True)
                self._buildGeneric(item["children"], subMenu, parent)

    def show(self, layout, menu, parent):
        for item, data in layout.items():
            if not data:
                continue
            # menu generic
            if item == "generic":
                self._buildGeneric(data, menu, parent)
                continue
            # nested marking menu
            elif isinstance(data, Layout):
                radMenu = cmds.menuItem(label=data["id"], subMenu=True, radialPosition=item.upper())
                self.show(data, radMenu, parent)
                continue
            # single item
            command = self.commandExecutor.findCommand(data)
            uiData = command.commandAction(1)
            uiData.create(parent=menu)
            cmds.menuItem(uiData.item, e=True, radialPosition=item.upper())
            uiData.triggered.connect(self.commandExecutor.execute)

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
