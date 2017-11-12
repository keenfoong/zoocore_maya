from maya import cmds
from maya.api import OpenMaya as om2

from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs


def distanceBetween(firstNode, secondNode, name):
    """Creates a distance between node and connects the 'firstNode' and 'secondNode' world space
    matrices.

    :param firstNode: The start transform node
    :type firstNode: MObject
    :param secondNode: The second transform node
    :type secondNode: MObject
    :return:  the Three nodes created by the function in the form of a tuple, the first element
    is the distance between node, the second is the start node decompose matrix, the third element
    is the second node decompose matrix
    :rtype: tuple(om2.MObject, om2.MObject, om2.MObject)  
    """
    firstFn = om2.MFnDependencyNode(firstNode)
    secondFn = om2.MFnDependencyNode(secondNode)

    distanceBetweenNode = nodes.createDGNode(name, "distanceBetween")
    distFn = om2.MFnDependencyNode(distanceBetweenNode)
    firstFnWorldMat = firstFn.findPlug("worldMatrix", False)
    firstFnWorldMat.evaluateNumElements()
    secondFnWorldMat = secondFn.findPlug("worldMatrix", False)
    secondFnWorldMat.evaluateNumElements()

    startDecomposeMat = nodes.createDGNode("_".join([firstFn.name(), secondFn.name(), "start_decomp"]),
                                           "decomposeMatrix")
    endDecomposeMat = nodes.createDGNode("_".join([firstFn.name(), secondFn.name(), "end_decomp"]), "decomposeMatrix")
    startDecomFn = om2.MFnDependencyNode(startDecomposeMat)
    endDecomFn = om2.MFnDependencyNode(endDecomposeMat)
    plugs.connectPlugs(firstFnWorldMat.elementByPhysicalIndex(0), startDecomFn.findPlug("inputMatrix", False))
    plugs.connectPlugs(secondFnWorldMat.elementByPhysicalIndex(0), endDecomFn.findPlug("inputMatrix", False))

    plugs.connectPlugs(startDecomFn.findPlug("outputTranslate", False), distFn.findPlug("point1", False))
    plugs.connectPlugs(endDecomFn.findPlug("outputTranslate", False), distFn.findPlug("point2", False))

    return distanceBetweenNode, startDecomposeMat, endDecomposeMat


def multiplyDivide(input1, input2, operation, name):
    """
    :param input1:the node attribute to connect to the input1 value or use int for value
    :type input1: MPlug or MVector
    :param input2:the node attribute to connect to the input2 value or use int for value
    :type input2: MPlug or MVector
    :param operation : the int value for operation ,
                                    no operation = 0,
                                    multipy = 1,
                                    divide = 2,
                                    power = 3
    :type operation: int
    :return, the multiplyDivide node MObject
    :rtype: MObject
    """

    mult = om2.MFnDependencyNode(nodes.createDGNode(name, "multiplyDivide"))
    # assume connection type
    if isinstance(input1, om2.MPlug):
        plugs.connectPlugs(input1, mult.findPlug("input1", False))
    # plug set
    else:
        plugs.setPlugValue(mult.findPlug("input1", False), input1)
    if isinstance(input2, om2.MPlug):
        plugs.connectPlugs(input2, mult.findPlug("input2", False))
    else:
        plugs.setPlugValue(mult.findPlug("input2", False), input1)
    plugs.setPlugValue(mult.findPlug("operation", False), operation)

    return mult.object()


def blendColors(color1, color2, name, blender):
    blendFn = om2.MFnDependencyNode(nodes.createDGNode(name, "blendColors"))
    if isinstance(color1, om2.MPlug):
        plugs.connectPlugs(color1, blendFn.findPlug("color1", False))
    else:
        plugs.setPlugValue(blendFn.findPlug("color1", False), color1)
    if isinstance(color2, om2.MPlug):
        plugs.connectPlugs(color2, blendFn.findPlug("color2", False))
    else:
        plugs.setPlugValue(blendFn.findPlug("color2", False), color2)
    if isinstance(blender, om2.MPlug):
        plugs.connectPlugs(blender, blendFn.findPlug("blender", False))
    else:
        plugs.setPlugValue(blendFn.findPlug("blender", False), blender)
    return blendFn.object()


def floatMath(floatA, floatB, operation, name):
    floatMathFn = om2.MFnDependencyNode(nodes.createDGNode(name, "floatMath"))
    if isinstance(floatA, om2.MPlug):
        plugs.connectPlugs(floatA, floatMathFn.findPlug("floatA", False))
    else:
        plugs.setPlugValue(floatMathFn.findPlug("floatA", False), floatA)

    if isinstance(floatB, om2.MPlug):
        plugs.connectPlugs(floatB, floatMathFn.findPlug("floatB", False))
    else:
        plugs.setPlugValue(floatMathFn.findPlug("floatB", False), floatB)
    plugs.setPlugValue(floatMathFn.findPlug("operation", False), operation)
    return floatMathFn.object()


def blendTwoAttr(input1, input2, blender, name):
    fn = om2.MFnDependencyNode(nodes.createDGNode(name, "blendTwoAttr"))
    inputArray = fn.findPlug("input", False)
    plugs.connectPlugs(input1, inputArray.elementByLogicalIndex(-1))
    plugs.connectPlugs(input2, inputArray.elementByLogicalIndex(-1))
    plugs.connectPlugs(blender, fn.findPlug("attributesBlender", False))
    return fn.object()


def pairBlend(name, inRotateA=None, inRotateB=None, inTranslateA=None, inTranslateB=None, weight=None,
              rotInterpolation=None):
    blendPairNode = om2.MFnDependencyNode(nodes.createDGNode(name, "pairBlend"))
    if inRotateA is not None:
        plugs.connectPlugs(inRotateA, blendPairNode.findPlug("inRotate1", False))
    if inRotateB is not None:
        plugs.connectPlugs(inRotateB, blendPairNode.findPlug("inRotate2", False))
    if inTranslateA is not None:
        plugs.connectPlugs(inTranslateA, blendPairNode.findPlug("inTranslate1", False))
    if inTranslateB is not None:
        plugs.connectPlugs(inTranslateB, blendPairNode.findPlug("inTranslate2", False))
    if weight is not None:
        if isinstance(weight, om2.MPlug):
            plugs.connectPlugs(weight, blendPairNode.findPlug("weight", False))
        else:
            plugs.setPlugValue(blendPairNode.findPlug("weight", False), weight)
    if rotInterpolation is not None:
        if isinstance(rotInterpolation, om2.MPlug):
            plugs.connectPlugs(rotInterpolation, blendPairNode.findPlug("rotInterpolation", False))
        else:
            plugs.setPlugValue(blendPairNode.findPlug("rotInterpolation", False), rotInterpolation)
    return blendPairNode.object()


def conditionVector(firstTerm, secondTerm, colorIfTrue, colorIfFalse, operation, name):
    """
    :param firstTerm: 
    :type firstTerm: om2.MPlug or float
    :param secondTerm: 
    :type secondTerm: om2.MPlug or float 
    :param colorIfTrue: seq of MPlugs or a single MPlug(compound) 
    :type colorIfTrue: om2.MPlug or list(om2.Plug) or om2.MVector
    :param colorIfFalse: seq of MPlugs or a single MPlug(compound)
    :type colorIfFalse: om2.MPlug or list(om2.Plug) or om2.MVector 
    :param operation: the comparsion operator
    :type operation: int
    :param name: the new name for the node
    :type name: str
    :return: 
    :rtype: om2.MObject
    """
    condNode = om2.MFnDependencyNode(nodes.createDGNode(name, "condition"))
    if isinstance(firstTerm, float):
        plugs.setPlugValue(condNode.findPlug("firstTerm", False), firstTerm)
    else:
        plugs.connectPlugs(firstTerm, condNode.findPlug("firstTerm", False))
    if isinstance(operation, int):
        plugs.setPlugValue(condNode.findPlug("operation", False), operation)
    else:
        plugs.connectPlugs(operation, condNode.findPlug("operation", False))

    if isinstance(secondTerm, float):
        plugs.setPlugValue(condNode.findPlug("secondTerm", False), firstTerm)
    else:
        plugs.connectPlugs(secondTerm, condNode.findPlug("secondTerm", False))
    if isinstance(colorIfTrue, om2.MPlug):
        plugs.connectPlugs(colorIfTrue, condNode.findPlug("colorIfTrue", False))
    elif isinstance(colorIfTrue, om2.MVector):
        plugs.setPlugValue(condNode.findPlug("colorIfTrue", False), colorIfTrue)
    else:
        color = condNode.findPlug("colorIfTrue", False)
        # expecting seq of plugs
        for i, p in enumerate(colorIfTrue):
            child = color.child(i)
            plugs.connectPlugs(p, child)
    if isinstance(colorIfFalse, om2.MPlug):
        plugs.connectPlugs(colorIfFalse, condNode.findPlug("colorIfFalse", False))
    elif isinstance(colorIfFalse, om2.MVector):
        plugs.setPlugValue(condNode.findPlug("colorIfFalse", False), colorIfFalse)
    else:
        color = condNode.findPlug("colorIfFalse", False)
        # expecting seq of plugs
        for i, p in enumerate(colorIfFalse):
            child = color.child(i)
            plugs.connectPlugs(p, child)
    return condNode.object()


def createAnnotation(rootObj, endObj, text=None, name=None):
    name = name or "annotation"
    rootDag = om2.MFnDagNode(rootObj)
    boundingBox = rootDag.boundingBox
    center = om2.MVector(boundingBox.center)
    transform = nodes.createDagNode("_".join([name, "loc"]), "transform", parent=rootObj)
    nodes.setTranslation(transform, nodes.getTranslation(rootObj, om2.MSpace.kWorld), om2.MSpace.kWorld)
    annotationNode = nodes.asMObject(cmds.annotate(nodes.nameFromMObject(transform), tx=text))
    annParent = nodes.getParent(annotationNode)
    nodes.rename(annParent, name)
    plugs.setPlugValue(om2.MFnDagNode(annotationNode).findPlug("position", False), center)
    nodes.setParent(annParent, endObj, False)
    return annotationNode, transform


def createMultMatrix(name, inputs, output):
    multMatrix = nodes.createDGNode(name, "multMatrix")
    fn = om2.MFnDependencyNode(multMatrix)
    plugs.connectPlugs(fn.findPlug("matrixSum", False), output)
    compound = fn.findPlug("matrixIn", False)
    compound.evaluateNumElements()

    for i in xrange(len(inputs)):
        inp = inputs[i]
        if isinstance(inp, om2.MPlug):
            plugs.connectPlugs(inp, compound.elementByLogicalIndex(i))
            continue
        plugs.setPlugValue(compound.elementByLogicalIndex(i), inp)
    return multMatrix


def createWtAddMatrix():
    pass


def createDecompose(name, destination, translateValues, scaleValues, rotationValues, inputMatrixPlug=None):
    """Creates a decompose node and connects it to the destination node.

    :param inputMatrixPlug: The input matrix plug to connect from.
    :type inputMatrixPlug: om2.MPlug
    :param translateValues: the x,y,z to apply must have all three if all three are true then the compound will be
    connected.
    :type translateValues: list(str)
    :param scaleValues: the x,y,z to apply must have all three if all three are true then the compound will be
    connected.
    :type scaleValues: list(str)
    :param rotationValues: the x,y,z to apply must have all three if all three are true then the compound will be
    connected.
    :type rotationValues: list(str)
    :param destination: the node to connect to
    :type destination: om2.MObject
    :return: the decompose node
    :rtype: om2.MObject
    """
    decompose = nodes.createDGNode(name, "decomposeMatrix")
    mfn = om2.MFnDependencyNode(decompose)
    destFn = om2.MFnDependencyNode(destination)
    if inputMatrixPlug is not None:
        plugs.connectPlugs(inputMatrixPlug, mfn.findPlug("inputMatrix", False))
    # translation
    plugs.connectVectorPlugs(mfn.findPlug("outputTranslate", False), destFn.findPlug("translate", False),
                             translateValues)
    plugs.connectVectorPlugs(mfn.findPlug("outputRotate", False), destFn.findPlug("rotate", False), rotationValues)
    plugs.connectVectorPlugs(mfn.findPlug("outputScale", False), destFn.findPlug("scale", False), scaleValues)
    return decompose


def graphSerialize(graphNodes):
    data = []
    for i in iter(graphNodes):
        data.append(nodes.serializeNode(i))
    return data


def graphdeserialize(data, inputs):
    """
    :param data:
    :type data: list
    :param inputs:
    :type inputs: dict{str: plug instance}
    :return:
    :rtype:
    """
    for nodeData in iter(data):
        pass


"""

def deserializeNode(data):
    parent = data.get("parent")
    name = om2.MNamespace.stripNamespaceFromName(data["name"]).split("|")[-1]
    nodeType = data["type"]
    if not parent:
        newNode = nodes.createDGNode(name, nodeType)
        dep = om2.MFnDependencyNode(newNode)
    else:
        newNode = nodes.createDagNode(name, nodeType)
        dep = om2.MFnDagNode(newNode)
    attributes = data.get("attributes")
    if attributes:
        for name, attrData in iter(attributes.items()):
            if not attrData.get("isDynamic"):
                plugs.setAttr(dep.findPlug(name, False), attrData["value"])
                continue
            newAttr = nodes.addAttribute(dep.object(), name, name, attrData["type"])
            if newAttr is None:
                continue
            newAttr.keyable = attrData["keyable"]
            newAttr.channelBox = attrData["channelBox"]
            currentPlug = dep.findPlug(newAttr.object(), False)
            currentPlug.isLocked = attrData["locked"]
            max = attrData["max"]
            min = attrData["min"]
            softMax = attrData["softMax"]
            softMin = attrData["softMin"]
            default = attrData["default"]
            plugs.setMax(currentPlug, max)
            plugs.setMin(currentPlug, min)
            plugs.setMin(currentPlug, softMax)
            plugs.setMin(currentPlug, softMin)
            # if newAttr.hasFn(om2.MFn.kEnumAttribute):
                # if default != plugs.plugDefault(currentPlug):
                #     plugs.setPlugDefault(currentPlug, default)
    return newNode


def deserializeContainer(containerName, data):
    children = data["children"]
    newNodes = {}
    containerName = data["name"]
    for nodeName, nodeData in iter(data.items()):
        name = nodeData["name"]
        if name in newNodes:
            newNode = newNodes[name]
        else:
            newNode = deserializeNode(nodeData)
            newNodes[name] = newNode
        parent = nodeData.get("parent")
        if parent:
            if parent == containerName:
                nodes.setParent(newNode, container, maintainOffset=True)
            elif parent in newNodes:
                nodes.setParent(newNode, newNodes[parent], maintainOffset=True)
            else:
                parentdata = children.get(parent)
                if parentdata:
                    newParent = deserializeNode(parentdata)
                    nodes.setParent(newNode, newParent, maintainOffset=True)
                    newNodes[parent] = newParent
        for attrName, attrData in nodeData["connections"]:
            connections = attrData.get("connections")
            if connections:
                for con in iter(connections):
                    sourceNode = newNodes.get(con[0])
                    if not sourceNode:
                        sourceNodeData = children.get(con[0])
                        if not sourceNodeData:
                            try:
                                sourceNode = nodes.asMObject(con[0])
                            except RuntimeError:
                                continue
                        else:
                            sourceNode = deserializeNode(sourceNodeData)
                        newNodes[con[0]] = sourceNode
                    destinationNodeName = nodes.nameFromMObject(newNode)
                    sourceNodeName = nodes.nameFromMObject(sourceNode)
                    sourcename = ".".join([sourceNodeName, con[1]])
                    destName = ".".join([destinationNodeName, con[0]])
                    destPlug = plugs.asMPlug(destName)
                    sourcePlug = plugs.asMPlug(sourcename)
                    plugs.connectPlugs(sourcePlug, destPlug)

    return container

"""
