import json
import sqlite3
import sys
import string
import secrets

import qrcode
from PIL import ImageQt
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QGroupBox, QPushButton, QInputDialog
from fbs_runtime.application_context.PyQt5 import ApplicationContext


def loadlist():
    userlist.clear()

    execlist = cur.execute(f'SELECT * FROM {settings["tablename"]}')
    listinfo = execlist.fetchall()

    for row in listinfo:
        userlist.addTopLevelItem(QTreeWidgetItem([f'{row[0]}', f'{row[1]}', f'{row[2]}', f'{row[3]}']))


def adduser():
    vards, status = QInputDialog.getText(window, 'Naudotojo pridėjimas', 'Įveskite naudotojo vardą:')
    pavrd, status = QInputDialog.getText(window, 'Naudotojo pridėjimas', 'Įveskite naudotojo pavardę:')

    pswrd = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(9))
    usrnm = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(9))

    if pavrd:
        cur.execute("INSERT INTO IIA (first_name, last_name, username, password) VALUES (?, ?, ?, ?)",
                    (str(vards), str(pavrd), str(usrnm), str(pswrd)))
        con.commit()

        loadlist()


@QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
def listass(it):
    namelabel.setText('Vardas - ' + it.text(0))
    surnamelabel.setText('Pavardė - ' + it.text(1))

    image = qrcode.make(f'WIFI:T:WPA;S:{settings["networkname"]};I:{it.text(2)};P:{it.text(3)}')

    QtImage1 = ImageQt.ImageQt(image)
    QtImage2 = QImage(QtImage1)
    pixmap = QPixmap.fromImage(QtImage2)

    pic.setPixmap(pixmap)
    pic.setAlignment(QtCore.Qt.AlignCenter)


if __name__ == '__main__':
    appctxt = ApplicationContext()

    # Load settings
    settings = json.load(open(appctxt.get_resource('config.json')))

    # Init window
    window = QWidget()
    window.setWindowTitle(settings['appname'])

    window.setContentsMargins(10, 10, 10, 10)
    window.setMinimumSize(1280, 800)

    # Main layout
    mainlayout = QHBoxLayout()
    window.setLayout(mainlayout)

    # User list
    userlist = QTreeWidget()
    userlist.itemClicked.connect(listass)
    userlist.setColumnCount(4)
    userlist.setHeaderLabels(['Vardas', 'Pavardė', 'Prisijungimo vardas', 'Slaptažodis'])
    mainlayout.addWidget(userlist, 6)

    # Info layout
    infotab = QVBoxLayout()
    infotab.setContentsMargins(10, 0, 0, 0)
    mainlayout.addLayout(infotab, 4)

    pic = QLabel()
    infotab.addWidget(pic)

    groupbox = QGroupBox()
    groupbox.setTitle('Naudotojo informacija')
    infotab.addWidget(groupbox)

    infolayout = QVBoxLayout()
    groupbox.setLayout(infolayout)

    namelabel = QLabel()
    namelabel.setText('Vardas -')
    infolayout.addWidget(namelabel)

    surnamelabel = QLabel()
    surnamelabel.setText('Pavardė -')
    infolayout.addWidget(surnamelabel)

    addbutton = QPushButton()
    addbutton.setText('Pridėti naudotoją')
    addbutton.clicked.connect(adduser)
    infotab.addWidget(addbutton)

    con = sqlite3.connect(appctxt.get_resource(settings['database']))
    cur = con.cursor()

    loadlist()

    image = qrcode.make(settings['defaultqr'])
    QtImage1 = ImageQt.ImageQt(image)
    QtImage2 = QImage(QtImage1)
    pixmap = QPixmap.fromImage(QtImage2)

    pic.setPixmap(pixmap)
    pic.setAlignment(QtCore.Qt.AlignCenter)

    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
