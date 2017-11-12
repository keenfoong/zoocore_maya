"""
@todo hassrt method
"""
from maya import cmds
from maya.api import OpenMaya as om2
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import generic
from zoo.libs.maya.api import curves
from zoo.libs.maya import shapelib


class Control(object):
    """This Control class wraps the common functionality on a rig control. The class allows for creation of loading
    of curve shapes from the zoo shape library. you can use addSrt() to add a part transform.
    :note: transformations to most likely be on the srt as thats the preferred method in rigging
    """

    def __init__(self, node=None, name=""):
        """
        :param name:The name of the curve, can be an existing node transform
        :type name: str
        """
        self._name = name
        if node is not None:
            self.dagPath = om2.MFnDagNode(node).getPath()
            self._name = self.dagPath.partialPathName()
        else:
            self.dagPath = None
        self.srt = None

    def __repr__(self):
        result = "name: {0}, colour: {0}".format(self.name if not self.dagPath else self.dagPath.fullPathName(),
                                                 self.colour)
        return result

    @property
    def name(self):
        """Returns the full path name for the control

        :rtype: str
        """
        if self.dagPath is not None:
            return self.dagPath.fullPathName()
        return self._name

    def exists(self):
        return self.dagPath is not None and self.dagPath.isValid()

    def mobject(self):
        """Returns the mobject from the dagPath node

        :rtype: mobject
        """
        if self.dagPath is not None:
            return self.dagPath.node()

    def setParent(self, parent, maintainOffset=False):
        if self.srt is not None:
            nodes.setParent(self.srt.object(), parent, maintainOffset=maintainOffset)
            return
        nodes.setParent(self.mobject(), parent, maintainOffset=maintainOffset)

    def addSrtBuffer(self, suffix="", parent=None):
        """Adds a parent transform to the curve transform

        :param suffix: the suffix that this transform will get, eg name: self.name_suffix
        :type suffix: str
        :return: the newly created node
        :rtype: mobject
        """

        if self.dagPath is None:
            return
        ctrlPat = nodes.getParent(self.mobject())
        newSrt = nodes.createDagNode("_".join([self.name, suffix]), "transform", ctrlPat)
        nodes.setMatrix(newSrt, nodes.getWorldMatrix(self.mobject()))

        if parent is not None:
            nodes.setParent(newSrt, parent, True)
        nodes.setParent(self.mobject(), newSrt, True)
        self.srt = om2.MObjectHandle(newSrt)
        return newSrt

    def parent(self):
        return self.dagPath.pop().node()

    def create(self, shape=None, position=None, rotation=None, scale=(1, 1, 1), rotationOrder=0, color=None):
        """This method creates a new set of curve shapes for the control based on the shape type specified.
         if the self.node already initialized then this node will become the parent. this method has basic functionality
         for transformation if you need more control use the other helper method on this class.

        :param shape: The shape type to create should be present in the shape library
        :type shape: str
        :param position: The position to set the control at, if not specified the control will be created at 0,0,0
        :type position: MVector
        :param rotation: the rotation for the control, if not specified the control with rotation 0,0,0
        :type rotation: MEulerRotation or MQuaterion
        :param scale: the scale for the control, if not specified the control will be created at 1,1,1
        :type scale: sequence
        :param rotationOrder: the rotation eg. MEulerRotation.kXYZ
        :type rotationOrder: int
        :return: The newly created control transform
        :rtype: mobject
        """
        if not self._name:
            self._name = "control_new"
        if not self.dagPath:
            self.dagPath = nodes.createDagNode(self._name, "transform")
        if isinstance(shape, basestring):
            self.dagPath = om2.MFnDagNode(shapelib.loadFromLib(shape, parent=self.dagPath)).getPath()
        else:
            self.dagPath = om2.MFnDagNode(curves.createCurveShape(self.dagPath, shape)).getPath()

        if self.dagPath is None:
            raise ValueError("Not a valid shape name %s" % shape)
        if position is not None:
            self.setPosition(position, space=om2.MSpace.kWorld)
        if rotation is not None:
            self.setRotation(rotation)
        if scale != (1, 1, 1) and scale:
            self.setScale(scale, space=om2.MSpace.kWorld)
        if color is not None:
            self.setColour(color, 0)
        self.setRotationOrder(rotationOrder)
        return self.dagPath

    def addShapeFromLib(self, shapeName):
        if shapeName in shapelib.shapeNames():
            shapelib.loadFromLib(shapeName, parent=self.mobject())
            return True
        return False

    def addShapeFromData(self, shapeData):
        return curves.createCurveShape(self.dagPath, shapeData)

    def setPosition(self, position, cvs=False, space=None, useParent=True):
        """Sets the translation component of this control, if cvs is True then translate the cvs instead

        :param position: The MVector that represent the position based on the space given.
        :type position: MVector
        :param cvs: If true then the MVector will be applied to all cvs
        :type cvs: bool
        :param space: the space to work on eg.MSpace.kObject or MSpace.kWorld
        :type space: int
        """
        space = space or om2.MSpace.kTransform
        if self.dagPath is None:
            return
        if cvs:
            dag = om2.MFnDagNode(self.dagPath)
            dagPath = dag.getPath()
            shapes = nodes.childPaths(dagPath)
            for i in shapes:
                cvsPositions = nodes.cvPositions(i, space=space)
                newPositions = om2.MPointArray()
                for pnt in cvsPositions:
                    newPositions.append(om2.MPoint(pnt.x * position.x, pnt.y * position.y, pnt.z * position.z))
                nodes.setCurvePositions(i, newPositions, space=space)
        if useParent:
            parent = nodes.getParent(self.dagPath.node())
            if parent:
                nodes.setTranslation(parent, position, space)
                return
        nodes.setTranslation(self.dagPath.node(), position, space)

    def setRotation(self, rotation, space=om2.MSpace.kTransform, cvs=False):
        """Set's the rotation on the transform control using the space.

        :param rotation: the eulerRotation to rotate the transform by
        :type rotation: om.MEulerRotation or MQuaternion or seq
        :param space: the space to work on
        :type space: om.MSpace
        :param cvs: if true then the rotation will be applied to the cv components
        :type cvs: bool
        :todo:: api for cv rotation
        """
        if self.dagPath is None:
            return
        if cvs:
            # uber temp should be api, just need to get to it
            cmds.rotate(rotation.x, rotation.y, rotation.z,
                        cmds.ls(om2.MFnDagNode(self.dagPath).fullPathName() + ".cv[*]"))
            return
        trans = om2.MFnTransform(self.dagPath)
        if isinstance(rotation, (list, tuple)):
            rotation = generic.asEuler(rotation).asQuaternion()
        trans.setRotation(rotation, space)

    def setScale(self, scale, cvs=False, space=None):
        """Applies the specified scale vector to the transform or the cvs

        :param space: the space to work on, eg. MSpace.kWorld
        :type scale: sequence
        :type space: int
        :param cvs: if True then the scaling vector will be applied to the cv components
        :type cvs: bool
        """
        if self.dagPath is None:
            return
        space = space or om2.MSpace.kObject
        if cvs:
            shapes = nodes.shapes(self.dagPath)
            for shape in shapes:
                curve = om2.MFnNurbsCurve(shape)
                positions = curve.cvPositions(space)
                newPositions = om2.MPointArray()
                for i in positions:
                    newPositions.append(om2.MPoint(i[0] * scale[0], i[1] * scale[1], i[2] * scale[2]))
                nodes.setCurvePositions(shape.node(), newPositions, space=space)
            return

        trans = om2.MFnTransform(self.dagPath)
        trans.setScale(scale)

    def setColour(self, colour, shapeIndex=None):
        """

        :param colour:
        :type colour:
        :param shapeIndex:
        :type shapeIndex: int or None
        :rtype: tuple(str, int, dict)
        """
        if self.dagPath is None:
            return

        if shapeIndex is not None:
            # do all shapes
            if shapeIndex == 0:
                shapes = nodes.shapes(self.dagPath)
                for shape in shapes:
                    nodes.setNodeColour(shape.node(), colour)
            else:
                shape = nodes.shapeAtIndex(self.dagPath.node(), shapeIndex)
                nodes.setNodeColour(shape.node, colour)
            return
        nodes.setNodeColour(self.dagPath.node(), colour)

    def setRotationOrder(self, rotateOrder=None):
        """Sets rotation order for the control

        :param rotateOrder: om.MTransformationMatrix.kXYZ
        :type rotateOrder: int
        """
        if self.dagPath is None:
            return
        if rotateOrder is None:
            rotateOrder = om2.MTransformationMatrix.kXYZ
        else:
            rotateOrder = generic.intToMTransformRotationOrder(rotateOrder)
        trans = om2.MFnTransform(self.dagPath)
        trans.setRotationOrder(rotateOrder, True)

    def setPivot(self, vec, type_=("t", "r", "s"), space=None):
        """
        :param vec:
        :type vec: om.MVector
        :param type_:
        :type type_: sequence
        :param space:
        :type space: int
        """
        if self.dagPath is None:
            return
        space = space or om2.MSpace.kObject
        transform = om2.MFnTransform(self.dagPath)
        if "t" in type_:
            transform.setScalePivotTranslation(vec, space)
        if "r" in type_:
            transform.setRotatePivot(vec, space)
        if "s" in type_:
            transform.setScalePivot(vec, space)
