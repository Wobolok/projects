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
        if ev.button() == Qt.LeftButton:
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
        elemText = svgDoc.documentElement().firstChildElement()
        text = elemText.elementsByTagName('text')
        if text.size() and text.at(0).isElement():
            elem = text.at(0).toElement()
            elem.childNodes().at(0).setNodeValue(self.name)
        # elemText.firstChild().toText().setData(self.name)
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

    def selectRow(self):
        self.findChild(QTableWidget, 'lanSockets').selectRow(selectedSocket)

    def readData(self, data):
        ports.clear()
        lanSockets.clear()
        socketId = 0
        file = open('./text_test.txt', 'r')
        data = file.readlines()
        for line in data:
            if line.startswith('port'):
                if len(line.split()) > 5:
                    ports.append(line.split(maxsplit=5))

    def enter(self):
        if self.win.login.text() == '' or self.win.passwd.text() == '' or self.win.port.text() == '':
            QMessageBox.warning(self, 'Ошибка при попытке подключения',
                                'Неудачная попытка подключения: не все поля заполнены!')  # ошибка входа
        else:
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
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # ssh.connect(self.win.ip.text(), username=self.win.login.text(), password=self.win.passwd.text())
            ssh.connect('10.16.7.74', username='obi', password='ndszi3917')
            channel = ssh.invoke_shell()
            time.sleep(1)
            channel.send('enable\n')
            time.sleep(1)
            output = channel.recv(65535)
            channel.send('screen-length 0 temporary\n')
            print(output.decode('utf-8'))
            channel.send('show running-config\n')
            for kaka in range(10):
                time.sleep(1)
                channel.send(' ')
            while True:
                if channel.recv_ready():
                    output = channel.recv(65535).decode('utf-8')
                    print(output)
                else:
                    break
            output = channel.recv(65535)
            print(output.decode('utf-8'))

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

        finally:
            ssh.close()

    def onclick(self):
        self.win = AnotherWindow()
        uic.loadUi('./loginForm.ui', self.win)
        self.win.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.win.ok.clicked.connect(self.enter)
        self.win.passwd.setEchoMode(QLineEdit.Password)
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"  # Часть регулярного выражения
        ipRegex = QRegExp(
            "^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")  # Само регулярное выражение
        ipValidator = QRegExpValidator(ipRegex, self)  # Валидатор для QLineEdit
        self.win.ip.setValidator(ipValidator)
        self.win.show()


app = QApplication(sys.argv)

window = MainWindow()
window.setWindowIcon(QIcon('./src/appIcon.png'))
window.setWindowTitle('Communicator')
window.setMinimumSize(1200, 900)

window.readData('')

if len(ports) != 0:
    fillingComm = window.findChild(QGridLayout, 'socketsPreview')
    window.findChild(QGroupBox, 'groupBox_2').setTitle('Коммутатор ' + ports[0][0][4])

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
            gb.setStyleSheet('QWidget {background-color:#dfdfdfff;} QGroupBox:title {subcontrol-origin: '
                             'margin;subcontrol-position: top'
                             'center;border-top-left-radius:'
                             '15px;border-top-right-radius: 15px;padding: 5px 50px;background-color: #FF17365D;color: '
                             'rgb(255, 255, 255);};')
            window.findChild(QGroupBox, 'groupBox').layout().addWidget(gb)
            fillingComm = comm

        j = ports.index(port)
        parameters = []
        soc = LANSocket()
        soc.setId(socketId)
        soc.setWlan(port[2])
        soc.setName(port[0].split('.')[2])
        if (int(soc.getName())) % 2 == 0:
            soc.setPos(1, int(soc.getName()) - fillingComm.columnCount()+1)
        else:
            soc.setPos(0, int(soc.getName()) - fillingComm.columnCount()+1)
        soc.setCommName(port[0][4])
        if port[1] == 'notconnect':
            soc.setStatus(port[1], './src/socket_free.svg')
        elif port[1] == 'connected' and port[2] == 'trunk':
            soc.setStatus(port[1], './src/socket_trunk.svg')
        elif port[1] == 'connected' and port[2] != 'trunk':
            soc.setStatus(port[1], './src/socket_used.svg')
        soc.setSpeed(port[4])
        soc.setDuplex(port[3])
        soc.setType(port[5])
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
        window.findChild(QTableWidget, 'lanSockets').insertRow(socketId)
        for k in range(window.findChild(QTableWidget, 'lanSockets').columnCount()):
            itm = QTableWidgetItem()
            itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            itm.setText(parameters[k])
            window.findChild(QTableWidget, 'lanSockets').setItem(socketId, k, itm)

        socketId += 1
        prevComm = currComm


    # Поиск сокета в превью по нажатию на строку таблицы
    def selectSocket():
        for lab in lanSockets:
            lab.getIco().setStyleSheet('border:none;:hover {border:3px solid #FF17365D;border-radius:5px;};')

        commName = window.findChild(QTableWidget, 'lanSockets').item(window.findChild(QTableWidget, 'lanSockets').currentRow(), 0).text()
        name = window.findChild(QTableWidget, 'lanSockets').item(window.findChild(QTableWidget, 'lanSockets').currentRow(), 1).text()
        for lab in lanSockets:
            if lab.getName() == name and lab.getCommName() == commName:
                print('clicked')
                lab.getIco().setStyleSheet('border:3px solid #FF17365D;border-radius:5px;padding:0;margin:0;')

    def selectRow(row):
        window.findChild(QTableWidget, 'lanSockets').selectRow(row)
        for soc in window.findChildren(LANSocketLabel):
            if soc.getId() != row:
                soc.setStyleSheet('border:none; :hover {border:3px solid #FF17365D;border-radius:5px;};')
            else:
                soc.setStyleSheet('border:3px solid #FF17365D;border-radius:5px;padding:0;margin:0;')

    def showMenu():
        menu = QMenu()
        menu.setStyleSheet('border-radius:10px;border:3px solid #FF17365D;')
        editVlan = QAction(QIcon(QPixmap('./src/changeVlan.png')), 'Изменить VLAN')
        editSpeed = QAction(QIcon(QPixmap('./src/changeSpeed.png')), 'Изменить режим скорости')
        setTrunk = QAction(QIcon(QPixmap('./src/changeMode.png')), 'Изменить на trunk')
        setAccess = QAction(QIcon(QPixmap('./src/changeSpeed.png')), 'Изменить на access')
        menu.addAction(editVlan)
        menu.addAction(editSpeed)
        menu.addAction(setTrunk)
        menu.exec_(QCursor.pos())


    window.findChild(QTableWidget, 'lanSockets').itemClicked.connect(selectSocket)
    for soc in window.findChildren(LANSocketLabel):
        soc.clicked.connect(selectRow)
        soc.customContextMenuRequested.connect(showMenu)

window.show()

app.exec_()
