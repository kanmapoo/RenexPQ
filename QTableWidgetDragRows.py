from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QTableView
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class TableWidgetDragRows(QTableWidget):
    def __init__(self, *args, **kwargs):
        QTableWidget.__init__(self, *args, **kwargs)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def dropEvent(self, event):
        if event.source() == self and (event.dropAction() == Qt.DropAction.MoveAction or self.dragDropMode() == QAbstractItemView.DragDropMode.InternalMove):
            success, row, _, _ = self.dropOn(event)
            if success:
                selRows = self.getSelectedRowsFast()

                top = selRows[0]
                # print 'top is %d'%top
                dropRow = row
                if dropRow == -1:
                    dropRow = self.rowCount()
                # print 'dropRow is %d'%dropRow
                offset = dropRow - top
                # print 'offset is %d'%offset

                for i, row in enumerate(selRows):
                    r = row + offset
                    if r > self.rowCount() or r < 0:
                        r = 0
                    self.insertRow(r)
                    # print 'inserting row at %d'%r

                selRows = self.getSelectedRowsFast()
                # print 'selected rows: %s'%selRows

                top = selRows[0]
                # print 'top is %d'%top
                offset = dropRow - top
                # print 'offset is %d'%offset
                for i, row in enumerate(selRows):
                    r = row + offset
                    if r > self.rowCount() or r < 0:
                        r = 0

                    for j in range(self.columnCount()):
                        source = QTableWidgetItem(self.item(row, j))
                        self.setItem(r, j, source)
                event.accept()

        else:
            QTableView.dropEvent(event)

    def getSelectedRowsFast(self):
        selRows = []
        for item in self.selectedItems():
            if item.row() not in selRows:
                selRows.append(item.row())
        return selRows

    def droppingOnItself(self, event, index):
        dropAction = event.dropAction()

        if self.dragDropMode() == QAbstractItemView.DragDropMode.InternalMove:
            dropAction = Qt.DropAction.MoveAction

        if event.source() == self and event.possibleActions() & Qt.DropAction.MoveAction and dropAction == Qt.DropAction.MoveAction:
            selectedIndexes = self.selectedIndexes()
            child = index
            while child.isValid() and child != self.rootIndex():
                if child in selectedIndexes:
                    return True
                child = child.parent()

        return False

    def dropOn(self, event): 
        if event.isAccepted():
            return False, None, None, None

        index = QModelIndex()
        row = -1
        col = -1
        if self.viewport().rect().contains(int(event.position().x()), int(event.position().y())):
            
            index = self.indexAt(QPoint(int(event.position().x()), int(event.position().y())))
            if not index.isValid() or not self.visualRect(index).contains(QPoint(int(event.position().x()), int(event.position().y()))):
                index = self.rootIndex()

        if self.model().supportedDropActions() & event.dropAction():
            if index != self.rootIndex():
                dropIndicatorPosition = self.position(event.position(), self.visualRect(index), index)

                if dropIndicatorPosition == QAbstractItemView.DropIndicatorPosition.AboveItem:
                    row = index.row()
                    col = index.column()
                elif dropIndicatorPosition == QAbstractItemView.DropIndicatorPosition.BelowItem:
                    row = index.row() + 1
                    col = index.column()
                else:
                    row = index.row()
                    col = index.column()

            if not self.droppingOnItself(event, index):
                return True, row, col, index
        return False, None, None, None

    def position(self, pos, rect, index):
        r = QAbstractItemView.viewport
        margin = 2
        if pos.y() - rect.top() < margin:
            r = QAbstractItemView.DropIndicatorPosition.AboveItem
        elif rect.bottom() - pos.y() < margin:
            r = QAbstractItemView.DropIndicatorPosition.BelowItem
        elif rect.contains(pos.toPoint(), True):
            r = QAbstractItemView.DropIndicatorPosition.OnItem

        if r == QAbstractItemView.DropIndicatorPosition.OnItem and not (self.model().flags(index) & Qt.ItemFlag.ItemIsDropEnabled):
            r = QAbstractItemView.DropIndicatorPosition.AboveItem if pos.y() < rect.center().y() else QAbstractItemView.DropIndicatorPosition.BelowItem
        return r
