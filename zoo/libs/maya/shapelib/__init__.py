"""This module holds utility methods for dealing with nurbscurves
"""
import os
from zoo.libs.utils import file

from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import curves


def iterAvailableShapesNames():
    """Generator function for looping over all available shape names
    :return:
    :rtype:
    """
    lib = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
    for f in iter(os.listdir(lib)):
        if f.endswith("shape"):
            yield os.path.splitext(f)[0]


def shapeNames():
    return list(iterAvailableShapesNames())


def loadFromLib(shapeName, parent=None):
    """Loads the data for the given shape Name

    :param shapeName: The shape name from the library, excluding the extension
    :type shapeName: str
    :param parent: if specified then this function will also create the shapes under the parent
    :type parent: MObject
    :return: Returns the data from the library or the MObject of the parent
    :rtype: dict or MObject
    :raises ValueError
    """
    lib = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
    for f in iter(os.listdir(lib)):
        if not f.endswith("shape"):
            continue
        name = os.path.splitext(f)[0]
        if name == shapeName:
            data = file.loadJson(os.path.join(os.path.normpath(lib), f))
            if parent is not None and data:
                return curves.createCurveShape(parent, data)
            if data:
                return data
    raise ValueError("The shape name '{}' doesn't exist in the library".format(shapeName))


def loadAndCreateFromLib(shapeName, parent=None):
    """Load's and create's the nurbscurve from the shapelib.

    :param shapeName: the shape library name.
    :type shapeName: str
    :param parent: the parent for the nurbscurve default is None.
    :type parent: om2.MObject
    :return: the create transform for the nurbscurve.
    :rtype: om2.MObject
    """
    newData = loadFromLib(shapeName, parent)
    if parent is None:
        return curves.createCurveShape(parent, newData)
    return newData


def saveToLib(node, name, override=True):
    """Save's the current transform node shapes to the zoo library, used internally for zoo.

    :param node:The mobject to the transform that you want to save
        :type node: MObject
    :param name: the name of the file to create, if not specified the node name will be used
    :type name: str
    :return: The file path to the newly created shape file
    :rtype: str

    Example::
        >>>nurbsCurve = cmds.circle()[0]
        # requires an MObject of the shape node
        >>>data, path = saveToLib(api.asMObject(nurbsCurve))
    """
    if name is None:
        name = nodes.nameFromMObject(node)
    if not name.endswith(".shape"):
        name = ".".join([name, "shape"])
    data = curves.serializeCurve(node)

    lib = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
    if override:
        names = [f for f in iterAvailableShapesNames()]
        if name in names:
            raise ValueError("name-> {} already exists in the shape library!".format(name))
    path = os.path.join(lib, name)
    file.saveJson(data, path)

    return data, path
