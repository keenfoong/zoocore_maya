ZOOCORE MAYA
============
Zoo Core Maya is all about Autodesk Maya general operation's.

In ZooTools we focus on developing code which is efficient as possible(limiting to python) with a functional design where preferred.
To achieve such a thing we utilize OpenMaya 2.0 as much as possible and only use the cmds module where the operation
is faster and returns the correct data. For Example if a command returns obj names we'll use om2 instead since node
paths are trash in cmds.
Of coarse moving to OpenMaya 2.0 has a small problem when doing maya state changes, for example setting attribute values nodes we don't get
undo/redo functionality. So we created Zoo Maya Command framework.

Version Support
---------------
Currently tested and only supporting:
- Maya 2017 update 4+
- Maya 2018+
- Maya 2019

We don't intend to support older version of maya and we are likely to deprecated 2017 in the next year.


