from Add_Movie_Tree import *
from Delete_Movie_List import *
from Movie_Table import *
from PyQt5.QtWidgets import *
from hachoir_metadata import extractMetadata
from hachoir_parser import createParser
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
        self.movie_table = Movie_Table(self.grid)
        self.show()

    def set_grid_layout(self, grid):
        grid.setRowStretch(0, 100)
        grid.setRowStretch(1, 1)
        self.main_window.setLayout(grid)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        self.create_add_movie_action(file_menu)
        self.create_delete_movie_action(file_menu)

    def create_movie_table(self):
        movie_table = Movie_Table(self.grid)
        return movie_table

    def create_add_movie_action(self, file_menu):
        add_movie_action = QAction("Add Movie", self)
        add_movie_action.triggered.connect(self.create_add_movie_tree)
        file_menu.addAction(add_movie_action)


    def create_delete_movie_action(self, file_menu):
        delete_movie_action = QAction("Delete Movie", self)
        delete_movie_action.triggered.connect(self.create_delete_movie_list)
        file_menu.addAction(delete_movie_action)

    def create_add_movie_tree(self):
        path = os.path.join(os.path.dirname(__file__), '..')
        add_movie_tree = Add_Movie_Tree(path, self.pos())
        add_movie_tree.exec_()
        self.movie_table.destroy()
        self.create_movie_table()

    def create_delete_movie_list(self):
        delete_movie_list = Delete_Movie_List(self)
        delete_movie_list.exec_()
        self.movie_table.destroy()
        self.create_movie_table()

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
            metadata['width'] = re.search(r'width: (.*$)', lines).group(0)
            resolution_width = re.sub('pixels', "", re.search(r'\d.*', metadata_width).group(0)).strip()
        elif re.search(r'Image height:', lines) is not None:
            metadata_height = re.search(r'height: (.*$)', lines).group(0)
            metadata['height'] = metadata_height
            resolution_height = re.sub('pixels', "", re.search(r'\d.*', metadata_height).group(0)).strip()
    metadata['resolution'] = resolution_width + ' X ' + resolution_height
    metadata['title'] = os.path.basename(os.path.normpath(path)).replace("_", ' ').title().split(".")[0]
    metadata['extension'] = os.path.basename(os.path.normpath(path)).split(".")[1].strip("\n")
    metadata['path'] = path

    return metadata

if __name__ == "__main__":
    q_app = QApplication(sys.argv)
    q_window = Qt_window()
    sys.exit(q_app.exec_())