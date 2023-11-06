import typing
from PyQt6 import QtCore
from PyQt6.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem, QWidget
from PyQt6.QtGui import QDropEvent
from PyQt6.QtCore import QChildEvent, QEvent

class TableWidgetDropRow(QTableWidget):
    def __init__(self, *args, **kwargs):
        QTableWidget.__init__(self, *args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)


    def dropEvent(self, event: QDropEvent):
        print('dropevent')
        orig = self.selectedItems()
        ligneO = orig[0].row()
        dest = self.itemAt(int(event.position().x()), int(event.position().y()))
        if not isinstance(dest, QTableWidgetItem):
            return
        ligneD = dest.row()
        
        if ligneO != ligneD:
            self.blockSignals(True) #blockage de signal "changed" en début de ligne
            self.insertRow(ligneD)
            c = 0
            for c, cell in enumerate(orig):
                if c == len(orig)-1: 
                    self.blockSignals(False) #on débloque le signal en fin de ligne, pour avoir un seul "changed" par ligne et pas par cellule
                self.setItem(ligneD, c, QTableWidgetItem(cell.text()))
            if ligneO > ligneD:   
                self.removeRow(ligneO+1)
            else:
                self.removeRow(ligneO)
    
