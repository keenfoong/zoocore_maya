from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import attrtypes
from zoo.libs.maya.meta import base
from maya.api import OpenMaya as om2

TRIGGER_ATTR_NAME = "zooTrigger"
LAYOUTID_ATTR_NAME = "zooTriggerLayoutId"
COMMANDTYPE_ATTR_NAME = "zooTriggerCommandType"
COMMAND_ATTR_NAME = "zooTriggerString"

# command Types
PYTHON_TYPE = 0
COMMAND_TYPE = 1
LAYOUT_TYPE = 2


def updateCommandString(node, value):
    fn = om2.MFnDependencyNode(node)
    if not fn.hasAttribute(TRIGGER_ATTR_NAME):
        return False
    comp = fn.findPlug(TRIGGER_ATTR_NAME, False)
    commandStr = comp.child(1)
    commandStr.isLocked = False
    commandStr.setString(value)
    commandStr.isLocked = True
    return True


def createTriggerAttributes(node, commandType, command):
    """ Create's the standard zootrigger compound attribute including children.


    :param node: the node to add the command to,
    :type node: om2.MObject
    :param commandType: PYTHON_TYPE ,COMMAND_TYPE, LAYOUT_TYPE
    :type commandType: int
    :param command: if COMMAND_TYPE then the command arg value should be a zoocommand id , if PYTHONTYPE then it
    should be an executable str, if LAYOUT_TYPE then the layoutId.
    :type command: str
    :return: The compound MPlug
    :rtype: om2.MPlug
    """
    children = [
        {"name": COMMANDTYPE_ATTR_NAME, "Type": attrtypes.kMFnNumericInt, "isArray": False, "value": commandType,
         "locked": True},
        {"name": COMMAND_ATTR_NAME, "Type": attrtypes.kMFnDataString, "isArray": False, "value": command,
         "locked": True}]
    return nodes.addCompoundAttribute(node, TRIGGER_ATTR_NAME, TRIGGER_ATTR_NAME, children, False)


def hasTrigger(node):
    """Determines if the current node is attached to a trigger.
    There's two ways a trigger can be determined, the first is the zooTrigger compound attr exist's directly on the node.
    The second is the node is attached to a meta node which has the zooTrigger attr.

    :param node: The node to search
    :type node: om2.MObject
    :return: True if valid Trigger
    :rtype: bool
    """
    # first check on the current node
    fn = om2.MFnDependencyNode(node)
    if fn.hasAttribute(TRIGGER_ATTR_NAME):
        return True
    # ok so its not on the node, check for a meta node node
    attachedmeta = base.getConnectedMetaNodes(node, direction=om2.MItDependencyGraph.kUpstream)
    for i in attachedmeta:
        if i.hasAttribute(TRIGGER_ATTR_NAME):
            return True
    return False


def layoutIdsFromNode(node):
    """
    :param node:
    :type node:
    :return:
    :rtype: iterable(str)
    """
    fn = om2.MFnDependencyNode(node)
    layouts = []
    if fn.hasAttribute(LAYOUTID_ATTR_NAME):
        triggerComp = fn.findPlug(LAYOUTID_ATTR_NAME, False)
        layoutId = triggerComp.asString()
        if layoutId:
            layouts.append(layoutId)
        # ok so its not on the node, check for a meta node node
    attachedmeta = base.getConnectedMetaNodes(node, direction=om2.MItDependencyGraph.kUpstream)
    for i in attachedmeta:
        if i.hasAttribute(LAYOUTID_ATTR_NAME):
            triggerComp = i.findPlug(LAYOUTID_ATTR_NAME, False)
            layoutId = triggerComp.asString()
            if layoutId:
                layouts.append(layoutId)
    return layouts


def triggerPlugsFromNode(node):
    fn = om2.MFnDependencyNode(node)
    triggerPlugs = []
    if fn.hasAttribute(TRIGGER_ATTR_NAME):
        triggerPlugs.append(fn.findPlug(TRIGGER_ATTR_NAME, False))

    attachedmeta = base.getConnectedMetaNodes(node, direction=om2.MItDependencyGraph.kUpstream)
    for i in attachedmeta:
        if i.hasAttribute(TRIGGER_ATTR_NAME):
            triggerPlugs.append(i.findPlug(TRIGGER_ATTR_NAME, False))
    return triggerPlugs
