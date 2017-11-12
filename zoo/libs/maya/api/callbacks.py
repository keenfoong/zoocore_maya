from maya.api import OpenMaya as om2


def removeCallbacksFromNode(mobject):
    """
    :param mobject: The node to remote all node callbacks from
    :type mobject: om2.MObject
    :return: the number of callbacks removed
    :rtype: int
    """
    calls = om2.MMessage.nodeCallbacks(mobject)
    count = len(calls)
    for cb in iter(calls):
        om2.MMessage.removeCallback(cb)
    return count


def removeCallbacksFromNodes(mobjects):
    """Will remove all callbacks from each node.

    :param mobjects: The nodes to remove callbacks from
    :type mobjects: sequence(MObject)
    :return: total count of all callbacks removed
    :rtype: int
    """

    cbcount = 0
    for mobj in iter(mobjects):
        cbcount += removeCallbacksFromNode(mobj)
    return cbcount
