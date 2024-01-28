import os, sys
import time

import paramiko
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtXml import QDomDocument, QDomElement, QDomNode, QDomNodeList
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget
from PyQt5 import QtCore, uic
import threading

prevComm = None
socketId = 0
lanSockets = []
path = './commLogos'
images = []
ports = []

for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
        images.append(os.path.join(path, file))


class LANSocketLabel(QSvgWidget):
    clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.id = None
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton or ev.button() == Qt.RightButton:
            selectedSocket = self.getId()
            self.clicked.emit(selectedSocket)
            print(selectedSocket)

    def setId(self, socId):
        self.id = socId

    def getId(self):
        return self.id


class LANSocket():
    def __init__(self):
        super().__init__()
        self.id = None
        self.posX = None
        self.posY = None
        self.name = None
        self.commName = None
        self.wlan = None
        self.status = None
        self.imgPath = None
        self.pix = None
        self.ico = None
        self.speed = None
        self.type = None
        self.duplex = None

    def setId(self, id):
        self.id = id

    def setPos(self, posX, posY):
        self.posX = posX
        self.posY = posY

    def setName(self, name):
        self.name = name

    def setCommName(self, commName):
        self.commName = commName

    def setWlan(self, wlan):
        self.wlan = wlan

    def setStatus(self, status, imgPath):
        self.status = status

        svg = QFile(imgPath)
        self.ico = LANSocketLabel()
        svgDoc = QDomDocument()
        svgDoc.setContent(svg)
        svgDoc.childNodes().at(2).childNodes().at(2).childNodes().at(1).childNodes().at(0).firstChild().setNodeValue(self.getName())
        svg.close()
        self.ico.load(svgDoc.toByteArray())
        self.ico.setId(self.getId())
        self.ico.setFixedSize(50, 50)

        # self.pix = QPixmap(QPixmap(imgPath).scaled(50, 50, Qt.KeepAspectRatio))
        # self.ico = LANSocketLabel()
        # self.ico.setPixmap(self.pix)
        # self.ico.setId(self.getId())
        # self.ico.setOpenExternalLinks(True)
        self.imgPath = imgPath

    def setSpeed(self, speed):
        self.speed = speed

    def setType(self, type):
        self.type = type

    def setDuplex(self, duplex):
        self.duplex = duplex

    def getId(self):
        return self.id

    def getPosX(self):
        return self.posX

    def getPosY(self):
        return self.posY

    def getWlan(self):
        return self.wlan

    def getName(self):
        return self.name

    def getCommName(self):
        return self.commName

    def getStatus(self):
        return self.status

    def getImgPath(self):
        return self.imgPath

    def getIco(self):
        return self.ico

    def getSpeed(self):
        return self.speed

    def getType(self):
        return self.type

    def getDuplex(self):
        return self.duplex


class AnotherWindow(QWidget):
    def __init__(self):
        super().__init__()


class WarWindow(QWidget):
    def __init__(self, title, message):
        super().__init__()
        self.setWindowTitle(title)
        lay = QHBoxLayout()
        label = QLabel()
        label.setText(message)
        lay.addWidget(label)
        self.setLayout(lay)


class MainWindow(QMainWindow):
    xyi = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)

        w = QWidget()
        uic.loadUi('./mainForm_v2.ui', w)
        self.setCentralWidget(w)

        self.subW = QWidget()
        uic.loadUi('./form.ui', self.subW)
        self.subW.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.subW.show()

        for child in range(len(self.subW.findChildren(QPushButton))):
            self.subW.findChildren(QPushButton)[child].setIcon(QIcon(images[child]))
            self.subW.findChildren(QPushButton)[child].setIconSize(QtCore.QSize(200, 100))

        self.subW.pushButton.clicked.connect(self.onclick)

        self.ssh = None
        self.channel = None
    def clearContent(self):
        gbox = window.findChild(QGroupBox, 'groupBox')
        table = window.findChild(QTableWidget, 'lanSockets')
        table.setRowCount(0)
        for g in gbox.findChildren(QGroupBox):
            g.close()
        self.subW.show()

<<<<<<< HEAD
    def check(self):
        print('check')
        self.readData('')
=======

    def check(self):
        gbox = window.findChild(QGroupBox, 'groupBox')
        table = window.findChild(QTableWidget, 'lanSockets')
        table.setRowCount(0)
        for g in gbox.findChildren(QGroupBox):
            g.close()
        output = self.channel.recv(65535)
        self.channel.send('show interface status\n')
        for kaka in range(4):
            time.sleep(0.1)
            self.channel.send(' ')
        while True:
            if self.channel.recv_ready():
                output = self.channel.recv(65535).decode('utf-8')
            else:
                break
        self.readData(output)
>>>>>>> b0052d7d59cb7ebcfc60f4a6556f899dc15c8d0c

    def selectRow(self):
        self.findChild(QTableWidget, 'lanSockets').selectRow()

    def createConfig(self, data):
        with open('./src/example.txt', "w") as file:
            file.write(data)
            return file

    def readData(self, data_1):
        ports.clear()
        lanSockets.clear()
        socketId = 0
        file = self.createConfig(data_1)
        data = open('./src/example.txt', 'r').readlines()
        file.close()
        for line in data:
            if line.startswith('port'):
                if len(line.split()) > 5:
                    ports.append(line.split(maxsplit=5))

        prevComm = None

        comm = QGridLayout()
        comm.setObjectName('socketsPreview' + ports[0][0][4])
        comm.setHorizontalSpacing(0)
        comm.setVerticalSpacing(0)
        gb = QGroupBox()
        gb.setLayout(comm)
        gb.setTitle('Коммутатор ' + ports[0][0][4])
        self.findChild(QGroupBox, 'groupBox').layout().addWidget(gb)
        fillingComm = comm

        for port in ports:
            currComm = port[0][4]

            if prevComm is not None and prevComm != currComm:
                comm = QGridLayout()
                comm.setObjectName('socketsPreview' + currComm)
                comm.setHorizontalSpacing(0)
                comm.setVerticalSpacing(0)
                gb = QGroupBox()
                gb.setLayout(comm)
                gb.setTitle('Коммутатор ' + currComm)
                self.findChild(QGroupBox, 'groupBox').layout().addWidget(gb)
                fillingComm = comm

            j = ports.index(port)
            parameters = []
            soc = LANSocket()
            soc.setId(socketId)
            soc.setWlan(port[2])
            soc.setName(port[0].split('.')[2])
            if (int(soc.getName())) % 2 == 0:
                soc.setPos(1, int(soc.getName()) - fillingComm.columnCount() + 1)
            else:
                soc.setPos(0, int(soc.getName()) - fillingComm.columnCount() + 1)
            soc.setCommName(port[0][4])
            if port[1] == 'notconnect':
                soc.setStatus(port[1], './src/socket_free.svg')
            elif port[1] == 'connected' and port[2] == 'trunk':
                soc.setStatus(port[1], './src/socket_trunk.svg')
            elif port[1] == 'connected' and port[2] != 'trunk':
                soc.setStatus(port[1], './src/socket_used.svg')
            elif port[1] == 'disabled':
                soc.setStatus(port[1], './src/socket_disabled.svg')
            soc.setSpeed(port[4])
            soc.setDuplex(port[3])
            soc.setType(port[5])

            soc.getIco().clicked.connect(self.selectRow)
            soc.getIco().customContextMenuRequested.connect(self.showMenu)

            lanSockets.append(soc)

            # parameters.append(str(soc.getId()))
            parameters.append(soc.getCommName())
            parameters.append(soc.getName())
            parameters.append(soc.getStatus())
            parameters.append(soc.getWlan())
            parameters.append(soc.getDuplex())
            parameters.append(soc.getSpeed())
            parameters.append(soc.getType())

            # Заполнение превью комика
            fillingComm.addWidget(soc.getIco(), soc.getPosX(), soc.getPosY(), Qt.AlignCenter)
            # Заполнение таблицы по вебморде
            self.findChild(QTableWidget, 'lanSockets').insertRow(socketId)
            for k in range(self.findChild(QTableWidget, 'lanSockets').columnCount()):
                itm = QTableWidgetItem()
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                itm.setText(parameters[k])
                self.findChild(QTableWidget, 'lanSockets').setItem(socketId, k, itm)

            socketId += 1
            prevComm = currComm
            self.findChild(QGroupBox, 'groupBox').update()


    def enter(self):
        # if self.win.login.text() == '' or self.win.passwd.text() == '' or self.win.port.text() == '':
        #     QMessageBox.warning(self, 'Ошибка при попытке подключения',
        #                         'Неудачная попытка подключения: не все поля заполнены!')  # ошибка входа
        # else:
        self.win.connStatus.setStyleSheet('color:green;text-align:center;')
        self.win.connStatus.setText('Подключение...')
        read_thread = threading.Thread(target=self.connect)
        read_thread.start()
        self.win.ok.setDisabled(True)
        self.win.login.setDisabled(True)
        self.win.passwd.setDisabled(True)
        self.win.port.setDisabled(True)
        self.win.ip.setDisabled(True)
        self.win.setCursor(Qt.CursorShape.WaitCursor)

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # ssh.connect(self.win.ip.text(), username=self.win.login.text(), password=self.win.passwd.text())
            self.ssh.connect('10.16.7.79', username='obi', password='ndszi3917')
            self.channel = self.ssh.invoke_shell()
            if self.channel.active:
                self.win.connStatus.setStyleSheet('color:green;text-align:center;')
                self.win.connStatus.setText('Успешно подключено.')
                self.win.close()
                self.subW.close()
                self.win.connStatus.clear()
            time.sleep(0.5)
            self.channel.send('enable\n')
            time.sleep(0.5)
            output = self.channel.recv(65535)
            self.channel.send('show interface status\n')
            for kaka in range(4):
                time.sleep(0.1)
                self.channel.send(' ')
            while True:
                if self.channel.recv_ready():
                    output = self.channel.recv(65535).decode('utf-8')
                else:
                    break
            #self.readData(output)
            self.xyi.emit(output)

        except TimeoutError:
            self.win.connStatus.setStyleSheet('color:red;text-align:center;font-size:10px;')
            self.win.connStatus.setText('Ошибка аутентификации: Истекло время подключения.')
            self.win.ok.setDisabled(False)
            self.win.login.setDisabled(False)
            self.win.passwd.setDisabled(False)
            self.win.port.setDisabled(False)
            self.win.ip.setDisabled(False)
            self.win.setCursor(Qt.CursorShape.ArrowCursor)

        except paramiko.AuthenticationException:
            self.win.connStatus.setStyleSheet('color:red;text-align:center;font-size:10px;')
            self.win.connStatus.setText('Ошибка аутентификации: Проверьте правильность имени пользователя и пароля.')
            self.win.ok.setDisabled(False)
            self.win.login.setDisabled(False)
            self.win.passwd.setDisabled(False)
            self.win.port.setDisabled(False)
            self.win.ip.setDisabled(False)
            self.win.setCursor(Qt.CursorShape.ArrowCursor)

        except paramiko.SSHException as sshException:
            self.win.connStatus.setStyleSheet('color:red;text-align:center;font-size:10px;')
            self.win.connStatus.setText('Ошибка SSH: ' + str(sshException))
            self.win.ok.setDisabled(False)
            self.win.login.setDisabled(False)
            self.win.passwd.setDisabled(False)
            self.win.port.setDisabled(False)
            self.win.ip.setDisabled(False)
            self.win.setCursor(Qt.CursorShape.ArrowCursor)

        except paramiko.ssh_exception.NoValidConnectionsError as e:
            self.win.connStatus.setStyleSheet('color:red;text-align:center;font-size:10px;')
            self.win.connStatus.setText('Ошибка подключения: ' + str(e))
            self.win.ok.setDisabled(False)
            self.win.login.setDisabled(False)
            self.win.passwd.setDisabled(False)
            self.win.port.setDisabled(False)
            self.win.ip.setDisabled(False)
            self.win.setCursor(Qt.CursorShape.ArrowCursor)




    def onclick(self):
        self.win = AnotherWindow()
        uic.loadUi('./loginForm.ui', self.win)
        self.win.login.addAction(QIcon(QPixmap('./src/login.png')),QLineEdit.LeadingPosition)
        self.win.passwd.addAction(QIcon(QPixmap('./src/password.png')), QLineEdit.LeadingPosition)
        self.win.ip.addAction(QIcon(QPixmap('./src/ip.png')), QLineEdit.LeadingPosition)
        self.win.port.addAction(QIcon(QPixmap('./src/port.png')), QLineEdit.LeadingPosition)
        self.win.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.win.ok.clicked.connect(self.enter)
        self.win.passwd.setEchoMode(QLineEdit.Password)
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"  # Часть регулярного выражения
        ipRegex = QRegExp(
            "^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")  # Само регулярное выражение
        ipValidator = QRegExpValidator(ipRegex, self)  # Валидатор для QLineEdit
        self.win.ip.setValidator(ipValidator)
        self.win.show()

    # Поиск сокета в превью по нажатию на строку таблицы
    def selectSocket(self):
        for lab in lanSockets:
            lab.getIco().setStyleSheet('border:none;:hover {border:3px solid #4DB0A8;border-radius:5px;};')

        commName = self.findChild(QTableWidget, 'lanSockets').item(
            self.findChild(QTableWidget, 'lanSockets').currentRow(), 0).text()
        name = self.findChild(QTableWidget, 'lanSockets').item(
            self.findChild(QTableWidget, 'lanSockets').currentRow(), 1).text()
        for lab in lanSockets:
            if lab.getName() == name and lab.getCommName() == commName:
                lab.getIco().setStyleSheet('border:3px solid #4DB0A8;border-radius:5px;padding:0;margin:0;')

    # Поиск строки по нажатию на сокет
    def selectRow(self, row):
        table = self.findChild(QTableWidget, 'lanSockets')
        table.selectRow(row)
        table.scrollTo(table.selectedIndexes()[0], QAbstractItemView.PositionAtCenter)
        for soc in self.findChildren(LANSocketLabel):
            if soc.getId() != row:
                soc.setStyleSheet('border:none; :hover {border:3px solid #4DB0A8;border-radius:5px;};')
            else:
                soc.setStyleSheet('border:3px solid #4DB0A8;border-radius:5px;padding:0;margin:0;')
        self.editingPort = ports[row]

    def enableDisable(self):
        print(self.editingPort[1])
        if self.editingPort[1] == 'disabled':
            self.channel.send('configure terminal\n')
            time.sleep(0.001)
            self.channel.send(f'interface {self.editingPort[0]}\n')
            time.sleep(0.001)
            self.channel.send('no shutdown\n')
            time.sleep(0.001)
            self.channel.send('exit\n')
            time.sleep(0.001)
            self.channel.send('exit\n')
            time.sleep(0.001)
            self.channel.send('write\n')
        else:
            self.channel.send('configure terminal\n')
            time.sleep(0.001)
            self.channel.send(f'interface {self.editingPort[0]}\n')
            time.sleep(0.001)
            self.channel.send('shutdown\n')
            time.sleep(0.001)
            self.channel.send('exit\n')
            time.sleep(0.001)
            self.channel.send('exit\n')
            time.sleep(0.001)
            self.channel.send('write\n')

        self.check()

    def setTrunk(self):
        self.channel.send('configure terminal\n')
        time.sleep(0.001)
        output = self.channel.recv(65535)
        print(output.decode('utf-8'))
        self.channel.send(f'interface {self.editingPort[0]}\n')
        time.sleep(0.001)
        self.channel.send(f'switchport mode trunk\n')
        output = self.channel.recv(65535).decode('utf-8')
        print(output)
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('write\n')

        self.check()

    def setAccess(self):
        self.channel.send('configure terminal\n')
        time.sleep(0.001)
        output = self.channel.recv(65535)
        print(output.decode('utf-8'))
        self.channel.send(f'interface {self.editingPort[0]}\n')
        time.sleep(0.001)
        self.channel.send(f'switchport mode access\n')
        output = self.channel.recv(65535).decode('utf-8')
        print(output)
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('write\n')

        self.check()

    def editVlan(self):
        self.channel.send('configure terminal\n')
        time.sleep(0.001)
        output = self.channel.recv(65535)
        print(output.decode('utf-8'))
        self.channel.send(f'interface {self.editingPort[0]}\n')
        time.sleep(0.001)
        self.channel.send(f'switchport access vlan {self.vlan}\n')
        output = self.channel.recv(65535).decode('utf-8')
        print(output)
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('write\n')

        self.check()

    # Здесь используй self.vlan
    def setEditedVlan(self, vlan):
        self.vlan = vlan
        print(self.vlan)

    def editVlanShow(self):
        self.editVlanWin = AnotherWindow()
        uic.loadUi('./changeVlanForm.ui', self.editVlanWin)
        self.editVlanWin.apply.clicked.connect(self.editVlan)
        self.editVlanWin.vlan.textEdited.connect(self.setEditedVlan)
        self.editVlanWin.apply.clicked.connect(self.editVlanWin.close)
        self.editVlanWin.show()

    # Контекстное
    def showMenu(self):
        speedMenu = QMenu()
        speedMenu.addAction('auto')
        speedMenu.addAction('100')
        speedMenu.addAction('1000')
        speedMenu.setStyleSheet('QMenu {border:none;background-color:#586578;}'
                                'QMenu::item:selected {background-color:#4DB0A8;border:3px solid #4DB0A8;}'
                                'QMenu::item {color:white;border:3px solid #586578;padding:5px 10px;border-radius:5px;}')
        menu = QMenu()
        menu.setStyleSheet('QMenu {border:1px solid #4DB0A8;background-color:#586578;}'
                           'QMenu::item:selected {background-color:#4DB0A8;border:3px solid #4DB0A8;}'
                           'QMenu::item {color:white;border:3px solid #586578;padding:5px 10px;border-radius:5px;}')
        onOff = QAction(QIcon(QPixmap('./src/onoff.png')), 'Вкл/Выкл')
        onOff.triggered.connect(self.enableDisable)
        editVlan = QAction(QIcon(QPixmap('./src/changeVlan.png')), 'Изменить VLAN')
        editVlan.triggered.connect(self.editVlanShow)
        showVlan = QAction(QIcon(QPixmap('./src/show.png')), 'Показать все VLAN')
        editSpeed = QAction(QIcon(QPixmap('./src/changeSpeed.png')), 'Изменить режим скорости')
        editSpeed.setMenu(speedMenu)
        setTrunk = QAction(QIcon(QPixmap('./src/changeMode.png')), 'Изменить на trunk')
        setTrunk.triggered.connect(self.setTrunk)
        setAccess = QAction(QIcon(QPixmap('./src/changeMode.png')), 'Изменить на access')
        setAccess.triggered.connect(self.setAccess)

        if self.findChild(QTableWidget, 'lanSockets').item(
                self.findChild(QTableWidget, 'lanSockets').currentRow(), 3).text() != 'trunk':
            menu.clear()
            menu.addAction(onOff)
            menu.addAction(editVlan)
            menu.addAction(editSpeed)
            menu.addAction(setTrunk)
        else:
            menu.clear()
            menu.addAction(onOff)
            menu.addAction(editVlan)
            menu.addAction(showVlan)
            menu.addAction(editSpeed)
            menu.addAction(setAccess)
        menu.exec_(QCursor.pos())


app = QApplication(sys.argv)

window = MainWindow()
window.setWindowIcon(QIcon('./src/appIcon.png'))
window.setWindowTitle('Communicator')
window.setMinimumSize(1200, 900)
# ==================================Коннекты===================================

window.findChild(QPushButton, 'exit').clicked.connect(window.close)
window.findChild(QPushButton, 'changeDevice').clicked.connect(window.clearContent)
window.findChild(QPushButton, 'refresh').clicked.connect(window.check)
window.findChild(QTableWidget, 'lanSockets').itemClicked.connect(window.selectSocket)
window.xyi.connect(window.readData)
window.show()
app.exec_()
