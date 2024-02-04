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
    fillPreview = pyqtSignal(str)
    fillDatabase = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)

        w = QWidget()
        uic.loadUi('./mainForm_v2.ui', w)
        w.reboot.setIcon(QIcon('./src/reboot.png'))
        w.exit.setIcon(QIcon('./src/exit.png'))
        w.vlanDB.setIcon(QIcon('./src/db.png'))
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
        self.availableVlans = []

    def clearContent(self):
        gbox = window.findChild(QGroupBox, 'groupBox')
        table = window.findChild(QTableWidget, 'lanSockets')
        table.setRowCount(0)
        for g in gbox.findChildren(QGroupBox):
            g.close()
        self.subW.show()

    def refresh(self):
        try:
            gbox = window.findChild(QGroupBox, 'groupBox')
            table = window.findChild(QTableWidget, 'lanSockets')
            table.setRowCount(0)
            for g in gbox.findChildren(QGroupBox):
                g.close()

            output = self.channel.recv(65535)
            self.channel.send('show running-config switch vlan\n')
            time.sleep(0.1)
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
            self.fillDB(output)

        except:

            data = open('./src/example.txt', 'r')
            output = data.readlines()
            self.readData(output)
            data1 = open('./vlan_test.txt', 'r')
            output1 = data1.readlines()
            self.fillDB(output1)

    def fillDB(self, data_1):
        self.availableVlans.clear()

        file = self.createConfig(data_1)
        data = open('./src/example.txt', 'r').readlines()
        file.close()

        for item in data:
            if item.startswith(' vlan'):
                item = item.split(maxsplit=4)
                if item[2] == 'name':
                    self.availableVlans.append(item)

        self.dbWin = AnotherWindow()
        uic.loadUi('./vlanDBForm.ui', self.dbWin)
        self.dbWin.setWindowIcon(QIcon('./src/database.png'))
        self.dbWin.add.setIcon(QIcon('./src/add.png'))
        self.dbWin.remove.setIcon(QIcon('./src/remove.png'))

        # Коннекты
        self.dbWin.add.clicked.connect(self.addVlanToDatabase)
        self.dbWin.remove.clicked.connect(self.removeVlanFromDatabase)

        # Заполнение таблицы
        table = self.dbWin.database
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        table.setRowCount(len(self.availableVlans))
        for vlan in self.availableVlans:
            num = QTableWidgetItem()
            num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num.setText(vlan[1])

            name = QTableWidgetItem()
            name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name.setText(vlan[3])

            table.setItem(self.availableVlans.index(vlan), 0, num)
            table.setItem(self.availableVlans.index(vlan), 1, name)

    def selectRow(self):
        self.findChild(QTableWidget, 'lanSockets').selectRow()

    def createConfig(self, data):
        with open('./src/example.txt', "w") as file:
            file.write(data)
            return file

    def createConfig1(self, data):
        with open('./src/example1.txt', "w") as file:
            file.write(data)
            return file

    def readData(self, data_1):
        ports.clear()
        lanSockets.clear()
        socketId = 0
        # =====================================Раскомментить=========================================
        file = self.createConfig(data_1)
        data = open('./src/example.txt', 'r').readlines()
        file.close()
        # ==========================Убрать строчку под этим комментом================================
        # data = open('./text_test.txt', 'r').readlines()

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
            self.channel.send('show running-config switch vlan\n')
            time.sleep(0.1)
            self.channel.send('show interface status\n')
            for kaka in range(4):
                time.sleep(0.1)
                self.channel.send(' ')
            while True:
                if self.channel.recv_ready():
                    output = self.channel.recv(65535).decode('utf-8')
                else:
                    break
            self.fillPreview.emit(output)
            self.fillDatabase.emit(output)

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

        self.refresh()

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

        self.refresh()

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

        self.refresh()

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

        self.refresh()

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

    def showVlans(self):
        # Запрос в результате которого output
        self.channel.send(f'show running-config interface {self.editingPort[0]}\n')
        time.sleep(0.1)
        output = self.channel.recv(65535).decode('utf-8')
        print(output)
        file = self.createConfig(output)
        data = open('./src/example.txt', 'r').readlines()
        file.close()

        vlans = []
        result_vlans = []

        for line in data:
            if line.startswith(' switchport trunk'):
                vlans = line.split()[len(line.split()) - 1].split(',')

        for element in vlans:
            if '-' in element:
                start, end = element.split('-')
                result_vlans.extend(list(map(str, range(int(start), int(end) + 1))))
            else:
                result_vlans.append(str(element))

        self.showVlansWin = AnotherWindow()
        uic.loadUi('./vlanDBForm.ui', self.showVlansWin)
        self.showVlansWin.setWindowTitle(f'VLAN на порту {self.editingPort[0].split("port")[1]}')
        self.showVlansWin.setWindowIcon(QIcon('./src/socket.png'))
        self.showVlansWin.add.setIcon(QIcon('./src/add.png'))
        self.showVlansWin.remove.setIcon(QIcon('./src/remove.png'))
        self.showVlansWin.database.removeColumn(1)

        def add():
            if self.addVlanToTrunkWin.vlans.currentText() in result_vlans:
                warn = QMessageBox.warning(self.addVlanToTrunkWin, 'Ошибка при попытке добавления VLAN',
                                           'Данный VLAN уже добавлен на выбранный порт!')

            else:
                self.channel.send('configure terminal\n')
                time.sleep(0.001)
                output = self.channel.recv(65535)
                print(output.decode('utf-8'))
                self.channel.send(f'interface {self.editingPort[0]}\n')
                time.sleep(0.001)
                self.channel.send(f'switchport trunk allowed vlan add {self.addVlanToTrunkWin.vlans.currentText()}\n')
                output = self.channel.recv(65535).decode('utf-8')
                print(output)
                time.sleep(0.001)
                self.channel.send('exit\n')
                time.sleep(0.001)
                self.channel.send('exit\n')
                time.sleep(0.001)
                self.channel.send('write\n')

                newVlan = QTableWidgetItem()
                newVlan.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                newVlan.setText(self.addVlanToTrunkWin.vlans.currentText())

                table.setRowCount(table.rowCount() + 1)
                table.setItem(table.rowCount() - 1, 0, newVlan)
                result_vlans.append(newVlan.text())
                self.addVlanToTrunkWin.close()

        def addVlan():
            self.addVlanToTrunkWin = AnotherWindow()
            uic.loadUi('./addVlanToTrunkForm.ui', self.addVlanToTrunkWin)

            for v in self.availableVlans:
                self.addVlanToTrunkWin.vlans.addItem(v[1])

            self.addVlanToTrunkWin.add.clicked.connect(add)

            self.addVlanToTrunkWin.show()

        def removeVlan():
            selectedVlan = table.currentItem().text()

            self.channel.send('configure terminal\n')
            time.sleep(0.001)
            output = self.channel.recv(65535)
            print(output.decode('utf-8'))
            self.channel.send(f'interface {self.editingPort[0]}\n')
            time.sleep(0.001)
            self.channel.send(f'switchport trunk allowed vlan remove {selectedVlan}\n')
            output = self.channel.recv(65535).decode('utf-8')
            print(output)
            time.sleep(0.001)
            self.channel.send('exit\n')
            time.sleep(0.001)
            self.channel.send('exit\n')
            time.sleep(0.001)
            self.channel.send('write\n')

            result_vlans.remove(selectedVlan)
            table.removeRow(table.currentRow())

        # Коннекты
        self.showVlansWin.add.clicked.connect(addVlan)
        self.showVlansWin.remove.clicked.connect(removeVlan)

        # Заполнение таблицы
        table = self.showVlansWin.database
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        table.setRowCount(len(result_vlans))
        for vlan in result_vlans:
            num = QTableWidgetItem()
            num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num.setText(vlan)

            table.setItem(vlans.index(vlan), 0, num)

        self.showVlansWin.show()

    def setUnlocked(self):
        self.channel.send('configure terminal\n')
        time.sleep(0.001)
        output = self.channel.recv(65535)
        print(output.decode('utf-8'))
        self.channel.send(f'interface {self.editingPort[0]}\n')
        time.sleep(0.001)
        self.channel.send(f'no switchport port-security\n')
        output = self.channel.recv(65535).decode('utf-8')
        print(output)
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('write\n')

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
        showVlan.triggered.connect(self.showVlans)
        editSpeed = QAction(QIcon(QPixmap('./src/changeSpeed.png')), 'Изменить режим скорости')
        editSpeed.setMenu(speedMenu)
        setTrunk = QAction(QIcon(QPixmap('./src/changeMode.png')), 'Изменить на trunk')
        setTrunk.triggered.connect(self.setTrunk)
        setAccess = QAction(QIcon(QPixmap('./src/changeMode.png')), 'Изменить на access')
        setAccess.triggered.connect(self.setAccess)
        unlock = QAction(QIcon(QPixmap('./src/unlock.png')), 'Снять защиту')
        unlock.triggered.connect(self.setUnlocked)

        if self.findChild(QTableWidget, 'lanSockets').item(
                self.findChild(QTableWidget, 'lanSockets').currentRow(), 3).text() != 'trunk':
            menu.clear()
            menu.addAction(onOff)
            menu.addAction(editVlan)
            menu.addAction(editSpeed)
            menu.addAction(setTrunk)
            menu.addAction(unlock)
        else:
            menu.clear()
            menu.addAction(onOff)
            menu.addAction(showVlan)
            menu.addAction(editSpeed)
            menu.addAction(setAccess)
            menu.addAction(unlock)
        menu.exec_(QCursor.pos())

    def addVlanToDatabase(self):
        self.addVlanWin = AnotherWindow()
        uic.loadUi('./addVlanForm.ui', self.addVlanWin)

        def addVlan():
            if self.addVlanWin.name.text() == '' or self.addVlanWin.vlan.text() == '':
                warn = QMessageBox.warning(self.addVlanWin, 'Ошибка при попытке добавления VLAN',
                                           'Пожалуйста, заполните все поля!')
            else:
                self.channel.send('configure terminal\n')
                time.sleep(0.001)
                self.channel.send('vlan database\n')
                time.sleep(0.001)
                self.channel.send(f'vlan {self.addVlanWin.vlan.text()} name {self.addVlanWin.name.text()}\n')
                time.sleep(0.001)
                self.channel.send('exit\n')
                time.sleep(0.001)
                self.channel.send('exit\n')
                time.sleep(0.001)
                self.channel.send('write\n')
                table = self.dbWin.database
                table.setRowCount(table.rowCount() + 1)

                num = QTableWidgetItem()
                num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                num.setText(self.addVlanWin.vlan.text())

                name = QTableWidgetItem()
                name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                name.setText(self.addVlanWin.name.text())

                table.setItem(table.rowCount() - 1, 0, num)
                table.setItem(table.rowCount() - 1, 1, name)
                self.availableVlans.append(['vlan', num.text(), 'name', name.text()])
                self.addVlanWin.close()

        self.addVlanWin.add.clicked.connect(addVlan)

        self.addVlanWin.show()

    def removeVlanFromDatabase(self):
        table = self.dbWin.database
        vlan = table.selectedItems()[0].text()
        self.channel.send('configure terminal\n')
        time.sleep(0.001)
        self.channel.send('vlan database\n')
        time.sleep(0.001)
        self.channel.send(f'no vlan {vlan}\n')
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('exit\n')
        time.sleep(0.001)
        self.channel.send('write\n')
        table.removeRow(table.currentRow())
        self.availableVlans.remove(self.availableVlans[table.currentRow() + 1])

    def showDatabase(self):
        self.dbWin.show()

    def reboot(self):
        answer = QMessageBox.question(self.centralWidget(), "Перезапуск устройства",
                                      "Вы действительно желаете перезапустить устройство?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if answer == QMessageBox.Yes:
            self.loadingWin = AnotherWindow()
            uic.loadUi('./loadingForm.ui', self.loadingWin)
            self.loadingWin.setWindowFlags(Qt.FramelessWindowHint)
            self.channel.send('reboot\n')
            time.sleep(0.001)
            self.channel.send('Y\n')

            timer = QTimer(self)
            timer.timeout.connect(self.loadingWin.close, 120000)
            timer.timeout.connect(self.clearContent, 120000)
            self.loadingWin.show()
            timer.start(120000)
        elif answer == QMessageBox.No:
            pass
app = QApplication(sys.argv)

window = MainWindow()
window.setWindowIcon(QIcon('./src/appIcon.png'))
window.setWindowTitle('Communicator')
window.setMinimumSize(1200, 900)
# ==================================Коннекты===================================

window.findChild(QPushButton, 'exit').clicked.connect(window.close)
window.findChild(QPushButton, 'changeDevice').clicked.connect(window.clearContent)
window.findChild(QPushButton, 'refresh').clicked.connect(window.refresh)
window.findChild(QTableWidget, 'lanSockets').itemClicked.connect(window.selectSocket)
window.findChild(QPushButton, 'vlanDB').clicked.connect(window.showDatabase)
window.findChild(QPushButton, 'reboot').clicked.connect(window.reboot)
window.fillPreview.connect(window.readData)
window.fillDatabase.connect(window.fillDB)
window.show()
app.exec_()
