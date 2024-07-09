from qfluentwidgets import InfoBarIcon, TeachingTip, TeachingTipTailPosition


def tip(parent, target, title: str, content: str, icon='Info', closable=True, duration=5000):
    """
    :param parent: 窗口对象
    :param target: Tip指向的控件
    :param title: 标题
    :param content: 正文
    :param icon: 图标，可选值：Info, Warning, Error, Success
    :param closable: 是否可手动关闭
    :param duration: 时长
    :return:
    """
    if icon == 'Info':
        icon = InfoBarIcon.INFORMATION
    elif icon == 'Warning':
        icon = InfoBarIcon.WARNING
    elif icon == 'Error':
        icon = InfoBarIcon.ERROR
    elif icon == 'Success':
        icon = InfoBarIcon.SUCCESS
    TeachingTip.create(
        target=target,
        icon=icon,
        title=title,
        content=content,
        isClosable=closable,
        tailPosition=TeachingTipTailPosition.TOP,
        duration=duration,
        parent=parent
    )
