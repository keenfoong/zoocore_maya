from tests import mayatestutils

from zoo.libs.maya.meta import base
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import attrtypes
from maya.api import OpenMaya as om2


class TestMetaData(mayatestutils.BaseMayaTest):
    def setUp(self):
        self.meta = base.MetaBase(name="testNode", lock=True)

    def test_hasDefaultAttributes(self):
        self.assertTrue(self.meta.mfn().hasAttribute(base.MCLASS_ATTR_NAME))
        self.assertEquals(self.meta.mfn().findPlug(base.MCLASS_ATTR_NAME, False).asString(), self.meta.__class__.__name__)
        self.assertTrue(self.meta.hasAttribute(base.MPARENT_ATTR_NAME))
        self.assertTrue(self.meta.hasAttribute(base.MCHILDREN_ATTR_NAME))

    def test_lockMetaManager(self):
        node = self.meta

        @base.lockMetaManager
        def test(node):
            self.assertFalse(node.mfn().isLocked)

        self.assertTrue(node.mfn().isLocked)
        test(node)
        self.assertTrue(node.mfn().isLocked)

    def test_renameAttribute(self):
        self.meta.renameAttribute(base.MCLASS_ATTR_NAME, "bob")
        self.assertTrue(self.meta.mfn().hasAttribute("bob"))
        self.assertFalse(self.meta.mfn().hasAttribute(base.MCLASS_ATTR_NAME))

    def test_getAttribute(self):
        self.meta.addAttribute("test", 10.0, attrtypes.kMFnNumericDouble)
        self.assertIsNotNone(self.meta.attribute("test"))
        self.assertIsInstance(self.meta.attribute("test"), om2.MPlug)
        with self.assertRaises(AttributeError) as context:
            self.meta.testAttribute

    def test_name(self):
        self.assertEquals(self.meta.fullPathName(), "testNode_meta")
        self.assertEquals(base.MetaBase(nodes.createDagNode("transform1", "transform")).fullPathName(), "|transform1")

    def test_delete(self):
        self.meta.delete()

    def testLock(self):
        self.meta.lock(True)
        self.assertTrue(self.meta.mfn().isLocked)
        self.meta.lock(False)
        self.assertFalse(self.meta.mfn().isLocked)

    def test_rename(self):
        self.meta.rename("newName")
        self.assertEquals(self.meta.fullPathName(), "newName")

    def test_setattr(self):
        self.meta.addAttribute("testAttr", "", attrtypes.kMFnDataString)
        self.assertEquals(self.meta.testAttr.asString(), "")
        self.meta.testAttr = "testClass"
        self.assertEquals(self.meta.testAttr.asString(), "testClass")
        with self.assertRaises(TypeError):
            self.meta.testAttr = 10
        child = base.MetaBase()
        child.addParent(self.meta)
        self.assertIsInstance(list(child.metaParents())[0], base.MetaBase)
        self.assertIsInstance(list(self.meta.iterMetaChildren())[0], base.MetaBase)

    def test_addChild(self):
        newNode = nodes.createDagNode("test", "transform")
        newParent = base.MetaBase(newNode)
        self.meta.addChild(newParent)
        self.assertEquals(len(list(self.meta.iterMetaChildren())), 1)
        self.assertEquals(list(self.meta.iterMetaChildren())[0].mobject(), newParent.mobject())

    def test_addParent(self):
        newNode = nodes.createDagNode("test", "transform")
        newParent = base.MetaBase(newNode)
        self.meta.addParent(newParent)
        self.assertEquals(list(self.meta.metaParents())[0].mobject(), newParent.mobject())

    def test_removeParent(self):
        newNode = nodes.createDagNode("test", "transform")
        newParent = base.MetaBase(newNode)
        self.meta.addParent(newParent)
        self.assertEquals(len(list(newParent.iterMetaChildren())), 1)
        self.meta.removeParent(newParent)
        self.assertEquals(len(list(newParent.iterMetaChildren())), 0)
        self.meta.addParent(newParent)
        self.assertEquals(len(list(newParent.iterMetaChildren())), 1)
        self.meta.removeParent(newParent)
        self.assertEquals(len(list(newParent.iterMetaChildren())), 0)

    def test_iterMetaChildren(self):
        childOne = base.MetaBase(nodes.createDagNode("child", "transform"))
        childTwo = base.MetaBase(nodes.createDagNode("child1", "transform"))
        childThree = base.MetaBase(nodes.createDagNode("child2", "transform"))
        self.meta.addChild(childOne)
        childOne.addChild(childTwo)
        childTwo.addChild(childThree)
        iterchildren = [i for i in self.meta.iterMetaChildren()]
        nonChildren = [i for i in self.meta.iterMetaChildren(depthLimit=1)]
        self.assertEquals(len(nonChildren), 1)
        self.assertEquals(len(iterchildren), 3)
        selection = [childOne, childTwo, childThree]
        # non recursive
        self.assertTrue(nonChildren[0] in nonChildren)
        for i in selection:
            self.assertTrue(i in iterchildren)
            selection.remove(i)

    def test_iterMetaChildrenLargeNetwork(self):
        # large network
        children = []
        parentMeta = base.MetaBase(nodes.createDGNode("parentMeta", "network"))
        # to test connecting multiple nodes to a single parent
        for i in range(100):
            child = base.MetaBase(nodes.createDGNode("child{}".format(i), "network"))
            parentMeta.addChild(child)
            children.append(child)
        self.assertTrue(len(list(parentMeta.iterMetaChildren())), len(children))

        parent = parentMeta
        for child in children:
            child.removeParent()
            child.addParent(parent)
            parent = child
        self.assertEquals(len(list(parentMeta.iterMetaChildren(depthLimit=1))), 1)
        # we hit a depth limit
        self.assertEquals(len(list(parentMeta.iterMetaChildren(depthLimit=100))), 100)
        self.assertEquals(len(list(parentMeta.iterMetaChildren(depthLimit=len(children) + 1))),
                          len(children))

    # def test_findPlugsByFilteredName(self):
    #     pass
    #
    # def test_findPlugsByType(self):
    #     pass
    #
    # def test_iterAttributes(self):
    #     pass
    #
    # def classNameFromPlug(node):
    #     pass
    #
    # def test_constructor(cls, *args, **kwargs):
    #     pass
    #
    # def test_equals(self, other):
    #     pass
    #
    # def test_metaClassPlug(self):
    #     pass
    #
    # def test_exists(self):
    #     pass
    #
    # def test_removeAttribute(self, name):
    #     pass
    #
    # def test_findConnectedNodes(self, attributeName="", filter=""):
    #     pass
    #
    # def test_serialize(self):
    #     pass
