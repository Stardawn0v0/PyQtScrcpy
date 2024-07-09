import os
import sys

TOOL_VERSION = r'Release-v1'
TOOL_VERSION_CODE = 1
TOOL_NAME = r'PyQtScrcpy'
TOOL_AUTHOR = r'bilibili@星间晞'
DATA_PATH = os.path.join(os.path.expanduser('~'), '.pyqtscrcpy')


try:
    if os.path.isdir(os.path.join(os.path.dirname(__file__), 'bin')):
        BASEDIR = os.path.join(os.path.dirname(__file__), 'bin')
    elif os.path.isdir(os.path.join(os.path.dirname(sys.executable), 'bin')):
        BASEDIR = os.path.join(os.path.dirname(sys.executable), 'bin')
    else:
        BASEDIR = os.path.join(os.path.dirname(__file__), 'bin')
        print('bin not found, using current directory')
except Exception:
    pass
