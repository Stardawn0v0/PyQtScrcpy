import os
import platform
import subprocess
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
    if 'Windows' in platform.system():
        ADB = os.path.join(BASEDIR, 'adb.exe')
        SCRCPY = os.path.join(BASEDIR, 'scrcpy.exe')
    else:
        ADB = 'adb'
        SCRCPY = 'scrcpy'
except Exception:
    pass

if 'Windows' in platform.system():
    CREATE_NEW_CONSOLE = subprocess.CREATE_NEW_CONSOLE
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
else:
    CREATE_NEW_CONSOLE = 0
    CREATE_NO_WINDOW = 0
