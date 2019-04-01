#This is a rubik's cube tracker.

import sys
import random
import time
import math
from pynput import keyboard

from PyQt5.QtCore import QDate, QTimer, QSize, Qt
from PyQt5.QtWidgets import (QMainWindow, QLabel, QGridLayout, QWidget,
                             qApp, QApplication, QTabWidget, QVBoxLayout,
                             QPlainTextEdit, QSizePolicy, QPushButton)



class Rubix(QMainWindow):

    def __init__(self):
        super().__init__()

        self.times = []
        self.old_face = random.randint(1, 6)
        self.old_old_face = random.randint(1, 6)
        while self.old_old_face == self.old_face:
            self.old_old_face = random.randint(1, 6)
        self.rectime = 0
        self.timeState = 0
        self.timeCanceled = False
        self.dnf = False
        self.avg5 = float(1000000)
        self.avg12 = float(1000000)
        self.released = False
        self.alreadyRecorded = False

        self.initUI()

        self.timerRunning = False

    def initUI(self):
        self.scrambleText = QPlainTextEdit()
        self.scrambleText.setReadOnly(True)
        self.scrambleText.setPlainText('hello world')
        font = self.scrambleText.font()
        font.setPixelSize(20)
        self.scrambleText.setFont(font)
        self.scrambleText.setMaximumSize(QSize(1000, 40))
        self.showScramble()

        self.cancelTimeButton = QPushButton()
        self.cancelTimeButton.setText('&Cancel Time')
        self.cancelTimeButton.clicked.connect(self.badTime)
        self.cancelTimeButton.setEnabled(False)

        self.dnfButton = QPushButton()
        self.dnfButton.setText('&DNF')
        self.dnfButton.clicked.connect(self.dnfEvent)
        self.dnfButton.setEnabled(False)

        self.timerDisplay = QLabel('00:00.000')
        self.timerDisplay.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        font = self.timerDisplay.font()
        font.setPixelSize(100)
        self.timerDisplay.setFont(font)
        
        timer = QWidget()
        timer_layout = QVBoxLayout()
        label = QLabel('Scramble:')
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        timer_layout.addWidget(label)
        timer_layout.addWidget(self.scrambleText)
        timer_layout.addWidget(self.timerDisplay)
        timer_layout.addWidget(self.cancelTimeButton)
        timer_layout.addWidget(self.dnfButton)
        timer.setLayout(timer_layout)

        self.statsText = QPlainTextEdit()
        self.statsText.setReadOnly(True)
        font = self.statsText.font()
        font.setPixelSize(20)
        self.statsText.setFont(font)
        self.statsText.setPlainText('Nobody will see this!')

        self.resetTimesButton = QPushButton()
        self.resetTimesButton.setText('&Reset Statistics')
        self.resetTimesButton.clicked.connect(self.badStats)
        self.resetTimesButton.setEnabled(False)

        stats = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(self.statsText)
        stats_layout.addWidget(self.resetTimesButton)
        stats.setLayout(stats_layout)

        plltext = QPlainTextEdit()
        plltext.setReadOnly(True)
        font = plltext.font()
        font.setPixelSize(20)
        plltext.setFont(font)
        plltext.setPlainText(self.pllStrings())

        pll = QWidget()
        pll_layout = QVBoxLayout()
        pll_layout.addWidget(plltext)
        pll.setLayout(pll_layout)

        #exitAct = QAction('Exit', self)
        #exitAct.setShortcut('Ctrl+Q')
        #exitAct.triggered.connect(qApp.quit)

        self.tabwidget = QTabWidget()
        self.tabwidget.addTab(timer, 'Timer')
        self.tabwidget.addTab(stats, 'Statistics')
        self.tabwidget.addTab(pll, 'PLL')
        self.tabwidget.currentChanged.connect(self.on_tab_changed)

        self.setCentralWidget(self.tabwidget)

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("Rubik's Cube Tracker")

        self.show()

    def on_tab_changed(self, index):
        if index == 0:
            self.showScramble()
            self.timeState = 0
        elif index == 1:
            self.cancelTimeButton.setEnabled(False)
            self.dnfButton.setEnabled(False)
            if(not self.rectime == 0 and not self.timeCanceled and not self.alreadyRecorded):
                if self.dnf:
                    self.times.append(1000000)
                else:
                    self.times.append(self.rectime)
                    # write time to file
                    file = open("previous_solves.txt", "a+")
                    file.write(QDate.currentDate().toString(Qt.ISODate) + ", ")
                    file.write(self.fixText(self.rectime) + '\n')
                    file.close()
                self.resetTimesButton.setEnabled(True)
            self.timerDisplay.setText('00:00.000')
            self.updateStats()
            self.rectime = 0
        elif index == 2:
            self.cancelTimeButton.setEnabled(False)
            self.dnfButton.setEnabled(False)
            if(not self.rectime == 0 and not self.timeCanceled and not self.alreadyRecorded):
                if self.dnf:
                    self.times.append(1000000)
                else:
                    self.times.append(self.rectime)
                    # write time to file
                    file = open("previous_solves.txt", "a+")
                    file.write(QDate.currentDate().toString(Qt.ISODate) + ", ")
                    file.write(self.fixText(self.rectime) + '\n')
                    file.close()
                self.resetTimesButton.setEnabled(True)
            self.timerDisplay.setText('00:00.000')
            self.rectime = 0
            
    def badTime(self):
        self.timeCanceled = True
        self.timerDisplay.setText('Canceled')
        self.cancelTimeButton.setEnabled(False)
        self.dnfButton.setEnabled(False)

    def dnfEvent(self):
        self.dnf = True
        self.timerDisplay.setText('DNF')
        file = open("previous_solves.txt", "a+")
        file.write(QDate.currentDate().toString(Qt.ISODate) + ", ")
        file.write('DNF\n')
        file.close()
        self.dnfButton.setEnabled(False)
        self.cancelTimeButton.setEnabled(False)

    def badStats(self):
        self.times.clear()
        self.resetTimesButton.setEnabled(False)
        self.updateStats()

    def keyPressEvent(self, event):
        if self.tabwidget.currentIndex() != 0:
            super().keyPressEvent(event)
            return
        if event.isAutoRepeat():
            return

        if not self.timerRunning and self.timeState == 0:
            # only start timer when key is released
            def on_release(key):
                self.released = True
                return False
            with keyboard.Listener(on_release = on_release) as listener:
                listener.join()
            while(self.released == False):
                on_key_release()
            self.released = False
            self.cancelTimeButton.setEnabled(False)
            self.dnfButton.setEnabled(False)
            self.alreadyRecorded = False
            # clear dnfs and canceled times
            if(not self.timeCanceled and not self.rectime == 0):
                self.resetTimesButton.setEnabled(True)
            self.timeCanceled = False
            self.dnf = False
            # start the timer
            self.timerRunning = True
            self.time_start = time.time()
            self.time_end = None
            self.timer = QTimer()
            self.timer.timeout.connect(self.updateTimerDisplay)
            # send a signal every 20 milliseconds:
            self.timer.start(20)
        elif self.timeState == 1:
            if (not self.timeCanceled):
                if self.dnf:
                    self.times.append(1000000)
                else:
                    self.times.append(self.rectime)
                    # write time to file
                    file = open("previous_solves.txt", "a+")
                    file.write(QDate.currentDate().toString(Qt.ISODate) + ", ")
                    file.write(self.fixText(self.rectime) + '\n')
                    file.close()
                    self.alreadyRecorded = True
            self.showScramble()
            self.timeState = 0
            self.timerDisplay.setText('{:02d}:{:02d}.{:03d}'.format(0, 0, 0))
            self.cancelTimeButton.setEnabled(False)
            self.dnfButton.setEnabled(False)
        else:
            # stop the timer
            self.timerRunning = False
            self.time_end = time.time()
            self.timer.stop()
            self.updateTimerDisplay()
            self.rectime = self.time_end - self.time_start
            self.cancelTimeButton.setEnabled(True)
            self.dnfButton.setEnabled(True)
            self.timeState = 1

    def updateTimerDisplay(self):
        if self.timerRunning:
            time_current = time.time()
            duration = time_current - self.time_start
        else:
            duration = self.time_end - self.time_start

        minutes = math.floor(duration / 60)
        seconds = math.floor(duration - 60 * minutes)
        millis = math.floor(1000 * (duration - 60 * minutes - seconds))
        self.timerDisplay.setText('{:02d}:{:02d}.{:03d}'.format(minutes, seconds, millis))

    def fixText(self, numTime):
        minutes = math.floor(numTime / 60)
        seconds = math.floor(numTime - 60 * minutes)
        millis = math.floor(1000 * (numTime - 60 * minutes - seconds))
        return '{:02d}:{:02d}.{:03d}'.format(minutes, seconds, millis)
        
    def pllStrings(self):
        result = ('Ua perm: [R U\' R] U R U R U\' R\' U\' R2\n'
                  'Ub perm: R2 U R U R\' U\' R\' U\' R\' U R\'\n'
                  'Z perm:  M2 U M2 U M\' U2 M2 U2 M\' U2\n'
                  'H perm:  M2 U M2 U2 M2 U M2\n\n'

                  'Aa perm: l\' U R\' D2 R U\' R\' D2 R2\n'
                  'Ab perm: l U\' R D2 R\' U R D2 R2\n'
                  'E perm:  x\' [R U\' R\' D] [R U R\' D\'] [R U R\' D] [R U\' R\' D\']\n\n'

                  'T perm:  [R U R\' U\'] R\' F R2 U\' R\' U\' [R U R\' F\']\n'
                  'F perm:  [R\' U R U\'] R2 y\' [R\' U\' R U] y x [R U R\' U\'] [R2 x U\']\n'
                  'Ja perm: L\' U\' L F L\' U\' L U L F\' L2 U L U\n'
                  'Jb perm: [R U R\' F\'] [R U R\' U\' R\' F] [R2 U\' R\' U\']\n'
                  'Ra perm: [R U R\' F\'] R U2 R\' U2 R\' F R U R U2 R\' U\'\n'
                  'Rb perm: L\' U\' L F L\' U2 L U2 L F\' L\' U\' L\' U2 L U\n'
                  'V perm:  [R\' U R\' d\'] R\' F\' R2 U\' R\' U R\' F R F\n'
                  'Y perm:  [F R U\' R\' U\' R U R\' F\'] [R U R\' U\'] [R\' F R F\']\n'
                  'Na perm: {L U\' R U2 L\' U R\'} {L U\' R U2 L\' U R\'} U\n'
                  'Nb perm: {R\' U L\' U2 R U\' L} {R\' U L\' U2 R U\' L} U\'\n\n'

                  'Ga perm: [R2 u] R\' U R\' U\' R u\' R2 y\' [R\' U R]\n'
                  'Gb perm: [L\' U\' L] y\' {R2 u R\' U R U\' R u\' R2}\n'
                  'Gc perm: [R2 u\'] R U\' R U R\' u R2 y [R U\' R\']\n'
                  'Gd perm: [R U R\'] y\' R2 u\' R U\' R\' U R\' u R2\n')
        return result

    def updateStats(self):
        if len(self.times) == 0:
            self.statsText.setPlainText('Not enough times recorded yet!')
        else:
            sortedList = sorted(self.times)
            numDNFs = 0

            strtimes = ''
            for i in range(len(sortedList)):
                if i == len(sortedList) - 1:
                    if sortedList[i] == 1000000:
                        strtimes += 'DNF'
                        numDNFs += 1
                    else:
                        strtimes += self.fixText(sortedList[i])
                else:
                    if sortedList[i] == 1000000:
                        strtimes += 'DNF, '
                        numDNFs += 1
                    else:
                        strtimes += self.fixText(sortedList[i]) + ', '
            strtimes = 'List: ' + strtimes + '\n'

            if numDNFs == 0:
                strtimes += 'Mean: ' + self.fixText(sum(sortedList)/len(sortedList)) + '\n'
            else:
                strtimes += 'Mean: DNF\n'

            if numDNFs >= 2:
                strtimes += 'Average: DNF\n'
            elif len(sortedList) < 3:
                strtimes += 'Not enough data to display average!\n'
            else:
                strtimes += 'Average: ' + self.fixText(sum(sortedList[1:len(sortedList)-1])/(len(sortedList)-2)) + '\n'

            if sum(self.times[-5:]) >= 2000000:
                strtimes += 'Average of 5: DNF\n'
            elif len(sortedList) < 5:
                strtimes += 'Not enough data to display average of 5!\n'
            else:
                strtimes += 'Average of 5: ' + self.fixText(sum(sorted(self.times[-5:])[1:4])/3) + '\n'
                if sum(sorted(self.times[-5:])[1:4])/3 < self.avg5:
                    self.avg5 = sum(sorted(self.times[-5:])[1:4])/3

            if self.avg5 == float(1000000):
                strtimes += 'Not enough data to display best average of 5!\n'
            else:
                strtimes += 'Best average of 5: ' + self.fixText(self.avg5) + '\n'

            if sum(self.times[-12:]) >= 2000000:
                strtimes += 'Average of 12: DNF\n'
            elif len(sortedList) < 12:
                strtimes += 'Not enough data to display average of 12!\n'
            else:
                strtimes += 'Average of 12: ' + self.fixText(sum(sorted(self.times[-12:])[1:11])/10) + '\n'
                if sum(sorted(self.times[-12:])[1:11])/10 < self.avg12:
                    self.avg12 = sum(sorted(self.times[-12:])[1:11])/10

            if self.avg12 == float(1000000):
                strtimes += 'Not enough data to display best average of 12!\n'
            else:
                strtimes += 'Best average of 12: ' + self.fixText(self.avg12) + '\n'

            if len(sortedList) - numDNFs <= 0:
                strtimes += 'Not enough data to display fastest time!\n'
            else:
                strtimes += 'Fastest: ' + self.fixText(sortedList[0]) + '\n'

            if numDNFs == 0:
                strtimes += 'Slowest: ' + self.fixText(sortedList[len(sortedList) - 1]) + '\n'
            else:
                strtimes += 'Slowest: DNF\n'

            if len(sortedList) - numDNFs <= 0:
                strtimes += 'Not enough data to display slowest non-DNF time!\n'
            else:
                strtimes += 'Slowest non-DNF: ' + self.fixText(sortedList[len(sortedList) - 1 - numDNFs]) + '\n'

            if len(sortedList) - numDNFs <= 0:
                strtimes += 'Not enough data to display standard deviation!\n'
            else:
                stand = float(0)
                noDNFsum = sum(sortedList) - 1000000*numDNFs
                for i in sortedList:
                    if i != 1000000:
                        stand += math.pow((i - noDNFsum/(len(sortedList)-numDNFs)), 2)
                stand /= float(len(sortedList)-numDNFs)
                stand = math.sqrt(stand)
                strtimes += 'Standard Deviation of non-DNFs: ' + self.fixText(stand) + '\n'

            self.statsText.setPlainText(strtimes)

    def showScramble(self):
        scramble = ''
        for i in range(0, 20):
            subscramble = ''
            
            face = random.randint(1, 6)
            while face == self.old_face or (face == self.old_old_face and self.IsOppositeFaces()):
                face = random.randint(1, 6)
            self.old_old_face = self.old_face
            self.old_face = face
            turn = random.randint(1, 3)
            if face == 1:
                subscramble = 'F'
            elif face == 2:
                subscramble = 'B'
            elif face == 3:
                subscramble = 'R'
            elif face == 4:
                subscramble = 'L'
            elif face == 5:
                subscramble = 'U'
            else:
                subscramble = 'D'

            if turn == 1:
                subscramble = subscramble + '\' '
            elif turn == 2:
                subscramble = subscramble + '2 '
            else:
                subscramble = subscramble + ' '

            scramble = scramble + subscramble

        self.scrambleText.setPlainText(scramble)

    def IsOppositeFaces(self):
        return ((self.old_face == 1 and self.old_old_face == 2) or
                (self.old_face == 2 and self.old_old_face == 1) or
                (self.old_face == 3 and self.old_old_face == 4) or
                (self.old_face == 4 and self.old_old_face == 3) or
                (self.old_face == 5 and self.old_old_face == 6) or
                (self.old_face == 6 and self.old_old_face == 5))

if (__name__) == '__main__':
    app = QApplication(sys.argv)
    rubix = Rubix()
    sys.exit(app.exec_())

    
