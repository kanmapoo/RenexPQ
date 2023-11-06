import sys
from PyQt6.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QFileDialog, QMessageBox, QLabel, QStyleFactory, QTableWidgetItem,QAbstractItemDelegate
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize, Qt
import shutil as SH
import os
import xml.etree.ElementTree as ET
import glob as GL
import re as RE
#from QTableWidgetDragRows import TableWidgetDragRows
from QTableWidgetDropRow import TableWidgetDropRow

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 1000, 500 #dimensions
        self.resize(self.window_width, self.window_height)
        self.setWindowTitle('RenEx - renommage rapide de fichiers')
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.repO = QLineEdit()
        self.lblO = QLabel("Source : ")
        self.lblO.setFixedWidth(60)
        self.lblO.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.finderO = QPushButton()
        self.finderO.setIcon(QIcon('Blue_flat_directory_icon.svg.png'))
        self.finderO.setIconSize(QSize(30, 30))
        self.finderO.setText("Explorer...")
        self.lblF = QLabel("Filtre : ")
        self.lblF.setFixedWidth(60)
        self.lblF.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.filtres = QComboBox()
        self.filtres.setDuplicatesEnabled(False)
        self.fichiers = QTableWidget()
        self.fichiers.setShowGrid(True)
        self.deplacer = QPushButton()
        self.deplacer.setIcon(QIcon('file-transfer.png'))
        self.deplacer.setIconSize(QSize(60, 60))
        self.deplacer.setText("Déplacer !")
        self.nettoyer = QPushButton()
        self.nettoyer.setIcon(QIcon('pngegg.png'))
        self.nettoyer.setIconSize(QSize(60, 60))
        self.nettoyer.setText("Nettoyer (supprimer les répertoires vides)")
        self.regex = TableWidgetDropRow()
        self.regex.setShowGrid(True)

        hbox1.addWidget(self.lblO)
        hbox1.addWidget(self.repO)
        hbox1.addWidget(self.finderO)
        layout.addLayout(hbox1)

        hbox3.addWidget(self.lblF)
        hbox3.addWidget(self.filtres)
        layout.addLayout(hbox3)

        self.filtres.setEditable(True)
        layout.addWidget(self.fichiers)
        self.fichiers.setColumnCount(2)
        self.fichiers.setHorizontalHeaderLabels(["Avant", "Après"])
        self.fichiers.horizontalHeaderItem(0).setBackground(QColor("blue"))
        self.fichiers.horizontalHeaderItem(1).setBackground(QColor(43, 184, 240))
        
        self.fichiers.setColumnWidth(0, 500)
        self.fichiers.setColumnWidth(1, 500)
        self.fichiers.verticalHeader().setVisible(False)

        hbox2.addWidget(self.deplacer)
        hbox2.addWidget(self.nettoyer)
        layout.addLayout(hbox2)
        layout.addWidget(self.regex)
        self.regex.setColumnCount(2)
        self.regex.setHorizontalHeaderLabels(["Remplace...", "...Par"])
        self.regex.horizontalHeaderItem(0).setBackground(QColor("green"))
        self.regex.horizontalHeaderItem(1).setBackground(QColor(50, 237, 56))
        
        self.regex.setColumnWidth(0, 700)
        self.regex.setColumnWidth(1, 300)
        self.regex.verticalHeader().setVisible(False)

        self.lire_config_xml()
        self._liste_fichiers()

        self.finderO.clicked.connect(self._explorer)
        self.filtres.currentTextChanged.connect(self._filtres_changed)
        self.fichiers.cellChanged.connect(self._fichiers_changed)
        self.deplacer.clicked.connect(self._deplacer)
        self.nettoyer.clicked.connect(self._supprimer_repertoires_vides)
        self.regex.cellChanged.connect(self._regex_changed)

    def lire_config_xml(self):
        tree = ET.parse('config.xml')
        scripts = tree.find("scripts")
        filtres = tree.find("filtres")
        i = int(tree.find('filtres').attrib["select"])
        regex = scripts.findall("regex")
        self.repO.setText(tree.find("rep").text)
        self.filtres.insertItems(0, [filtre.text for filtre in filtres.findall("filtre")])
        self.filtres.setCurrentIndex(i)
        self.regex.setRowCount(len(regex)+1)
        for ligne, rpl in enumerate(regex):
            self.regex.setItem(ligne, 0, QTableWidgetItem(rpl.find("remplace").text))
            self.regex.setItem(ligne, 1, QTableWidgetItem(rpl.find("par").text))

    def _deplacer(self, *args):
        for t in range(self.fichiers.rowCount()):
            fo = self.fichiers.item(t, 0).text()
            fd = self.fichiers.item(t, 1).text()
            if fd != "" and fo != fd:
                SH.move(fo, fd)
        self._liste_fichiers()

    def _filtres_changed(self, new_text):
        if new_text == "":
            print(self.filtres.currentIndex())
        else:
            self._liste_fichiers()

    def _explorer(self):
        self.repO.setText(QFileDialog.getExistingDirectory(None, "Nouveau répertoire", self.repO.text(), QFileDialog.Option.ShowDirsOnly))
        self._liste_fichiers()

    def _liste_fichiers(self):
        try:
            f = RE.compile(self.filtres.currentText())
        except RE.error:
            return
        self.fichiers.clearContents()
        liste_brute = GL.glob("%s/**/*" % self.repO.text(), recursive=True)
        liste_filtree = list(filter(f.match, liste_brute))
        max_fichiers = len(liste_filtree)
        if max_fichiers > 30:
            msgBox = QMessageBox()
            msgBox.setText("La liste sera limitée à 30 fichiers\naffinez votre recherche")
            msgBox.exec()
            max_fichiers = 30
        self.fichiers.setRowCount(max_fichiers)
        for ligne, fic in enumerate(liste_filtree):
            if ligne == max_fichiers:
                break
            self.fichiers.setItem(ligne, 0, QTableWidgetItem(fic))
        self.renommer()

    def _fichiers_changed(self, lig, col):
        if col == 0 and self.fichiers.item(lig, 0).text() == "":
                    self.fichiers.removeRow(lig)

    def _regex_changed(self, lig, col):
        if col == 0:
            new_val = self.regex.item(lig, 0).text()
            if lig == self.regex.rowCount()-1 and new_val != "": #On remplit la dernière ligne 
                self.regex.insertRow(self.regex.rowCount()) #on insère une ligne vide en dessous
            if lig != self.regex.rowCount()-1 and new_val == "": #si on vide la col 0 d'une ligne (pas la dernière)
                self.regex.removeRow(lig) #alors, on supprime la ligne

        if self.regex.item(lig, 0) and self.regex.item(lig, 1):
            self.renommer()

    def renommer(self):
        for t in range(self.fichiers.rowCount()):
            fo = self.fichiers.item(t, 0).text()
            fd = self.regex_iteration(fo)
            self.fichiers.setItem(t, 1, QTableWidgetItem(fd))

    def regex_iteration(self, s):
        retour = s
        for u in range(self.regex.rowCount()-1):
            #if self.regex.item(u, 0) and self.regex.item(u, 1):
            #print("u = %d (%s => %s)" % (u, self.regex.item(u, 0).text(), self.regex.item(u, 1).text()))
            to = self.regex.item(u, 0).text()
            td = self.regex.item(u, 1).text()
            if to != "":
                if td == "[null]":
                    td = ''
                r = RE.compile(to, RE.I)
            retour = r.sub(td, retour)
        return retour

    def _supprimer_repertoires_vides(self, *args):
        for root, dirs, _ in os.walk(self.repO.text()):
            for name in dirs:
                vdir = os.path.normpath(os.path.join(root, name))
                try:
                    if not os.listdir(vdir): #repertoire vide
                        os.rmdir(vdir)
                except Exception as e:
                    print(e.__doc__)

    def closeEvent(self, event):
        print('Mise à jour param...')
        config = ET.Element("config")
        ET.SubElement(config, "rep").text = self.repO.text()
        filtres = ET.SubElement(config, "filtres", select=str(self.filtres.currentIndex()))
        for t in range(self.filtres.count()):
            ET.SubElement(filtres, "filtre").text = self.filtres.itemText(t)
        scripts = ET.SubElement(config, "scripts")
        for t in range(self.regex.rowCount()-1):
            regex = ET.SubElement(scripts, "regex")
            if self.regex.item(t, 0) != "":
                ET.SubElement(regex, "remplace").text = self.regex.item(t, 0).text()
                ET.SubElement(regex, "par").text = self.regex.item(t, 1).text()
        tree = ET.ElementTree(config)
        ET.indent(tree)
        tree.write("config.xml", encoding="utf-8", xml_declaration=True)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setStyleSheet('''
        QWidget {
            font-size: 12px;
        }
    ''')

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Fermeture de la fenêtre...')
