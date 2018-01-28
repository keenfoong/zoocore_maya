from zoo.libs.maya.markingmenu import menu, utils
from zoo.libs.maya.api import nodes, scene

layoutData = {
    "items": {
        "generic": [
            {
                "type": "menu",
                "label": "Testmenu",
                "children": [
                    {
                        "type": "python",
                        "command": "print '\hello world\'",
                        "label": "test",
                        "optionBox": True,
                        "commandUi": "print '\optionBox'"
                    }
                ]
            }
        ]
    },
    "id": "some.layout.id"
}


def validateAndBuild(parentMenu, nodeName):
    triggerNode = nodes.asMObject(nodeName)
    if not utils.hasTrigger(triggerNode):
        return 0
    triggerNodes = [triggerNode] + scene.getSelectedNodes()

    visited = []
    validLayout = None
    # gather the trigger information from the current node and the selection
    for st in triggerNodes:
        # get the compound trigger plug
        triggerPlugs = utils.triggerPlugsFromNode(st)
        # for each compound found, consolidate and gather info
        for tp in triggerPlugs:
            node = tp.node()
            print node
            if node in visited:
                continue
            visited.append(node)
            # pull the command type and command string from the compoundplug
            commandType = tp.child(0).asInt()
            commandStr = tp.child(1).asString()
            if commandType in (utils.PYTHON_TYPE, utils.COMMAND_TYPE):
                pass
            elif commandType == utils.LAYOUT_TYPE:
                layout = menu.findLayout(commandStr)
                if not layout:
                    continue
                if validLayout:
                    validLayout.merge(layout)
                else:
                    validLayout = layout
    if validLayout is None:
        return 0
    validLayout.solve()
    mainMenu = menu.MarkingMenu(validLayout, "zooTriggerMenu", parentMenu, validLayout.executor)
    mainMenu.attach()
    return 1
