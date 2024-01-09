import os, sys
import time

import paramiko
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtXml import QDomDocument, QDomElement, QDomNode
from PyQt5.QtSvg import QSvgRenderer
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


class LANSocketLabel(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.id = None
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

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
        # xml_reader = QDomDocument()
        # with open(imgPath, 'r') as file:
        #     xml_reader.setContent(file.read())
        #
        # # Replace text within the SVG
        # node = xml_reader.firstChild()
        # while not node.isNull():
        #     if node.isElement():
        #         element = node.toElement()
        #         if element.tagName() == 'text' and element.text() != str(self.id):
        #             element.setNodeValue(str(self.id))
        #     node = node.nextSibling()
        #
        # renderer = QSvgRenderer(xml_reader.toByteArray())
        # image = QImage(48, 48, QImage.Format_ARGB32)
        # image.fill(0)
        # painter = QPainter(image)
        # renderer.render(painter)
        # painter.end()
        self.pix = QPixmap(QPixmap(imgPath).scaled(50, 50, Qt.KeepAspectRatio))
        self.ico = LANSocketLabel()
        self.ico.setPixmap(self.pix)
        self.ico.setId(self.getId())
        self.ico.setOpenExternalLinks(True)
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
window.setMinimumSize(1000, 600)

window.readData('')

if len(ports) != 0:
    commLabel = QLabel()
    commLabel.setText('Коммутатор' + ports[0][0][4])
    window.findChild(QGroupBox, 'groupBox').layout().addWidget(commLabel)

    fillingComm = window.findChild(QGridLayout, 'socketsPreview')

    for port in ports:
        currComm = port[0][4]

        if prevComm is not None and prevComm != currComm:
            comm = QGridLayout()
            comm.setObjectName('socketsPreview' + currComm)
            nextCommLabel = QLabel()
            nextCommLabel.setText('Коммутатор' + currComm)
            window.findChild(QGroupBox, 'groupBox').layout().addWidget(nextCommLabel)
            window.findChild(QGroupBox, 'groupBox').layout().addLayout(comm)
            fillingComm = comm

        j = ports.index(port)
        parameters = []
        soc = LANSocket()
        soc.setId(socketId)
        if (soc.getId() + 1) % 2 == 0:
            soc.setPos(1, j-1)
        else:
            soc.setPos(0, j)
        soc.setWlan(port[2])
        soc.setName(port[0].split('.')[2])
        soc.setCommName(port[0][4])
        if port[1] == 'notconnect':
            soc.setStatus(port[1], './src/lan_free.png')
        elif port[1] == 'connected' and port[2] == 'trunk':
            soc.setStatus(port[1], './src/lan_root.png')
        elif port[1] == 'connected' and port[2] != 'trunk':
            soc.setStatus(port[1], './src/lan_used.png')
        soc.setSpeed(port[4])
        soc.setDuplex(port[3])
        soc.setType(port[5])
        lanSockets.append(soc)

        parameters.append(str(soc.getId()))
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
            itm.setText(parameters[k])
            itm.setTextAlignment(Qt.AlignCenter)
            window.findChild(QTableWidget, 'lanSockets').setItem(socketId, k, QTableWidgetItem(parameters[k]))

        socketId += 1
        prevComm = currComm


    # Поиск сокета в превью по нажатию на строку таблицы
    def selectSocket():
        for lab in lanSockets:
            lab.getIco().setStyleSheet('border:none;:hover {border:3px solid #FF17365D;border-radius:5px;};')

        commName = window.findChild(QTableWidget,'lanSockets').item(window.findChild(QTableWidget, 'lanSockets').currentRow(), 1).text()
        name = window.findChild(QTableWidget,'lanSockets').item(window.findChild(QTableWidget, 'lanSockets').currentRow(), 2).text()
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


    window.findChild(QTableWidget, 'lanSockets').itemClicked.connect(selectSocket)
    for soc in window.findChildren(LANSocketLabel):
        soc.clicked.connect(selectRow)

window.show()

app.exec_()
