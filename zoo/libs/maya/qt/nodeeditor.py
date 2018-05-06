from maya import cmds
from zoo.libs.maya.qt import mayaui
from qt import QtWidgets, QtCore
import weakref


def getPrimaryNodeEditor():
    """Find and return the name of the primary node editor if it exists.

    :return: The node editor name
    :rtype: str
    """
    allNEs = cmds.getPanel(scriptType="nodeEditorPanel")
    for oneNE in allNEs:
        ned = oneNE + "NodeEditorEd"
        if cmds.nodeEditor(ned, query=True, primary=True):
            return ned
    return ""


class NodeEditorWrapper(QtCore.QObject):
    @staticmethod
    def nodeEditorAsQtWidgets(nodeEditor):
        nodeEdPane = mayaui.toQtObject(nodeEditor)
        view = nodeEdPane.findChild(QtWidgets.QGraphicsView)
        return view, view.scene()

    @staticmethod
    def itemsRect(items):
        sourceRect = QtCore.QRect()

        for item in items:
            sourceRect = sourceRect.united(QtCore.QRect(*item.sceneBoundingRect().getRect()))
        return sourceRect

    def __init__(self, nodeEditor=None):
        super(NodeEditorWrapper, self).__init__()
        if not nodeEditor:
            primary = getPrimaryNodeEditor()
            if not primary:
                self.view, self.scene = None, None
            else:
                self.view, self.scene = NodeEditorWrapper.nodeEditorAsQtWidgets(getPrimaryNodeEditor())
        else:
            self.view, self.scene = NodeEditorWrapper.nodeEditorAsQtWidgets(nodeEditor)
    def exists(self):
        return True
    def selectedNodeItems(self):
        # check against type instead of isinstance since graphicsPathItem inherents from QGraphicsItem
        return [i for i in self.scene.selectedItems() if type(i) == QtWidgets.QGraphicsItem]

    def selectedConnections(self):
        return [i for i in self.scene.selectedItems() if type(i) == QtWidgets.QGraphicsPathItem]

    def alignLeft(self, items=None):
        items = items or self.selectedNodeItems()
        xPos = min([i.pos().x() for i in items])
        for item in items:
            item.setX(xPos)

    def alignRight(self, items):
        items = items or self.selectedNodeItems()
        xPos = max([i.pos().x() for i in items])
        for item in items:
            item.setX(xPos)

    def alignTop(self, items):
        items = items or self.selectedNodeItems()
        xPos = min([i.pos().y() for i in items])
        for item in items:
            item.setY(xPos)

    def alignBottom(self, items):
        items = items or self.selectedNodeItems()
        xPos = max([i.pos().y() for i in items])
        for item in items:
            item.setY(xPos)

    def alignCenterX(self, items):
        items = items or self.selectedNodeItems()
        rect = NodeEditorWrapper.itemsRect(items)
        center = rect.center()
        for i in items:
            i.setX(center.x())

    def alignCenterY(self, items):
        items = items or self.selectedNodeItems()
        rect = NodeEditorWrapper.itemsRect(items)
        center = rect.center()
        for i in items:
            i.setY(center.y())
