#! /usr/bin/env python

import re
import subprocess
import time
from PyQt5 import QtGui, QtCore, QtWidgets
from functools import partial


class RightClickMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, command=None, tray=None, main_window=None):
        QtWidgets.QMenu.__init__(self, "File", parent)
        icon = QtGui.QIcon.fromTheme("Quit")
        self.tray = tray
        self.command = command
        self.main_window = main_window
        if "cpu" in command:
            label = "&CPU stats"
        elif "battery" in command:
            label = "&Battery stats"
        
        exitAction2 = QtWidgets.QAction(icon, label, self)
        exitAction2.triggered.connect(self.display_msg)
        self.addAction(exitAction2)
        
        exitAction = QtWidgets.QAction(icon, "&Exit", self)
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        self.addAction(exitAction)
        
    def display_msg(self):
        scode = subprocess.check_output(self.command)
        out = str(scode, "utf-8")
        self.main_window.show_message(out, self.command)
        
        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setMinimumSize(QtCore.QSize(300, 200))    
        self.hide()

    def cleanup_msg(self, out, cmd):
        if "cpu" in cmd:
            y = out.split(' ')
            del y[-1]
            out = ' '.join(y)
        else:
            m = out.split('\n')
            y = []
            for i in m:
                l = i.split()
                if len(l) > 3:
                    del l[-2]
                y.append(' '.join(l))
            out = '\n'.join(y)
        return out
        
    def show_message(self, out, cmd):
        out = self.cleanup_msg(out, cmd)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(out)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.show()
        ret = msg.exec_()
        self.show()
        #time.sleep(0.5)
        self.hide()


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    
    def __init__(self, parent=None, command=None, main_window=None):
        QtWidgets.QSystemTrayIcon.__init__(self, parent)
        self.right_menu = RightClickMenu(tray=self, command=command, main_window=main_window)
        self.setContextMenu(self.right_menu)
        self.activated.connect(self.onTrayIconActivated)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.info_play)
        self.timer.start(2000)
        self.cpu = "NA"
        self.bat = "NA"
        self.command = command
    
    def onTrayIconActivated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            scode = subprocess.check_output(self.command)
            out = str(scode, "utf-8")
            if "cpu" in self.command:
                msg = out.split('\n')[0].split()
                del msg[-1]
            else:
                msg = out.split('\n')[0].split()
            self.showMessage("Info:", " ".join(msg))

    def data_ready(self, p):
        out = str(p.readAllStandardOutput()).strip()
        if out:
            cpu = re.search('CPU temp:[ ]*(?P<tmp>[^.]*)', out)
            bat = re.search('Battery temp:[ ]*(?P<tmp>[^.]*)', out)
            if cpu or bat:
                if cpu:
                    self.cpu = cpu.group("tmp")
                if bat:
                    self.bat = bat.group("tmp")
                self.start_painting()

    def start_painting(self):
        self.p = QtGui.QPixmap(296, 128)
        self.p.fill(QtGui.QColor("transparent"))
        painter	= QtGui.QPainter(self.p)
        color = self.decide_color()
        painter.setPen(QtGui.QColor(color))
        painter.setFont(QtGui.QFont('Sans', 120, QtGui.QFont.Bold))
        txt = self.decide_text()
        painter.drawText(QtCore.QRectF(0, 0, 296, 128), QtCore.Qt.AlignCenter, txt)
        self.setIcon(QtGui.QIcon(self.p))
        del painter

    def decide_color(self):
        color = "black"
        if "cpu" in self.command and self.cpu and self.cpu.isnumeric():
                tmp = int(self.cpu)
                if tmp < 51:
                    color = "green"
                elif tmp in range(51, 65):
                    color = "purple"
                else:
                    color = "red"
        elif "battery" in self.command and self.bat and self.bat.isnumeric():
                tmp = int(self.bat)
                if tmp < 38:
                    color = "green"
                elif tmp in range(38, 45):
                    color = "purple"
                else:
                    color = "red"
        return color

    def decide_text(self):
        if "cpu" in self.command:
            txt = "{}{}".format(self.cpu, u"\u00B0")
        elif "battery" in self.command:
            txt = "{}{}".format(self.bat, u"\u00B0")
        return txt
    
    def started(self):
        pass
        
    def finished(self):
        pass
        
    def info_play(self):
        proc = QtCore.QProcess()
        proc.started.connect(self.started)
        proc.readyReadStandardOutput.connect(partial(self.data_ready, proc))
        proc.finished.connect(self.finished)
        QtCore.QTimer.singleShot(100, partial(proc.start, " ".join(self.command)))

def main():
    app = QtWidgets.QApplication([])
    mainw = MainWindow()
    tray1 = SystemTrayIcon(command=["istats", "cpu"], main_window=mainw)
    tray1.show()
    tray2 = SystemTrayIcon(command=["istats", "battery"], main_window=mainw)
    tray2.show()
    app.exec_()
    
if __name__ == "__main__":
   main()
    
