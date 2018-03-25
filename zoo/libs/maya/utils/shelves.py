from maya import cmds


class Shelf(object):
    """A simple class to build shelves in maya. Since the build method is empty,
    it should be extended by the derived class to build the necessary shelf elements.
    By default it creates an empty shelf called "customShelf"."""

    def __init__(self, name="Animation"):
        self.name = name
        self.labelBackground = (0, 0, 0, 0)
        self.labelColour = (.9, .9, .9)

    def createShelf(self):
        self.name = cmds.shelfLayout(self.name, parent="ShelfLayout")

    def addButton(self, label, icon="commandButton.png", command=None, doubleCommand=None, Type="python"):
        """Adds a shelf button with the specified label, command, double click command and image."""
        cmds.setParent(self.name)
        icon = icon or ""
        command = command or ""
        doubleCommand = doubleCommand or ""
        return cmds.shelfButton(width=37, height=37, image=icon, label=label, command=command,
                                doubleClickCommand=doubleCommand,
                                imageOverlayLabel=label, overlayLabelBackColor=self.labelBackground,
                                overlayLabelColor=self.labelColour, sourceType=Type)

    def addMenuItem(self, parent, label, command="", icon=""):
        """Adds a shelf button with the specified label, command, and image."""
        icon = icon or ""
        return cmds.menuItem(parent=parent, label=label, command=command, icon=icon)

    def addSubMenu(self, parent, label, icon=None):
        """Adds a sub menu item with the specified label and icon to the specified parent popup menu."""
        icon = icon or ""
        return cmds.menuItem(parent=parent, label=label, icon=icon, subMenu=1)

    def _cleanOldShelf(self):
        """Checks if the shelf exists and empties it if it does or creates it if it does not."""
        cleanOldShelf(self.name)


def cleanOldShelf(shelfName):
    """Checks if the shelf exists and empties it if it does"""
    if cmds.shelfLayout(shelfName, exists=1):
        if cmds.shelfLayout(shelfName, query=1, childArray=1):
            for each in cmds.shelfLayout(shelfName, query=1, childArray=1):
                cmds.deleteUI(each)
        cmds.deleteUI(shelfName)
