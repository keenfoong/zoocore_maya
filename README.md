ZOOCORE MAYA
============
Zoo Core Maya is all about Autodesk Maya general operation's.

In ZooTools we focus on developing code which is efficient as possible(limiting to python) with a functional design where preferred.
To achieve such a thing we utilize OpenMaya 2.0 as much as possible and only use the cmds module where the operation
is faster and returns the correct data. For Example if a command returns obj names we'll use om2 instead since node
paths are trash in cmds.
Of coarse moving to OpenMaya 2.0 has a small problem when doing maya state changes, for example setting attribute values nodes we don't get
undo/redo functionality. So we created Zoo Maya Command framework [See below](#Zoo-Maya-command)




Version Support
---------------
Currently tested and only supporting:
- Maya 2017 update 4+
- Maya 2018+

We don't intend to support older version of maya and we are likely to deprecated 2017 in the next year.


Feature's
---------
#### Zoo Maya command


Exact same as the standalone version but integrated into maya's command engine. Standalone commands will still be usable
inside maya, if a command is undoable then it will be part of maya internal undostack.
Maya commands are a thin wrapper around the MPxCommand so we maintain the undo/redo feature's but we extended the possibilities
with maya by allowing for arbitrary data types to be passed to and from commands eg. om2.MObject. we only support using
om2, cmds and pure python, no om1 code as per maya documentation.
A few design decision have been made to simplify command creation.

- Only the doIt and undoIt methods need to be implemented.
- Zoo handles the registry of supported commands and only one plugin is registered to maya which is the undo.py in zoo.
- User's only need to tell zoo executor instance about the command location(Environment variable), no need for the initializePlugin().
- Minimal differences between MPxCommand and Zoocommand
- maya's undo/redo stacks and zooCommands stacks are synced via the custom MPx.
- ZooCommands support passing api objects and any datatype to and from a command(see below)
Notes:

- ZooCommands are not meant to do atomic operations and query ops. Only for maya state changes and only for large operations.
- ZooCommands are not meant to replace c++ commands or for efficient code but for tool development, it's not meant to be
run in loops or something stupid like that. eg. you press a pushbutton then you execute a command that builds a rig which
can be undone.


#### Example
```python

# End result is
from zoo.libs.command import executor
exe = executorExecutor()
nodes = exe.execute("zoo.create.nodetype", name="transform", amount=10, Type="transform")
print nodes
(<OpenMaya.MObjectHandle object at 0x0000024911572E70>, <OpenMaya.MObjectHandle object at 0x0000024911572E30>,
 <OpenMaya.MObjectHandle object at 0x0000024911572CB0>, <OpenMaya.MObjectHandle object at 0x0000024911572E90>,
 <OpenMaya.MObjectHandle object at 0x0000024911572EB0>, <OpenMaya.MObjectHandle object at 0x0000024911572ED0>,
 <OpenMaya.MObjectHandle object at 0x0000024911572EF0>, <OpenMaya.MObjectHandle object at 0x0000024911572F10>,
 <OpenMaya.MObjectHandle object at 0x0000024911572F30>, <OpenMaya.MObjectHandle object at 0x0000024911572F50>)


# see below for the command class

from zoo.libs.command import command


class CreateNodeTypeAmount(command.ZooCommand):
    id = "zoo.create.nodetype" # id which is used for execution, and any filtering, lookups, GUIs etc
    creator = "David Sparrow"
    isUndoable = True
    _modifier = None

    def resolveArguments(self, arguments):
        """Method to Pre check arguments this is run outside of mayas internals and the result cached on to the command instance.
        Since the result is store for the life time of the command you need to convert MObjects to MObjectHandles.
        :param arguments: dict representing the arguments
        :type arguments: dict
        """
        name=  arguments.get("name")
        if not name:
            self.cancel("Please provide a name!")
        amount = arguments.get("amount")
        if amount < 1:
            self.cancel("The amount can't be below one")
        if not arguments.get("Type"):
            arguments["Type"] = "transform"
        return arguments

    def doIt(self, name=None, amount=1, Type=None):
        """Its expected that the arguments are setup correctly with the correct datatype,
        """
        mod = om2.MDagModifier()
        nodes = [None] * amount
        for i in xrange(amount):
            obj = mod.createNode(Type)
            mod.renameNode(obj, "name{}".format(i))
            nodes[i] = obj
        mod.doIt()
        nodes = map(om2.MObjectHandle, nodes)
        self._modifier = mod
        return tuple(nodes)

    def undoIt(self):
        if self._modifier is not None:
            self._modifier.undoIt()
```


TODO
----
Most todo will be within the code base however any globals will be here.

- [ ] Update the unittests runner since we ported from zoocore repo.
- [ ] Get Sphinx documentation up and running for maya.
- [ ] Document how to install and run zoocore_maya which currently use a private repo.
- [ ] Update unitests, since we're lacking a fair amount.
- [ ] More Docstrings :D.
- [ ] Code Examples other than function level examples.


