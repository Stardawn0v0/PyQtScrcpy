from PyQt5.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition


def info_bar(MainWindow, title, content, style='o', timeout=5000, closeable=True, position='↑'):
    if position == '→':
        position = InfoBarPosition.TOP_RIGHT
    elif position == '↓':
        position = InfoBarPosition.BOTTOM
    elif position == '↑':
        position = InfoBarPosition.TOP
    if style == 'o':
        InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=closeable,
            position=position,
            duration=timeout,
            parent=MainWindow
        )
    elif style == 'e':
        InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=closeable,
            position=position,
            duration=timeout,
            parent=MainWindow
        )
    elif style == 'w':
        InfoBar.warning(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=closeable,
            position=position,
            duration=timeout,
            parent=MainWindow
        )
    elif style == 'i':
        InfoBar.info(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=closeable,
            position=position,
            duration=timeout,
            parent=MainWindow
        )
