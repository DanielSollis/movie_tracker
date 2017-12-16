from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGridLayout, QMainWindow, QAction, \
    QTreeView, QFileSystemModel
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer

from hachoir_metadata import extractMetadata
from hachoir_parser import createParser

import time
import re
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
        self.setCentralWidget(self.main_window)
        self.setGeometry(600, 300, 650, 450)
        self.setWindowTitle("Movie Tracker")
        self.set_grid_layout(self.grid)
        self.create_menu_bar()
        self.create_clock()
        self.show()

    def set_grid_layout(self, grid):
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

    # def create_clock(self):
    #     clock = QLabel()
    #     clock.setText("Time:")
    #     clock.setAlignment(QtCore.Qt.AlignRight)
    #     self.grid.addWidget(clock, 1, 1)
    #     timer = QTimer()
    #     timer.timeout.connect(self.clock_tick(clock))
    #     timer.start(1000)

    def clock_tick(self, clock):
        current_time = "Time: " + time.strftime('%H:%M:%S %p')
        current_clock = clock.text()
        if current_clock != current_time:
            clock.setText(current_time)

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
        self.tree = QTreeView()
        self.initUI()

    def initUI(self):
        self.setGeometry(625, 375, 550, 350)
        self.create_tree()
        self.set_layout()

    def create_tree(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(self.path)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.path))
        self.tree.doubleClicked.connect(self.file_selected)

    def set_layout(self):
        layout = QGridLayout(self)
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.show()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def file_selected(self, index):
        selected_index = self.model.index(index.row(), 0, index.parent())
        file_name = self.model.fileName(selected_index)
        file_path = self.model.filePath(selected_index)
        if (os.path.isdir(file_path) is not True):
            metadata = get_metadata(file_path)
            print metadata

def get_metadata(path):
    parser = createParser(path)
    extract_metadata = extractMetadata(parser)
    metadata_text = str(extract_metadata).split("\n")
    resolution_height = ""
    resolution_width = ""
    metadata = {}
    for lines in metadata_text:
        if re.search(r'Duration:', lines) is not None:
            metadata_duration = re.search(r'Duration: (.*$)', lines).group(0)
            metadata_duration = re.sub(r' hours? ', ':', metadata_duration)
            metadata_duration = re.sub(r' min ', ':', metadata_duration).strip(' sec')
            metadata['duration'] = re.sub("Duration: ", "", metadata_duration)
        elif re.search(r'Image width:', lines) is not None:
            metadata_width = re.search(r'width: (.*$)', lines).group(0)
            metadata['width'] = metadata_width
            resolution_width = re.sub('pixels', "", re.search(r'\d.*', metadata_width).group(0)).strip()
        elif re.search(r'Image height:', lines) is not None:
            metadata_height = re.search(r'height: (.*$)', lines).group(0)
            metadata['height'] = metadata_height
            resolution_height = re.sub('pixels', "", re.search(r'\d.*', metadata_height).group(0)).strip()
    metadata['resolution'] = resolution_width + ' X ' + resolution_height
    metadata['title'] = os.path.basename(os.path.normpath(path)).replace("_", ' ').title().split(".")[0]
    metadata['extension'] = os.path.basename(os.path.normpath(path)).split(".")[1].strip("\n")

    return metadata

if __name__ == "__main__":
    q_app = QApplication(sys.argv)
    q_window = Qt_window()
    sys.exit(q_app.exec_())