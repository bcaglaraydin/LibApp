from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sqlite3
import sys

'''Importing page designs'''
from add_window import *
from delete_window import *
from search_window import *

global conn
global curr

conn = sqlite3.connect("libdata.db")
curr = conn.cursor()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        '''Add new table into the database if it doesn't exists'''
        curr.execute(
            'CREATE TABLE IF NOT EXISTS books('
            'ID INTEGER PRIMARY KEY AUTOINCREMENT,'
            'Name TEXT NOT NULL,'
            'Author TEXT NOT NULL,'
            'Publisher TEXT NOT NULL,'
            'Stand TEXT NOT NULL)')

        '''Basic Main Window settings'''
        self.setWindowIcon(QIcon('icon/lib.png'))
        self.setWindowTitle("LibApp")
        self.setMinimumSize(800, 600)

        '''Add table wigdet'''
        self.tableWidget = QTableWidget()
        self.setCentralWidget(self.tableWidget)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.tableWidget.setHorizontalHeaderLabels(("ID", "Name", "Author", "Publisher", "Stand"))
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        '''Add toolbar'''
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        '''Add statusbar'''
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        '''Add buttons -> Add, Delete, Search ,Refresh ,Clear ,Exit'''
        but_add = QAction(QIcon("icon/add.jpg"), "Add Book", self)
        but_add.triggered.connect(self.add)
        but_add.setStatusTip("Add Book")
        toolbar.addAction(but_add)

        but_delete = QAction(QIcon("icon/delete.png"), "Delete", self)
        but_delete.triggered.connect(self.delete)
        but_delete.setStatusTip("Delete Book")
        toolbar.addAction(but_delete)

        but_search = QAction(QIcon("icon/search.png"), "Search", self)
        but_search.triggered.connect(self.search)
        but_search.setStatusTip("Search Book")
        toolbar.addAction(but_search)

        but_ref = QAction(QIcon("icon/refresh.png"), "Refresh", self)
        but_ref.triggered.connect(self.load)
        but_ref.setStatusTip("Refresh Table")
        toolbar.addAction(but_ref)

        but_clear = QAction(QIcon("icon/clear.png"), "Clear", self)
        but_clear.triggered.connect(self.clear)
        but_clear.setStatusTip("Clear Table")
        toolbar.addAction(but_clear)

        but_exit = QAction(QIcon("icon/exit.png"), "Exit", self)
        but_exit.triggered.connect(self.exit)
        but_exit.setStatusTip("Exit App")
        toolbar.addAction(but_exit)

    '''Clears the tablewidget and database'''
    def clear(self):
        q_clear = QMessageBox.critical(self, "Clear Database", "The whole table and the database will be cleared!",
                                       QMessageBox.Yes, QMessageBox.No)
        if q_clear == QMessageBox.Yes:
            curr.execute("DELETE FROM books")
            conn.commit()
            self.load()
        else:
            self.show()

    '''Loads content from database into tablewidget'''
    def load(self):
        query = "SELECT * FROM books"
        result = curr.execute(query)

        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    '''Exit App'''
    def exit(self):
        q_exit = QMessageBox.question(self, "Exit", "Are you sure you want to exit?", QMessageBox.Yes | QMessageBox.No)
        if q_exit == QMessageBox.Yes:
            conn.close()
            sys.exit(app.exec_())
        else:
            self.show()

    '''Functions in order to create correct object'''
    def add(self):
        add_page = Add()
        add_page.setWindowFlags(add_page.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        add_page.exec_()

    def delete(self):
        delete_page = Delete()
        delete_page.setWindowFlags(delete_page.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        delete_page.exec_()

    def search(self):
        search_page = Search()
        search_page.setWindowFlags(search_page.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        search_page.exec_()


'''
Every class includes:
A constructor which prepares and shows the window 
A function to operate
'''

class Search(QDialog):
    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)

        self.ui_search = Ui_search_Window()
        self.ui_search.setupUi(self)
        self.ui_search.search_but.clicked.connect(self.search_record)
        self.ui_search.cancel_but.clicked.connect(self.close)
        '''Edit stand combobox'''
        curr.execute("SELECT DISTINCT Stand FROM books")
        stand_list = curr.fetchall()
        s = 0
        stands = [elt[s] for elt in stand_list]

        self.ui_search.stand_box.addItem(" ")
        self.ui_search.stand_box.addItems(stands)
        self.show()

    def search_record(self):
        id_in = self.ui_search.id_line.text()
        name_in = self.ui_search.name_line.text()
        author_in = self.ui_search.author_line.text()
        pub_in = self.ui_search.pub_line.text()
        stand_in = self.ui_search.stand_box.currentText()

        query = "SELECT * FROM books WHERE ID=? OR Name=? OR Author=? OR Publisher=? OR Stand=?"
        data = (id_in, name_in, author_in, pub_in, stand_in)
        curr.execute(query, data)
        conn.commit()

        '''Show result on table'''
        window.tableWidget.clearContents()
        for row_number, row_data in enumerate(curr):
            window.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                window.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        self.close()


class Add(QDialog):
    def __init__(self, *args, **kwargs):
        super(Add, self).__init__(*args, **kwargs)

        self.ui_add = Ui_add_Window()
        self.ui_add.setupUi(self)
        self.ui_add.addbook_button.clicked.connect(self.add_record)
        self.ui_add.addpageCancel_but.clicked.connect(self.close)
        self.show()

    def add_record(self):
        name_in = self.ui_add.name_line.text()
        author_in = self.ui_add.author_line.text()
        pub_in = self.ui_add.pub_line.text()
        stand_in = self.ui_add.stand_line.text()

        insert_query = '''INSERT INTO books(Name,Author,Publisher,Stand)
                          VALUES (?,?,?,?);'''
        data = (name_in, author_in, pub_in, stand_in)
        curr.execute(insert_query, data)
        conn.commit()

        add_exit = QMessageBox.information(self, "Success", "The book successfully added!", QMessageBox.Ok)
        if add_exit == QMessageBox.Ok:
            self.close()
            window.load()


class Delete(QDialog):
    def __init__(self, *args, **kwargs):
        super(Delete, self).__init__(*args, **kwargs)

        self.ui_delete = Ui_delete_Window()
        self.ui_delete.setupUi(self)
        self.ui_delete.delete_button.clicked.connect(self.delete_record)
        self.ui_delete.cancel_button.clicked.connect(self.close)
        self.show()

    def delete_record(self):
        q_delete = QMessageBox.warning(self, "Delete Book", "The record will be deleted",
                                       QMessageBox.Ok, QMessageBox.Cancel)
        if q_delete == QMessageBox.Ok:
            deleted = self.ui_delete.lineEdit.text()
            try:
                '''Check if the record exists'''
                curr.execute("SELECT count(*)  FROM books WHERE ID = '%s' OR Name = '%s' OR Author = '%s' OR Publisher = '%s' OR Stand = '%s'"
                             % (deleted, deleted, deleted, deleted, deleted))
                found = curr.fetchone()[0]

                if found == 0:
                    not_found = QMessageBox.information(self, "Warning", "The book does not exists!", QMessageBox.Ok)
                    if not_found == QMessageBox.Ok:
                        self.close()
                else:
                    curr.execute(
                        "DELETE FROM books WHERE ID = '%s' OR Name = '%s' OR Author = '%s' OR Publisher = '%s' OR Stand = '%s'"
                        % (deleted, deleted, deleted, deleted, deleted))
                    conn.commit()

                    delete_exit = QMessageBox.information(self, "Success", "The book successfully deleted!", QMessageBox.Ok)
                    if delete_exit == QMessageBox.Ok:
                        self.close()
                        window.load()
            except Exception as error:
                self.statusbar.showMessage("Error:"+str(error))
        else:
            self.close()


app = QApplication(sys.argv)
if QDialog.Accepted:
    window = MainWindow()
    window.show()
    window.load()
sys.exit(app.exec_())
