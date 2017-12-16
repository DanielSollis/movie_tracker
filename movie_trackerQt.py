from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGridLayout, QMainWindow, QAction, \
    QTreeView, QFileSystemModel
from PyQt5 import QtCore
import hachoir_core
from hachoir_metadata import extractMetadata
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser

import time
import os
import sys

#CLASSES
class Qt_window(QMainWindow):
    def __init__(self):
        super(Qt_window, self).__init__()
        self.grid = QGridLayout()
        self.main_window = QWidget(self)
        self.initUI()

    def initUI(self):
        self.show()
        self.setCentralWidget(self.main_window)
        self.setGeometry(600, 300, 650, 450)
        self.setWindowTitle("Movie Tracker")
        self.set_grid_layout()
        self.create_menu_bar()
        self.create_clock()

    def set_grid_layout(self):
        grid = QGridLayout()
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 100)
        grid.setRowStretch(1, 1)
        self.main_window.setLayout(grid)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")

        add_movie_action = QAction("Add Movie", self)
        self.tree = add_movie_action.triggered.connect(self.create_tree)
        file_menu.addAction(add_movie_action)

        fizzbuzz_action = QAction("FIZZBUZZ", self)
        fizzbuzz_action.triggered.connect(self.fizz_buzz)
        edit_menu.addAction(fizzbuzz_action)

    def create_clock(self):
        clock = QLabel("TIME:")
        clock.setAlignment(QtCore.Qt.AlignRight)
        self.grid.addWidget(clock, 1, 1)

    def create_tree(self):
        path = os.path.join(os.path.dirname(__file__), '..')
        self.tree = Add_Movie_Tree(path, self.pos())

    def fizz_buzz(self):
        for i in range(1, 101):
            if i % 3 == 0 and i % 5 == 0:
                print "FIZZBUZZ!"
            elif i % 3 == 0:
                print "FIZZ"
            elif i % 5 == 0:
                print "BUZZ"
            else:
                print i

class Add_Movie_Tree(QWidget):
    def __init__(self, path, frame):
        super(Add_Movie_Tree, self).__init__()
        self.path = path
        self.initUI()
    def initUI(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(self.path)
        tree = QTreeView()
        tree.setModel(self.model)
        tree.setRootIndex(self.model.index(self.path))
        layout = QGridLayout(self)
        layout.addWidget(tree)
        self.setLayout(layout)
        self.show()

if __name__ == "__main__":
    q_app = QApplication(sys.argv)
    q_window = Qt_window()
    sys.exit(q_app.exec_())