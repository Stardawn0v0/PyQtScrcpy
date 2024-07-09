import datetime
import os
import sys
import re
import subprocess
import threading
import traceback

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QPropertyAnimation, QSize, QEasingCurve, Qt, QTranslator, QLocale
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from qfluentwidgets import MessageBox
from qframelesswindow import AcrylicWindow, StandardTitleBar

import util
from consts import *
from info_bar import info_bar
from mainWindow import Ui_Form
from cmosui import tip

os.environ['PATH'] += os.pathsep + os.pathsep.join([os.path.join(BASEDIR, name) for name in os.listdir(BASEDIR)])


class titleBar(StandardTitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.maxBtn.hide()
        self.titleLabel.setStyleSheet("""
                    QLabel{
                        background: transparent;
                        font: 13px 'Microsoft YaHei';
                        padding: 0 4px;
                        text-antialiasing: true;
                    }
                """)


class MainWindow(AcrylicWindow, Ui_Form):
    infoBar = pyqtSignal(str, str, str, int)
    error_signal = pyqtSignal(str)
    refresh_signal = pyqtSignal()
    slide_pro_page = pyqtSignal(QWidget)

    def __init__(self):
        super().__init__()
        self.pro_mode = False
        self.setTitleBar(titleBar(self))
        self.camera_info = None
        self.video_source = 'screen'
        self.setupUi(self)
        self.resize(self.minimumWidth(), self.height())
        self.previous_size = self.size()

        self.windowEffect.setMicaEffect(self.winId())
        self.setWindowTitle(f'{TOOL_NAME} {TOOL_VERSION}')
        self.setWindowIcon(QtGui.QIcon(":/icon/res/logo.png"))
        self.titleBar.raise_()

        sys.excepthook = self.custom_except_hook
        threading.excepthook = lambda args: self.custom_except_hook(args.exc_type, args.exc_value, args.exc_traceback)

        self.infoBar.connect(
            lambda title, content, style, timeout: info_bar(self, title, content if self.pro_mode else '', style,
                                                            timeout, position='↑' if self.pro_mode else '↓'))
        self.orientation.addItems(['0°', '90°', '180°', '270°'])
        self.video_source_switcher.addItem(
            routeKey='screen',
            text='设备屏幕',
            onClick=lambda: self.video_source_stacked.slideInWgt(self.screen_page),
        )
        self.video_source_switcher.addItem(
            routeKey='camera',
            text='摄像头',
            onClick=lambda: self.video_source_stacked.slideInWgt(self.camera_page),
        )
        self.video_source_switcher.setCurrentItem('screen')
        self.video_source_stacked.setCurrentIndex(0)
        self.video_bit_slider.valueChanged.connect(self.update_video_bitrate)
        self.audio_bit_slider.valueChanged.connect(self.update_audio_bitrate)

        self.get_devices_btn.clicked.connect(self.get_devices)
        self.restart_adb_btn.clicked.connect(self.restart_adb)
        self.camera_ids.currentIndexChanged.connect(self.on_camera_id_change)
        self.camera_sizes.currentIndexChanged.connect(self.on_camera_size_change)
        self.choice_record_output_path.clicked.connect(
            lambda: self.record_output_path.setText(QFileDialog.getExistingDirectory(self, '选择保存路径')))
        self.run_scrcpy.clicked.connect(self.run)
        self.install_pyqtscrcpy.clicked.connect(
            lambda: tip(self, self.install_pyqtscrcpy, '这个功能还没做完', '', 'Warning', True, 5000))
        self.abort_pyqtscrcpy.clicked.connect(
            lambda: tip(self, self.abort_pyqtscrcpy, '这个功能还没做完', '', 'Warning', True, 5000))
        self.devices_manager.clicked.connect(lambda: os.startfile('devmgmt.msc'))

        self.video_source_switcher.currentItemChanged.connect(self.on_video_source_change)
        self.adb_devices.itemSelectionChanged.connect(self.on_device_selection_changed)
        self.video_source_stacked.currentChanged.connect(self.audio_source_mic.setChecked)
        self.video_source_stacked.currentChanged.connect(lambda x: self.audio_source_output.setChecked(not x))

        self.animation = QPropertyAnimation(self, b"size")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.pro_page.clicked.connect(self.toggle_window_size)

        self.error_signal.connect(self.on_error)
        self.refresh_signal.connect(self.refresh_pro_page)
        self.slide_pro_page.connect(lambda w: self.pro_page_stacked.slideInWgt(w))

    def run(self):
        args = []
        if self.stay_awake.isChecked():
            args.append('--stay-awake')
        if self.turn_screen_off.isChecked():
            args.append('--turn-screen-off')
        if self.power_off_on_close.isChecked():
            args.append('--power-off-on-close')
        if self.no_control.isChecked():
            args.append('--no-control')
        if self.enable_record.isChecked():
            if not os.path.isdir(self.record_output_path.text()):
                tip(self, self.record_output_path, '请选择保存路径', '', 'Error', True, 5000)
                return
            args.append(f'--record="{self.record_output_path.text()}"')
            if self.record_time_limit.isChecked():
                if seconds := util.time_to_seconds(self.record_limit_edit.text()):
                    args.append(f'--time-limit={seconds}')
                else:
                    tip(self, self.record_limit_edit, '请输入正确的时间格式', '', 'Error', True, 5000)
                    return

            if self.no_playback.isChecked():
                args.append('--no-playback')

        if self.pro_page.isChecked():
            if self.enable_video.isChecked():
                if self.enable_orientation.isChecked():
                    args.append(f'--orientation={self.orientation.currentText().replace('°', '')}')
                args.append(f'--display-buffer={self.video_buffer.text()}')
                if self.enable_max_fps.isChecked():
                    args.append(f'--max-fps={self.max_fps.text()}')
                if self.video_source == 'screen':
                    if self.enable_target_screen.isChecked():
                        args.append(f'--display-id={self.target_screen.currentText()}')
                    if self.enable_max_size.isChecked():
                        args.append(f'--max-size={self.max_size.text()}')
                elif self.video_source == 'camera':
                    args.append('--video-source=camera')
                    args.append(f'--camera-id={self.camera_ids.currentText()}')
                    args.append(f'--camera-size={self.camera_sizes.currentText().replace('[高速]', '')}')
                    args.append(f'--camera-fps={self.camera_fps.currentText()}')
                if self.video_h264.isChecked():
                    args.append('--video-codec=h264')
                elif self.video_h265.isChecked():
                    args.append('--video-codec=h265')
                elif self.video_av1.isChecked():
                    args.append('--video-codec=av1')
                args.append(f'--video-bit-rate={util.convert_bitrate(self.video_bit.text())}')
            else:
                args.append('--no-video')

            if self.enable_audio.isChecked():
                if self.audio_source_output.isChecked():
                    args.append('--audio-source=output')
                elif self.audio_source_mic.isChecked():
                    args.append('--audio-source=mic')
                args.append(f'--audio-buffer={self.audio_buffer.text()}')
                if self.audio_opus.isChecked():
                    args.append('--audio-codec=opus')
                elif self.audio_aac.isChecked():
                    args.append('--audio-codec=aac')
                elif self.audio_flac.isChecked():
                    args.append('--audio-codec=flac')
                args.append(f'--audio-bit-rate={util.convert_bitrate(self.audio_bit.text())}')
            else:
                args.append('--no-audio')

        if self.enable_cust_port.isChecked():
            args.append(f'--tunnel-port={self.cust_port.text()}')

        if self.tcpip_connect.isChecked():
            args.append('--tcpip')

        args, invalid_args = util.check_args(args)

        cmd = f'start cmd /c "{SCRCPY} {" ".join(args)} || echo. & echo.\033[31m\033[1m---Scrcpy进程已结束 按任意键关闭窗口---\033[0m & pause>nul"'
        subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=BASEDIR)

    def refresh_pro_page(self):
        self.slide_pro_page.emit(self.refresh_page)

        def _():
            self.load_camera_ids()
            self.load_screen_ids()
            self.slide_pro_page.emit(self.main_pro_page)

        threading.Thread(target=_, daemon=True).start()

    def custom_except_hook(self, exc_type, exc_value, exc_traceback):
        if isinstance(exc_value, UnicodeDecodeError) or 'UnicodeDecodeError' in str(exc_value):
            # 如果异常是UnicodeDecodeError，发送特定的错误消息
            cwd_path = os.getcwd()
            if re.search(r'[\u4e00-\u9fff]', cwd_path):
                output = f"当前工作目录为：\n{cwd_path}\n请将工具文件移动至无中文字符的路径下并重启工具。"
            else:
                output = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            error_message = f"检测到编码错误：\n{output}"
            self.error_signal.emit(error_message)
        elif isinstance(exc_value, RuntimeError) or 'RuntimeError' in str(exc_value):
            return
        else:
            # 其他类型的错误处理
            formatted_traceback = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.error_signal.emit(formatted_traceback)

    def on_error(self, output):
        output = f'{TOOL_VERSION}\n{output}\n'
        with open('error.log', 'w') as f:
            output = f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]\n{output}'
            f.write(output)
        w = MessageBox('程序发生错误', output, self)
        w.cancelButton.hide()
        QApplication.clipboard().setText(output)
        w.yesButton.setText('确认')
        w.yesButton.clicked.connect(lambda: QApplication.clipboard().setText(output))
        w.exec()

    def on_device_selection_changed(self):
        self.refresh_signal.emit()
        selected_items = self.adb_devices.selectedItems()
        if selected_items:
            selected_device = selected_items[0].text()
            device_serial = selected_device.split(" | ")[-1]
            os.environ["ANDROID_SERIAL"] = device_serial
        else:
            os.environ.pop("ANDROID_SERIAL", None)

    def restart_adb(self):
        self.devices_card.setDisabled(True)

        def _():
            subprocess.run(f'{ADB} kill-server', shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            subprocess.run(f'{ADB} start-server', shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.devices_card.setDisabled(False)

            self.get_devices()

        threading.Thread(target=_, daemon=True).start()

    def get_devices(self):
        self.devices_card.setDisabled(True)

        def _():
            devices, unauthorized_devices, offline_devices = util.devices()
            self.adb_devices.clear()
            if devices:
                self.adb_devices.addItems([f"{name} | {serial}" for serial, name in devices.items()])
            elif unauthorized_devices:
                self.infoBar.emit(f'发现了{len(unauthorized_devices)}个未授权设备', '、'.join(unauthorized_devices), 'w',
                                  5000)
            elif offline_devices:
                self.infoBar.emit(f'发现了{len(offline_devices)}个离线设备', '、'.join(offline_devices), 'w', 5000)
            else:
                self.infoBar.emit('未发现设备', '请检查设备是否正常连接', 'e', 5000)
            self.devices_card.setDisabled(False)

        threading.Thread(target=_, daemon=True).start()

    def on_video_source_change(self, item):
        self.video_source = item
        if item == 'screen':
            self.enable_max_fps.setDisabled(False)
        elif item == 'camera':
            self.enable_max_fps.setDisabled(True)
            self.enable_max_fps.setChecked(False)

    def load_screen_ids(self):
        self.target_screen.clear()
        display_ids = util.get_display_ids()
        self.target_screen.addItems([str(id) for id in display_ids])

    def load_camera_ids(self):
        self.camera_ids.clear()
        self.camera_info = util.get_camera_sizes()
        camera_ids = list(self.camera_info.keys())
        self.camera_ids.addItems([str(id) for id in camera_ids])

    def on_camera_id_change(self):
        camera_id = int(self.camera_ids.currentText())
        sizes = list(self.camera_info[camera_id].keys())
        self.camera_sizes.clear()
        self.camera_sizes.addItems(sizes)

    def on_camera_size_change(self):
        camera_id = int(self.camera_ids.currentText())
        size = self.camera_sizes.currentText()
        fps_list = self.camera_info[camera_id][size]
        self.camera_fps.clear()
        self.camera_fps.addItems(fps_list)

    def update_audio_bitrate(self, value):
        if value < 10:
            bitrate = '32K'
        elif 10 <= value < 20:
            bitrate = '64K'
        elif 20 <= value < 40:
            bitrate = '128K'
        elif 40 <= value < 60:
            bitrate = '256K'
        elif 60 <= value < 80:
            bitrate = '512K'
        elif 80 <= value < 95:
            bitrate = '1M'
        elif 95 <= value < 100:
            bitrate = '2M'
        else:
            bitrate = '128K'

        self.audio_bit.setText(bitrate)

    def update_video_bitrate(self, value):
        if value == 0:
            value = 1
        if value >= 99:
            value = 100
        bitrate = value * 50

        if bitrate < 1000:
            unit = "K"
        else:
            bitrate /= 1000
            unit = "M"

        self.video_bit.setText(f"{bitrate:.2f} {unit}" if unit == "M" else f"{int(bitrate)} {unit}")

    def toggle_window_size(self):
        self.pro_mode = self.pro_page.isChecked()
        self.animation.stop() if self.animation.state() == QPropertyAnimation.Running else None
        page_size = QSize(800, 532) if self.pro_page.isChecked() else QSize(300, 532)
        start_size = self.size()
        self.animation.setStartValue(start_size)
        self.animation.setEndValue(page_size)
        self.animation.setDuration(300)
        self.animation.start()
        if self.pro_page.isChecked():
            self.setWindowTitle(f'{TOOL_NAME} {TOOL_VERSION}  by {TOOL_AUTHOR}')
        else:
            self.setWindowTitle(f'{TOOL_NAME} {TOOL_VERSION}')

    def resizeEvent(self, event):
        current_size = event.size()
        previous_size = self.previous_size

        if current_size.width() > previous_size.width() and not self.animation.state() == QPropertyAnimation.Running:
            self.pro_page.setChecked(True)
        elif current_size.width() == previous_size.width() and not self.animation.state() == QPropertyAnimation.Running:
            self.pro_page.setChecked(False)

        super().resizeEvent(event)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load(QLocale.system(), ':/i18n/media/qfluentwidgets.zh_CN.qm')
    app.installTranslator(translator)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
