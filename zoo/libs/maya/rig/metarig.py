from zoo.libs.utils import general
from maya.api import OpenMaya as om2

from zoo.libs.maya.meta import base


class MetaRigBase(base.MetaBase):
    icon = "user"
    _ctrlPrefix = "CTRL"
    _jntPrefix = "JNT"
    _skinJntPrefix = "SKIN"
    _geoPrefix = "GEO"
    _proxyGeoPrefix = "GEO_PROXY"
    SUPPORTSYSTEMATTR = "supportSystem"
    SUBSYSTEMATTR = "subSystem"

    def addControl(self, node, name):
        attrname = "_".join([self._ctrlPrefix, name])
        return self.connectTo(attrname, node)

    def addJoint(self, node, name):
        attrname = "_".join([self._jntPrefix, name])
        return self.connectTo(attrname, node)

    def addSkinJoint(self, node, name):
        attrname = "_".join([self._skinJntPrefix, name])
        return self.connectTo(attrname, node)

    def addProxyGeo(self, node, name):
        attrname = "_".join([self._proxyGeoPrefix, name])
        return self.connectTo(attrname, node)

    def addGeo(self, node, name):
        attrname = "_".join([self._geoPrefix, name])
        return self.connectTo(attrname, node)

    def proxyGeo(self, recursive=True):
        return self.findConnectedNodesByAttributeName(self._proxyGeoPrefix, recursive=recursive)

    def addIkJoint(self, joint, name):
        self.addJoint(joint, "_".join([self._ikPrefix, name, "jnt"]))

    def addFkJoint(self, joint, name):
        self.addJoint(joint, "_".join([self._fkPrefix, name, "jnt"]))

    def addIkControl(self, ctrl, name):
        self.addControl(ctrl, "_".join([self._ikPrefix, name, "anim"]))

    def addFkControl(self, ctrl, name):
        self.addControl(ctrl, "_".join([self._fkPrefix, name, "anim"]))

    def control(self, name, recursive):
        results = self.findConnectedNodesByAttributeName("_".join([self._ctrlPrefix, name]), recursive=recursive)
        if results:
            return results[0]
        return None

    def controls(self, recursive=True):
        return self.findConnectedNodesByAttributeName(self._ctrlPrefix, recursive=recursive)

    def joints(self, recursive=True):
        return self.findConnectedNodesByAttributeName(self._jntPrefix, recursive=recursive)

    def skinJoints(self, recursive):
        return self.findConnectedNodesByAttributeName(self._skinJntPrefix, recursive=recursive)

    def geo(self, recursive=True):
        return self.findConnectedNodesByAttributeName(self._geoPrefix, recursive=recursive)

    def filterSubSystemByName(self, name):
        for subsys in iter(self.subSystems()):
            if subsys.name.asString() == name:
                return subsys
        return None

    def filterSupportSystemByName(self, name):
        for subsys in iter(self.supportSystems()):
            if subsys.name.asString() == name:
                return subsys
        return None

    def isSubSystem(self):
        return isinstance(self, MetaSubSystem)

    def isSupportSystem(self):
        return isinstance(self, MetaSupportSystem)

    def hasSupportSystemByName(self, name):
        for subsys in iter(self.supportSystems()):
            if subsys.name.asString() == name:
                return True
        return False

    def hasSubSystemName(self, name):
        for subsys in iter(self.subSystems()):
            if subsys.name.asString() == name:
                return True
        return False

    def addSupportSystem(self, node=None, name=None):
        if node is None:
            name = "{}_#".format(MetaRig.SUPPORTSYSTEMATTR) if not name else "_".join([name, "meta"])
            node = MetaSupportSystem(name=name).object()
        elif isinstance(node, om2.MObject):
            node = MetaSupportSystem(node)

        self.connectTo(MetaRig.SUPPORTSYSTEMATTR, node.mobject(), base.MPARENT_ATTR_NAME)

        return node

    def addSubSystem(self, node=None, name=None):
        if node is None:
            node = MetaSubSystem(name=name)
        elif isinstance(node, om2.MObject):
            node = MetaSubSystem(node)

        self.connectTo(MetaRig.SUBSYSTEMATTR, node.mobject(), base.MPARENT_ATTR_NAME)

        return node

    def supportSystems(self):
        if isinstance(self, MetaSupportSystem):
            return
        return list(self.iterSupportSystems())

    def iterSupportSystems(self):
        if isinstance(self, MetaSubSystem) or self._mfn.hasAttribute(MetaRig.SUPPORTSYSTEMATTR):
            return
        plug = self._mfn.findPlug(MetaRig.SUPPORTSYSTEMATTR, False)
        if not plug.isSource:
            return
        connections = plug.destinations()
        for i in connections:
            yield MetaSupportSystem(i.node())

    def iterSubSystems(self):
        if isinstance(self, MetaSubSystem) or not self._mfn.hasAttribute(MetaRig.SUBSYSTEMATTR):
            return
        plug = self._mfn.findPlug(MetaRig.SUBSYSTEMATTR, False)
        if not plug.isSource:
            return
        connections = plug.destinations()
        for i in connections:
            yield MetaSubSystem(i.node())

    def subSystems(self):
        if isinstance(self, MetaSubSystem):
            return
        return list(self.iterSubSystems())


class MetaRig(MetaRigBase):
    pass


class MetaSupportSystem(MetaRigBase):
    def __init__(self, node=None, name=None, initDefaults=True):
        super(MetaSupportSystem, self).__init__(node, name, initDefaults)


class MetaSubSystem(MetaRigBase):
    def __init__(self, node=None, name="", initDefaults=True):
        super(MetaSubSystem, self).__init__(node, name, initDefaults)


class MetaFaceRig(MetaRigBase):
    def __init__(self, node=None, name="", initDefaults=True):
        super(MetaFaceRig, self).__init__(node, name, initDefaults)


def findDuplicateRigInstances():
    """Searches all MetaRigs and checks the rigName for duplicates.

    :return: list of duplicate metaRig instances.
    :rtype: list(MetaRig)
    """
    metaRigs = [(i, i.rigName) for i in findRigs()]
    duplicates = general.getDuplicates([i[1] for i in metaRigs])
    return [i[0] for i in metaRigs if i in duplicates]


def findRigs():
    return base.findMetaNodesByClassType(MetaRig.__name__)
