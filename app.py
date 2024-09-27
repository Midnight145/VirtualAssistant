import os
import re

import pulsectl
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def get_sources():
    command = "pactl list sources"
    regex = re.compile("Source #([0-9]+)")
    sources = []
    for line in os.popen(command).readlines():
        match = regex.match(line)
        if match:
            sources.append(int(match.group(1)))
    return sources

class MicrophoneAction(QAction):
    def __init__(self, source_info, pulse: pulsectl.Pulse, callback: callable):
        super().__init__(source_info.description, checkable=True) # type: ignore
        self.source_id = source_info.index
        self.pulse = pulse
        self.triggered.connect(self.trigger) # type: ignore
        self.callback = callback

    def trigger(self):
        self.callback()
        print(self.text())


# noinspection PyArgumentList
class Application(QApplication):
    def __init__(self):
        super().__init__([])
        self.setQuitOnLastWindowClosed(False)
        self.pulse = pulsectl.Pulse('voice-assistant')

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("icon.png"))
        self.tray.setVisible(True)

        self.main_menu = QMenu()
        self.quit_action = QAction("Quit", self.main_menu)
        self.quit_action.triggered.connect(self.exit)

        self.device_menu = QMenu("Devices")
        self.device_group = QActionGroup(self.device_menu)
        self.device_group.setExclusive(True)

        self.show_monitors_action = QAction("Show Monitors", checkable=True)
        self.show_monitors_action.triggered.connect(self.toggle_monitors)
        self.devices = []
        self.init_devices()

        self.main_menu.addMenu(self.device_menu)

        self.main_menu.addAction(self.show_monitors_action)
        self.main_menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.main_menu)
    def exit(self, code: int = 0):
        self.quit()
        self.pulse.close()

    def toggle_monitors(self):
        print("Toggling monitors")
        for i in self.device_group.actions():
            if "monitor" in i.text().lower():
                print("Toggling visibility of", i.text())
                i.setVisible(self.show_monitors_action.isChecked())

    def init_devices(self):
        sources = get_sources()
        for i in sources:
            source_info = self.pulse.source_info(i)
            action = MicrophoneAction(source_info, self.pulse, lambda:   None)
            if not self.show_monitors_action.isChecked():
                if "monitor" in source_info.description.lower():
                    action.setVisible(False)
            self.devices.append(action)
            self.device_group.addAction(action)
            self.device_menu.addAction(action)

Application().exec_()