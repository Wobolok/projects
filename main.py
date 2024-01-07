import os, sys
import time

import paramiko
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, uic
import threading

socketId = 0
lanSockets = []
path = './commLogos'
images = []

for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
        images.append(os.path.join(path, file))



class LANSocketLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.id = None
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            selectedSocket = self.getId()
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
        self.wlan = None
        self.ip = None
        self.port = None
        self.status = None
        self.imgPath = None
        self.pix = None
        self.ico = None
        self.speed = None

    def setId(self, id):
        self.id = id

    def setPos(self, posX, posY):
        self.posX = posX
        self.posY = posY

    def setWlan(self, wlan):
        self.wlan = wlan

    def setIp(self, ip):
        self.ip = ip

    def setPort(self, port):
        self.port = port

    def setStatus(self, status, imgPath):
        self.status = status
        self.pix = QPixmap(QPixmap(imgPath)).scaled(50, 50, Qt.KeepAspectRatio)
        self.ico = LANSocketLabel()
        self.ico.setPixmap(self.pix)
        self.ico.setId(self.getId())
        self.ico.setOpenExternalLinks(True)
        self.imgPath = imgPath

    def setSpeed(self, speed):
        self.speed = speed

    def getId(self):
        return self.id

    def getPosX(self):
        return self.posX

    def getPosY(self):
        return self.posY

    def getWlan(self):
        return self.wlan

    def getIp(self):
        return self.ip

    def getPort(self):
        return self.port

    def getStatus(self):
        return self.status

    def getImgPath(self):
        return self.imgPath

    def getIco(self):
        return self.ico

    def getSpeed(self):
        return self.speed


class AnotherWindow(QWidget):
    def __init__(self):
        super().__init__()


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

    def enter(self):
        # if (self.win.login.text() == '' or self.win.passwd.text() == '' or self.win.port.text() == ''):
        #     QMessageBox.warning(self, 'Ошибка при попытке подключения',
        #                         'Неудачная попытка подключения: не все поля заполнены!')  # ошибка
        # else:
            read_thread = threading.Thread(target=self.connect)
            read_thread.start()

    def connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            #ssh.connect(self.win.ip.text(), username=self.win.login.text(), password=self.win.passwd.text())
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
        except paramiko.AuthenticationException:
            print("Ошибка аутентификации. Проверьте правильность имени пользователя и пароля.")
        except paramiko.SSHException as sshException:
            print("Ошибка SSH: ", sshException)
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print("Ошибка подключения: ", e)
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
window.setMinimumSize(800, 600)

for i in range(2):
    for j in range(12):
        parameters = []
        soc = LANSocket()
        soc.setId(socketId)
        soc.setPos(i, j)
        soc.setIp('255.255.255.255')
        soc.setPort('2500')
        soc.setWlan('255.255.255.255')
        soc.setStatus(True, './src/lan_free.png')
        soc.setSpeed('100 Mb/s')
        lanSockets.append(soc)

        parameters.append(str(soc.getId()))
        parameters.append(soc.getIco())
        parameters.append(soc.getIp())
        parameters.append(soc.getPort())
        parameters.append(soc.getWlan())
        parameters.append(soc.getSpeed())

        # Заполнение превью комика
        window.findChild(QGridLayout,
                         'socketsPreview').addWidget(soc.getIco(), soc.getPosX(), soc.getPosY(), Qt.AlignCenter)
        # Заполнение таблицы по вебморде
        window.findChild(QTableWidget, 'lanSockets').insertRow(socketId)
        for k in range(window.findChild(QTableWidget, 'lanSockets').columnCount()):

            if k == 1:
                itm = QTableWidgetItem()
                itm.setIcon(QIcon(parameters[k].pixmap()))
                itm.setTextAlignment(Qt.AlignCenter)
                window.findChild(QTableWidget, 'lanSockets').setItem(socketId, k, itm)
            else:
                itm = QTableWidgetItem()
                itm.setText(parameters[k])
                itm.setTextAlignment(Qt.AlignCenter)
                window.findChild(QTableWidget, 'lanSockets').setItem(socketId, k, QTableWidgetItem(parameters[k]))

        socketId += 1


        # Поиск сокета в превью по нажатию на строку таблицы
        def selectSocket():
            for lab in lanSockets:
                lab.getIco().setStyleSheet('border:none;:hover {border:3px solid #FF17365D;border-radius:5px;};')
            num = window.findChild(QTableWidget, 'lanSockets').currentRow()
            for lab in lanSockets:
                if lab.getIco().getId() == num:
                    lab.getIco().setStyleSheet('border:3px solid #FF17365D;border-radius:5px;padding:0;margin:0;')
                    prevSocket = num


        window.findChild(QTableWidget, 'lanSockets').itemClicked.connect(selectSocket)

window.show()

app.exec_()
