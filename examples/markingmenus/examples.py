from zoo.libs.maya.markingmenu import menu
from zoo.libs.maya.api import nodes


class DynamicMMBySelectionExample(menu.MarkingMenu):
    id = "dynamicMMBySelectionExample"

    def show(self, layout, menu, parent):
        selNodes = self.commandArguments.get("nodes")
        if not selNodes:
            return
        items = []
        for i in selNodes:
            name = nodes.nameFromMObject(i.object(), partialName=False, includeNamespace=False)
            items.append({"type": "command", "id": "printNodePath",
                          "arguments": {"node": i, "label": name}})

        layout.data.update({"items": {"generic": items
                                           }
                                 })
        layout.solve()
        super(DynamicMMBySelectionExample, self).show(layout, menu, parent)


class PrintNodePath(menu.MarkingMenuCommand):
    id = "printNodePath"
    creator = "Zootools"

    @staticmethod
    def uiData(arguments):
        label = arguments.get("label", "None")
        return {"icon": "eye",
                "label": label,
                "bold": False,
                "italic": True,
                "optionBox": True,
                "optionBoxIcon": "eye"
                }

    def execute(self, arguments):
        node = arguments.get("node")
        print nodes.nameFromMObject(node.object())

    def executeUI(self, arguments):
        node = arguments.get("node")
        print nodes.nameFromMObject(node.object())
