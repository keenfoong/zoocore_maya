"""This module is for handling blendshapes in maya
@note, this needs a big update so right no one should use it until i've gotten around to fixing it.
"""

from maya.api import OpenMaya as om2

from zoo.libs.maya.api import nodes


class BlendShapeNode(object):
    """Abstracts maya's blendShape node and adds some high level functionality
    """

    def __init__(self, node):
        self.node = om2.MObjectHandle(node)
        self.mfn = om2.MFnDependencyNode(self.node.object())

        self.baseObjects = self._baseObjects()

    def _baseObjects(self):
        mfn = om2.MFnDependencyNode(self.node.object())
        bases = []
        geomPlug = mfn.findPlug("outputGeometry", False)
        for index in range(geomPlug.evaluateNumElements()):
            elementPlug = geomPlug.elementByPhysicalIndex(index)
            if elementPlug.isConnected:
                destinations = elementPlug.connectedTo(False, True)
                bases.extend([i.node() for i in destinations])
        if not bases:
            raise ValueError("No base objects found for specified blendshape node -> {}".format(self.mfn.name()))
        return bases

    def rename(self, name):
        nodes.rename(self.node.object(), name)

    def targetCount(self):
        return len(self.targets())

    def envelope(self):
        return self.mfn.findPlug("envelope", False).asFloat()

    def setEnvelope(self, value):
        self.mfn.findPlug("envelope", False).setFloat(value)

    def renameTarget(self, name, newName):
        idx = self.targetIdxByName(name)
        plug = self.mfn.findPlug("weight", False).elementByPhysicalIndex(idx)
        self.mfn.setAlias(newName, "weight[{}]".format(idx), plug)

    def iterTargetIndexPairs(self):
        weightArrayPlug = self.mfn.getAliasList()
        for alias, index in weightArrayPlug.evaluateNumElements():
            yield alias, index

    def targets(self, baseObjectIndex=0):
        """returns the mesh object for all connected targets
        """
        inputTargetGroup = self.mfn.findPlug("inputTarget", False).elementByPhysicalIndex(baseObjectIndex).child(0)
        targets = set()
        for element in range(inputTargetGroup.evaluateNumElements()):
            targetBasePlug = inputTargetGroup.elementByPhysicalIndex(element)
            inputTargetItem = targetBasePlug.child(0)
            for i in range(inputTargetItem.evaluateNumElements()):
                targetItemPlug = inputTargetItem.elementByPhysicalIndex(i).child(0)
                if targetItemPlug.isDestination:
                    targets.add(targetItemPlug.connectedTo(True, False)[0].node())
        return list(targets)

    def targetGroupPlug(self, targetIndex, baseObjectIndex=0):
        inputTargetGroup = self.mfn.findPlug("inputTarget", False).elementByPhysicalIndex(baseObjectIndex).child(0)

        if targetIndex in range(inputTargetGroup.evaluateNumElements()):
            return inputTargetGroup.elementByPhysicalIndex(targetIndex)

    def targetInbetweenPlug(self, targetIndex, logicalIndex, baseObjectIndex=0):
        targetItemGroup = self.targetGroupPlug(targetIndex, baseObjectIndex).child(0)
        indices = targetItemGroup.getExistingArrayAttributeIndices()
        if logicalIndex in indices:
            return targetItemGroup.elementByLogicalIndex(logicalIndex)

    def targetIdxByName(self, name):
        name = name
        for alias, idx in self.iterTargetIndexPairs():
            if alias == name:
                return idx
        raise AttributeError("target doesn't exist")

    def targetInbetweenName(self, targetIndex, logicalIndex):
        infoGroupPlug = self.mfn.findPlug("inbetweenInfoGroup")
        existinginbetweenIndices = infoGroupPlug.getExistingArrayAttributeIndices()
        if targetIndex in existinginbetweenIndices:
            inbetweenInfoPlug = infoGroupPlug.elementByLogicalIndex(targetIndex).child(0)
            inbetweenLogicalIndices = inbetweenInfoPlug.getExistingArrayAttributeIndices()
            if logicalIndex in inbetweenLogicalIndices:
                namePlug = inbetweenInfoPlug.elementByLogicalIndex(logicalIndex).child(1)
                return namePlug.asString()
        return ""

    def setTargetInbetweenName(self, name, targetIndex, logicalIndex):
        infoGroupPlug = self.mfn.findPlug("inbetweenInfoGroup")
        existinginbetweenIndices = infoGroupPlug.getExistingArrayAttributeIndices()
        if targetIndex in existinginbetweenIndices:
            inbetweenInfoPlug = infoGroupPlug.elementByLogicalIndex(targetIndex).child(0)
            inbetweenLogicalIndices = inbetweenInfoPlug.getExistingArrayAttributeIndices()
            if logicalIndex in inbetweenLogicalIndices:
                namePlug = inbetweenInfoPlug.elementByLogicalIndex(logicalIndex).child(1)
                namePlug.setString(name)
        return ""

    def targetIndexWeights(self, targetIndex, baseObjectIndex=0):
        """will return a list of weight values for all the inbetween shapes for a given target
        """
        groupPlug = self.targetGroupPlug(targetIndex, baseObjectIndex)

        weights = []
        inputTargetItemPlug = groupPlug.child(0)
        for i in range(inputTargetItemPlug.evaluateNumElements()):
            plug = inputTargetItemPlug.elementByPhysicalIndex(i)
            weights.append((plug.logicalIndex - 5000) * 0.001)

        return weights

    def targetWeights(self):
        weightPlug = self.mfn.findPlug("weight", False)
        weights = []
        for i in range(weightPlug.evaluateNumElements()):
            plug = weightPlug.elementByPhysicalIndex(i)
            weights.append(plug.logicalIndex(), plug.asFloat())
        return weights

    def targetPaintWeights(self, targetIndex, baseObjectIndex=0):
        groupPlug = self.targetGroupPlug(targetIndex, baseObjectIndex)
        weightArray = groupPlug.child(1)
        weights = set()
        for i in weightArray.getExistingArrayAttributeIndices():
            weights.add(i, weightArray.elementByLogicalIndex(i).asFloat())

        return weights

    def basePaintWeights(self, baseObjectIndex=0):
        inputTargetPlug = self.mfn.findPlug("inputTarget", False).elementByPhysicalIndex(baseObjectIndex)
        weightsPlug = inputTargetPlug.child(1)
        weights = set()
        for i in weightsPlug.getExistingArrayAttributeIndices():
            weights.add(i, weightsPlug.elementByLogicalIndex(i).asFloat())
        return weights

    def setTargetWeights(self, weightList):
        weightPlug = self.mfn.findPlug("weight", False)
        logicalIndices = weightPlug.getExistingArrayAttributeIndices()
        if not logicalIndices:
            return
        for idx, value in weightList:
            if idx in logicalIndices:
                weightPlug.elementByLogicalIndex(idx).setFloat(value)

    def setTargetWeightValue(self, targetIndex, value):
        weightPlug = self.mfn.findPlug("weight", False)
        if targetIndex in range(weightPlug.evaluateNumElements()):
            targetPlug = weightPlug.elementByPhysicalIndex(targetIndex)
            if not targetPlug.isDefaultValue():
                weightPlug.elementByLogicalIndex(targetIndex).setFloat(value)

    def setBasePaintWeights(self, weightList, baseObjectIndex=0):
        inputTargetPlug = self.mfn.findPlug("inputTarget", False).elementByPhysicalIndex(baseObjectIndex)
        weightsPlug = inputTargetPlug.child(1)
        for index, value in weightList:
            weightsPlug = weightsPlug.elementByLogicalIndex(index)
            weightsPlug.setFloat(value)

    def setTargetPaintWeights(self, weightList, targetIndex, baseObjectIndex=0):
        groupPlug = self.targetGroupPlug(targetIndex, baseObjectIndex)
        weightArray = groupPlug.child(1)
        for index, value in weightList:
            weightsPlug = weightArray.elementByLogicalIndex(index)
            weightsPlug.setFloat(value)

    def addTarget(self):
        pass

    def extract(self, targetIndex):
        pass

    def extractAll(self):
        pass

    def transfer(self, method="direct"):
        pass

    def transferPartial(self, polyGroup):
        pass


class TargetExtractContext(object):
    def __init__(self, blend):
        self.blendshapeNode = blend
        self.connectedPlugs = set()
        self.plugs = set()

    def __enter__(self):
        weightPlug = self.blendshapeNode.mfn.findPlug("weight", False)
        self.weightList = self.blendshapeNode.targetWeights()

        for i in range(weightPlug.evaluateNumElements()):
            plug = weightPlug.elementByPhysicalIndex(i)
            if plug.isConnected and plug.isDestination:
                self.connectedPlugs.add((plug, plug.connectedTo(True, False)))
            self.blendshapeNode.setTargetWeightValue(i, 0.0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        mod = om2.MDGModifier()
        weightPlug = self.blendshapeNode.findPlug("weight", False)
        for plugIdx, value, in self.plugs:
            mod.newPlugValueFloat(weightPlug.elementByLogicalIndex(plugIdx), value)
        for connectedPlug in self.connectedPlugs:
            for source in connectedPlug[1]:
                mod.connect(source, connectedPlug[0])
        mod.doIt()
