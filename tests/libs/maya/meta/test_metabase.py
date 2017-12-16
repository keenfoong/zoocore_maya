from tests import mayatestutils

from zoo.libs.maya.meta import base
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import attrtypes
from maya.api import OpenMaya as om2


class TestMetaData(mayatestutils.BaseMayaTest):
    def setUp(self):
        self.meta = base.MetaBase(name="testNode")

    def test_hasDefaultAttributes(self):
        self.assertTrue(self.meta.mfn().hasAttribute("mClass"))
        self.assertEquals(self.meta.mfn().findPlug("mClass", False).asString(), self.meta.__class__.__name__)
        self.assertTrue(self.meta.hasAttribute("root"))
        self.assertTrue(self.meta.hasAttribute("uuid"))
        self.assertTrue(self.meta.hasAttribute("metaParent"))
        self.assertTrue(self.meta.hasAttribute("metaChildren"))
        self.assertFalse(self.meta.findPlug("root", False).asBool())

    def test_lockMetaManager(self):
        node = self.meta

        @base.lockMetaManager
        def test(node):
            self.assertFalse(node.mfn().isLocked)

        self.assertTrue(node.mfn().isLocked)
        test(node)
        self.assertTrue(node.mfn().isLocked)

    def test_renameAttribute(self):
        self.meta.renameAttribute("mClass", "bob")
        self.assertTrue(self.meta.mfn().hasAttribute("bob"))
        self.assertFalse(self.meta.mfn().hasAttribute("mClass"))

    def test_getAttribute(self):
        self.meta.addAttribute("test", 10.0, attrtypes.kMFnNumericDouble)
        self.assertIsNotNone(self.meta.getAttribute("test"))
        self.assertIsInstance(self.meta.getAttribute("test"), om2.MPlug)
        with self.assertRaises(AttributeError) as context:
            self.meta.testAttribute

    def test_name(self):
        self.assertEquals(self.meta.fullPathName(), "testNode_meta")
        self.assertEquals(base.MetaBase(nodes.createDagNode("transform1", "transform")).fullPathName(), "|transform1")

    def test_delete(self):
        self.meta.delete()

    def testLock(self):
        self.assertTrue(self.meta.mfn().isLocked)
        self.meta.lock(False)
        self.assertFalse(self.meta.mfn().isLocked)

    def test_rename(self):
        self.meta.rename("newName")
        self.assertEquals(self.meta.fullPathName(), "newName")

    def test_setattr(self):
        self.meta.uuid = "testClass"
        self.assertEquals(self.meta.uuid.asString(), "testClass")
        with self.assertRaises(TypeError):
            self.meta.uuid = 10
        child = base.MetaBase()
        self.meta.metaParent = child
        self.assertIsNotNone(child.metaParent())
        self.assertIsNotNone(self.meta.metaChildren())

    def test_addChild(self):
        newNode = nodes.createDagNode("test", "transform")
        newParent = base.MetaBase(newNode)
        self.meta.addChild(newParent)
        self.assertEquals(len(self.meta.metaChildren()), 1)
        self.assertEquals(self.meta.metaChildren()[0].mobject(), newParent.mobject())

    def test_addParent(self):
        newNode = nodes.createDagNode("test", "transform")
        newParent = base.MetaBase(newNode)
        self.meta.addParent(newParent)
        self.assertEquals(self.meta.metaParent().mobject(), newParent.mobject())

    def test_removeChild(self):
        newNode = nodes.createDagNode("test", "transform")
        newParent = base.MetaBase(newNode)
        self.meta.addParent(newParent)
        self.assertEquals(len(newParent.metaChildren()), 1)
        newParent.removeChild(self.meta)
        self.assertEquals(len(newParent.metaChildren()), 0)
        self.meta.addParent(newParent)
        self.assertEquals(len(newParent.metaChildren()), 1)
        newParent.removeChild(self.meta.mobject())
        self.assertEquals(len(newParent.metaChildren()), 0)

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
        self.assertTrue(len(parentMeta.metaChildren()), len(children))

        parent = parentMeta
        for child in children:
            child.removeParent()
            child.addParent(parent)
            parent = child
        self.assertEquals(len([i for i in parentMeta.iterMetaChildren(depthLimit=1)]), 1)
        # we hit a depth limit
        self.assertEquals(len([i for i in parentMeta.iterMetaChildren(depthLimit=100)]), 100)
        self.assertEquals(len([i for i in parentMeta.iterMetaChildren(depthLimit=len(children) + 1)]),
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
