from maya.api import OpenMaya as om2

from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs


def getCurveData(shape, space=om2.MSpace.kObject):
    """From a given NurbsCurve shape node serialize the cvs positions, knots, degree, form rgb colours

    :param shape: MObject that represents the NurbsCurve shape
    :return: dict
    :param space:
    :type space: om2.MSpace

    Example::
        >>>nurbsCurve = cmds.circle()[1]
        # requires an MObject of the shape node
        >>>data = curve_utils.getCurveData(api.asMObject(nurbsCurve))
    """
    if isinstance(shape, om2.MObject):
        shape = om2.MFnDagNode(shape).getPath()
    data = nodes.getNodeColourData(shape.node())
    curve = om2.MFnNurbsCurve(shape)
    knots = curve.knots()
    cvs = curve.cvPositions(space)
    data["knots"] = [i for i in knots]
    data["cvs"] = [(i.x, i.y, i.z) for i in cvs]
    data["degree"] = curve.degree
    data["form"] = curve.form
    return data


def createCurveShape(parent, data):
    """Create a specified nurbs curves based on the data

    :param parent: The transform that takes ownership of the shapes, if None is supplied then one will be created
    :type parent: MObject
    :param data: {"shapeName": {"cvs": [], "knots":[], "degree": int, "form": int}}
    :type data: dict
    :return: the parent node
    :rtype: MObject
    """
    if parent is None:
        parent = om2.MObject.kNullObj
    newCurve = om2.MFnNurbsCurve()
    created = []
    for shapeName, curveData in iter(data.items()):
        cvs = om2.MPointArray()
        for point in curveData["cvs"]:
            cvs.append(om2.MPoint(point))
        knots = curveData["knots"]
        degree = curveData["degree"]
        form = curveData["form"]
        enabled = curveData["overrideEnabled"]
        shape = newCurve.create(cvs, knots, degree, form, False, False, parent)
        if parent == om2.MObject.kNullObj and shape.apiType() == om2.MFn.kTransform:
            parent = shape
            shape = nodes.childPathAtIndex(om2.MFnDagNode(shape).getPath(), -1)
            shape = nodes.asMObject(shape)
        if enabled:
            plugs.setPlugValue(om2.MFnDependencyNode(shape).findPlug("overrideEnabled", False),
                               int(curveData["overrideEnabled"]))
            colours = curveData["overrideColorRGB"]
            nodes.setNodeColour(newCurve.object(), colours)
        created.append(shape)
    return parent


def serializeCurve(node, space=om2.MSpace.kObject):
    """From a given transform serialize the shapes curve data and return a dict

    :param node: The MObject that represents the transform above the nurbsCurves
    :type node: MObject
    :return: returns the dict of data from the shapes
    :rtype: dict
    """
    shapes = nodes.shapes(om2.MFnDagNode(node).getPath())
    data = {}
    for shape in shapes:
        dag = om2.MFnDagNode(shape.node())
        isIntermediate = dag.isIntermediateObject
        if not isIntermediate:
            data[om2.MNamespace.stripNamespaceFromName(dag.name())] = getCurveData(shape, space=space)

    return data


def mirrorCurveCvs(curveObj, axis="x", space=None):
    """Mirrors the the curves transform shape cvs by a axis in a specified space

    :param curveObj: The curves transform to mirror
    :type curveObj: mobject
    :param axis: the axis the mirror on, accepts: 'x', 'y', 'z'
    :type axis: str
    :param space: the space to mirror by, accepts: MSpace.kObject, MSpace.kWorld, default: MSpace.kObject
    :type space: int
    Example::
            >>>nurbsCurve = cmds.circle()[0]
            >>>mirrorCurveCvs(api.asMObject(nurbsCurve), axis='y', space=om.MSpace.kObject)
    """
    space = space or om2.MSpace.kObject

    axis = axis.lower()
    axisDict = {'x': 0, 'y': 1, 'z': 2}
    axis = axisDict[axis]

    shapes = nodes.shapes(om2.MFnDagNode(curveObj).getPath())
    for shape in shapes:
        curve = om2.MFnNurbsCurve(shape)
        cvs = curve.getCVs(space=space)
        copyCvs = om2.MPointArray()
        # invert the cvs MPoints based on the axis
        for i in range(len(cvs)):
            pt = cvs[i]
            pt[axis] *= -1
            copyCvs.append(pt)

        curve.setCvPositions(copyCvs)
        curve.updateCurve()


def iterCurvePoints(dagPath, count, space=om2.MSpace.kObject):
    """Generator Function to iterate and return the position, normal and tangent for the curve with the given point count.

    :param dagPath: the dagPath to the curve shape node
    :type dagPath: om2.MDagPath
    :param count: the point count to generate
    :type count: int
    :param space: the coordinate space to query the point data
    :type space: om2.MSpace
    :return: The first element is the Position, second is the normal, third is the tangent
    :rtype: tuple(MVector, MVector, MVector)
    """
    crvFn = om2.MFnNurbsCurve(dagPath)
    length = crvFn.length()
    dist = length / float(count - 1)  # account for end point
    current = 0.001
    maxParam = crvFn.findParamFromLength(length)
    for i in xrange(count):
        param = crvFn.findParamFromLength(current)
        # maya fails to get the normal when the param is the maxparam so we sample with a slight offset
        if param == maxParam:
            param = maxParam - 0.0001
        point = om2.MVector(crvFn.getPointAtParam(param, space=space))
        yield point, crvFn.normal(param, space=space), crvFn.tangent(param, space=space)
        current += dist


def iterCurveParams(dagPath, count):
    """Generator Function to iterate and return the Parameter

    :param dagPath: the dagPath to the curve shape node
    :type dagPath: om2.MDagPath
    :param count: the Number of params to loop
    :type count: int
    :return: The curve param value
    :rtype: float
    """
    crvFn = om2.MFnNurbsCurve(dagPath)
    length = crvFn.length()
    dist = length / float(count - 1)  # account for end point
    current = 0.001
    for i in xrange(count):
        yield crvFn.findParamFromLength(current)
        current += dist


def attachNodeToCurveAtParam(curve, node, param, name):
    """Attaches the given node to the curve using a motion path node.

    :param curve: nurbsCurve Shape to attach to
    :type curve: om2.MObject
    :param node: the node to attach to the curve
    :type node: om2.MObject
    :param param: the parameter float value along the curve
    :type param: float
    :param name: the motion path node name to use
    :type name: str
    :return: motion path node
    :rtype: om2.MObject
    """
    nodeFn = om2.MFnDependencyNode(node)
    crvFn = om2.MFnDependencyNode(curve)
    mp = nodes.createDGNode(name, "motionPath")
    mpFn = om2.MFnDependencyNode(mp)
    plugs.connectVectorPlugs(mpFn.findPlug("rotate", False), nodeFn.findPlug("rotate", False),
                             (True, True, True))
    plugs.connectVectorPlugs(mpFn.findPlug("allCoordinates", False), nodeFn.findPlug("translate", False),
                             (True, True, True))
    crvWorld = crvFn.findPlug("worldSpace", False)
    plugs.connectPlugs(crvWorld.elementByLogicalIndex(0), mpFn.findPlug("geometryPath", False))
    mpFn.findPlug("uValue", False).setFloat(param)
    mpFn.findPlug("frontAxis", False).setInt(0)
    mpFn.findPlug("upAxis", False).setInt(1)
    return mp


def iterGenerateSrtAlongCurve(dagPath, count, name):
    """Generator function to iterate the curve and attach transform nodes to the curve using a motionPath

    :param dagPath: the dagpath to the nurbscurve shape node
    :type dagPath: om2.MDagPath
    :param count: the number of transforms
    :type count: int
    :param name: the name for the transform, the motionpath will have the same name plus "_mp"
    :type name: str
    :return: Python Generator  first element is the created transform node, the second is the motionpath node
    :rtype: Generate(tuple(om2.MObject, om2.MObject))
    """
    curveNode = dagPath.node()
    for index, param in enumerate(iterCurveParams(dagPath, count)):
        transform = nodes.createDagNode(name, "transform")
        motionPath = attachNodeToCurveAtParam(curveNode, transform, param, "_".join([name, "mp"]))
        yield transform, motionPath
