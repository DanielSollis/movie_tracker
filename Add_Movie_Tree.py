from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from movie_trackerQt import add_movie_to_database
import os

class Add_Movie_Tree(QDialog):
    def __init__(self, path, frame):
        super(Add_Movie_Tree, self).__init__()
        self.path = path
        self.tree = QTreeView()
        self.model = QFileSystemModel()
        self.initUI()

    def initUI(self):
        self.setGeometry(625, 375, 550, 350)
        self.create_tree()
        self.set_layout()

    def create_tree(self):
        self.model.setRootPath(self.path)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.path))
        self.tree.doubleClicked.connect(self.file_selected)
        self.tree.setColumnWidth(0, 200)

    def set_layout(self):
        layout = QGridLayout(self)
        layout.addWidget(self.tree)
        self.setLayout(layout)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def file_selected(self, index):
        selected_index = self.model.index(index.row(), 0, index.parent())
        file_path = self.model.filePath(selected_index)
        if os.path.isdir(file_path) is not True:
            add_movie_to_database(file_path)
            self.close()