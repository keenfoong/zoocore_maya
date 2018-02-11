import maya.cmds as cmds

INFO = 0
WARNING = 1
ERROR = 2


def inViewMessage(header, message, type_=INFO, fadeStayTime=1000):
    """Smaller wrapper function for nicely formatting maya inview message, INFO,WARNING,ERROR message types supported.
    Each message type will have a set color.

    :param header: The main header title for the message , ideally one word
    :type header: str
    :param message: The message to display
    :type message: str
    :param type_: gui.INFO,gui.WARNING, gui.ERROR
    :type type_: int
    :param fadeStayTime: the fade time
    :type fadeStayTime: int
    """
    useInViewMsg = cmds.optionVar(q='inViewMessageEnable')
    if not useInViewMsg:
        return
    if type_ == "info":
        msg = " <span style=\"color:#82C99A;\">{}:</span> {}"
        position = 'topCenter'
    elif type_ == "Warning":
        msg = "<span style=\"color:#F4FA58;\">{}:</span> {}"
        position = 'midCenterTop'
    elif type_ == "Error":
        msg = "<span style=\"color:#F05A5A;\">{}:</span> {}"
        position = 'midCenter'
    else:
        return
    cmds.inViewMessage(assistMessage=msg.format(header, message), fadeStayTime=fadeStayTime, dragKill=True,
                       position=position, fade=True)


def refreshContext():
    try:
        cmds.refresh(suppend=True)
        yield
    finally:
        cmds.refresh(suppend=False)