"""
:todo:: test cvs
"""
from maya import cmds
from maya.api import OpenMaya as om2

from tests import mayatestutils
from zoo.libs.maya.api import nodes, plugs
from zoo.libs.maya.rig import control


class TestControl(mayatestutils.BaseMayaTest):
    def test_init(self):
        con = control.Control(name="testControl")
        self.assertEquals(con.colour, (0, 0, 0))
        self.assertEquals(con.name, "testControl")
        curve = cmds.circle(ch=False)[0]
        con = control.Control(node=nodes.asMObject(curve))
        self.assertTrue(cmds.objExists(con.dagPath.fullPathName()))

    def test_createControlFromLib(self):
        con = control.Control(name="testControl")
        node = con.create(shape="arrow")
        cmds.objExists(node.fullPathName())
        self.assertEquals(node.partialPathName(), "testControl")

    def test_setPosition(self):
        con = control.Control(name="testControl")
        con.create(shape="arrow")
        con.setPosition(om2.MVector(10, 10, 10))
        trans = nodes.getTranslation(con.dagPath.node())
        self.assertEquals(trans, om2.MVector(10, 10, 10))
        con.setPosition(om2.MVector(-10, -10, -10), cvs=True)
        # probably should test the cv locations
        self.assertEquals(trans, om2.MVector(10, 10, 10))

    def test_setRotation(self):
        con = control.Control(name="testControl")
        con.create(shape="arrow")
        con.setRotation(om2.MEulerRotation(10, 10, 10))
        trans = om2.MFnTransform(con.dagPath.node())
        rot = trans.rotation()
        self.assertEquals(rot, om2.MEulerRotation(10, 10, 10))
        con.setRotation(om2.MEulerRotation(-10, -10, -10), cvs=True)
        # probably should test the cv locations
        self.assertEquals(trans.rotation(), om2.MEulerRotation(10, 10, 10))

    def test_setScale(self):
        con = control.Control(name="testControl")
        con.create(shape="arrow")
        con.setScale((2, 2, 2))
        trans = om2.MFnTransform(con.dagPath.node())
        self.assertEquals(trans.scale(), [2, 2, 2])
        con.setScale((2, 2, 2), cvs=True)

    def test_setRotationOrder(self):
        con = control.Control(name="testControl")
        con.create(shape="arrow")
        con.setRotationOrder(om2.MTransformationMatrix.kXZY)
        self.assertEqual(plugs.getPlugValue(om2.MFnDependencyNode(con.mobject()).findPlug("rotateOrder", False)),
                         om2.MTransformationMatrix.kXZY)

    def test_setPivot(self):
        raise ValueError("no test")

    def test_setColour(self):
        raise ValueError("no test")

    def test_addSrt(self):
        con = control.Control(name="testControl")
        con.create(shape="arrow")
        con.addSrtBuffer("testNode")
        self.assertTrue(nodes.hasParent(con.dagPath.node()))
        parent = con.dagPath.pop()
        self.assertTrue(parent.partialPathName().endswith("_testNode"))
