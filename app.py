from utils import *
from constants import *

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *



class Window(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = Status.STOPPED
        self.initUI()
        self.initTimer()
        self.initTrayIcon()
        self.initButtons()
        self.initShortcuts()
        self.setMode(Mode.POMODORO)
        self.cycles = 0


    def initUI(self):
        self.setWindowTitle("PomoFocus")
        self.resize(1000, 500)
        self.setStyleSheet("font-family: 'ArialRounded'")
        self.timeLabel = QLabel()
        self.timeLabel.setStyleSheet("font-family: 'ArialRounded'; font-size: 180px")


    def initShortcuts(self) -> None:
        self.shortcutQuit = QShortcut(QKeySequence.Quit, self)
        self.shortcutQuit.activated.connect(self.close)
    

    def initButtons(self) -> None:
        verticalBox = QVBoxLayout()
        modeBox = QHBoxLayout()
        timerLayout = QGridLayout()

        self.pomodoroBtn = QPushButton("Pomodoro")
        self.shortBreakBtn = QPushButton("Short break")
        self.longBreakBtn = QPushButton("Long break")

        self.pomodoroBtn.clicked.connect(lambda: self.setMode(Mode.POMODORO))
        self.pomodoroBtn.setToolTip("Start working")
        self.shortBreakBtn.clicked.connect(lambda: self.setMode(Mode.SHORT_BREAK))
        self.shortBreakBtn.setToolTip("Take a short break")
        self.longBreakBtn.clicked.connect(lambda: self.setMode(Mode.LONG_BREAK))
        self.longBreakBtn.setToolTip("Take a long break")

        modeBox.addWidget(self.pomodoroBtn)
        modeBox.addWidget(self.shortBreakBtn)
        modeBox.addWidget(self.longBreakBtn)

        self.resetBtn = QPushButton()
        self.timerBtn = QPushButton()
        self.skipBtn = QPushButton()
        self.setStartTimer()

        self.resetBtn.clicked.connect(self.reset)
        self.resetBtn.setText("Reset")
        self.resetBtn.setToolTip("Reset the timer")
        self.timerBtn.clicked.connect(self.onTimerButtonClick)
        self.skipBtn.clicked.connect(self.skip)
        self.skipBtn.setText("Skip")
        self.skipBtn.setToolTip("Skip to the next mode")

        self.resetBtn.setStyleSheet("color: #d95550; background-color: #ffffff;")
        self.timerBtn.setStyleSheet("color: #d95550; background-color: #ffffff;")
        self.skipBtn.setStyleSheet("color: #d95550; background-color: #ffffff;")

        timerLayout.addWidget(self.resetBtn, 0, 0)
        timerLayout.addWidget(self.timerBtn, 0, 1)
        timerLayout.addWidget(self.skipBtn, 0, 2)

        verticalBox.addLayout(modeBox)
        verticalBox.addWidget(self.timeLabel, alignment=Qt.AlignCenter)
        verticalBox.addLayout(timerLayout)

        centralWidget = QWidget(self)
        centralWidget.setLayout(verticalBox)
        self.setCentralWidget(centralWidget)


    def initTrayIcon(self) -> None:
        self.pomodoroIcon = QIcon("resources/pomodoro.png")
        self.trayIcon = QSystemTrayIcon()
        self.trayIcon.setIcon(self.pomodoroIcon)
        self.trayIcon.show()

        trayIconContextMenu = QMenu()
        self.timeAction = trayIconContextMenu.addAction("Start")
        self.resetAction = trayIconContextMenu.addAction("Reset")
        self.skipAction = trayIconContextMenu.addAction("Skip")

        self.timeAction.triggered.connect(self.start)
        self.resetAction.triggered.connect(self.reset)
        self.skipAction.triggered.connect(self.skip)

        trayIconContextMenu.addAction(self.timeAction)
        self.trayIcon.setContextMenu(trayIconContextMenu)


    def initTimer(self) -> None:
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)    


    def setMode(self, mode: Mode) -> None:
        if self.status == Status.RUNNING:
            messageBox = QMessageBox.question(self, "Switch mode", "Are you sure? The timer will be reset", QMessageBox.Yes | QMessageBox.Cancel)
            if messageBox == QMessageBox.Yes:
                self.mode = mode
                self.reset()
        else:
            self.mode = mode
            self.reset()


    def displayTime(self) -> None:
        self.timeLabel.setText(format_time(self.time_left))


    def reset(self) -> None:
        if self.mode == Mode.POMODORO:
            self.time_left = POMODORO
            self.pomodoroBtn.setEnabled(False)
            self.shortBreakBtn.setEnabled(True)
            self.longBreakBtn.setEnabled(True)
        elif self.mode == Mode.SHORT_BREAK:
            self.time_left = SHORT_BREAK
            self.pomodoroBtn.setEnabled(True)
            self.shortBreakBtn.setEnabled(False)
            self.longBreakBtn.setEnabled(True)
        elif self.mode == Mode.LONG_BREAK:
            self.time_left = LONG_BREAK
            self.pomodoroBtn.setEnabled(True)
            self.shortBreakBtn.setEnabled(True)
            self.longBreakBtn.setEnabled(False)
        self.displayTime()
        self.pause()


    def skip(self) -> None:
        self.reset()
        if self.mode == Mode.POMODORO:
            self.setMode(Mode.SHORT_BREAK)
        else:
            self.setMode(Mode.POMODORO)


    def onTimerButtonClick(self) -> None:
        if self.status == Status.STOPPED:
            self.start()
        else:
            self.pause()


    def start(self) -> None:
        self.timer.start(1000)
        self.setPauseTimer()


    def setStartTimer(self) -> None:
        self.status = Status.STOPPED
        self.timerBtn.setText("Start")
        self.timerBtn.setToolTip("Start the timer")
        self.timeAction.setText("Start")
        self.timeAction.triggered.connect(self.start)


    def pause(self) -> None:
        self.timer.stop()
        self.setStartTimer()


    def setPauseTimer(self) -> None:
        self.status = Status.RUNNING
        self.timerBtn.setText("Pause")
        self.timerBtn.setToolTip("Pause the timer")
        self.timeAction.setText("Pause")
        self.timeAction.triggered.connect(self.pause)


    def updateTime(self) -> None:
        self.time_left -= 1
        self.displayTime()
        if self.time_left == 0:
            self.notify()


    def notify(self) -> None:
        self.pause()
        if self.mode == Mode.POMODORO:
            self.cycles += 1
            if self.cycles % 4 != 0:
                self.trayIcon.showMessage("Congratulations!", "You have completed your 25 minutes of work! You can now relax by taking a short break :)", self.pomodoroIcon)
                self.setMode(Mode.SHORT_BREAK)
                self.trayIcon.MessageIcon()
            else:
                self.trayIcon.showMessage("Congratulations!", "You have completed 4 cycles! Now it's time for a long break!", self.pomodoroIcon)
                self.setMode(Mode.LONG_BREAK)
                self.cycles = 0
        else:
            self.trayIcon.showMessage("The break is ended!", "It's time to coming back to focus!", self.pomodoroIcon)
            self.setMode(Mode.POMODORO)
        self.start()


    def closeEvent(self, event) -> None:
        close = QMessageBox.question(self, "Quit", "Are you sure?", QMessageBox.Yes | QMessageBox.Cancel)
        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
