from Add_Movie_Tree import *
from Delete_Movie_List import *
from password import passwd

from PyQt5.QtWidgets import *
from hachoir_metadata import extractMetadata
from hachoir_parser import createParser
import MySQLdb
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
        self.initialize_movie_table_from_db()
        self.show()

    def set_grid_layout(self, grid):
        grid.setRowStretch(0, 100)
        grid.setRowStretch(1, 1)
        self.main_window.setLayout(grid)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        self.create_add_movie_action(file_menu)
        self.create_delete_movie_action(file_menu)

        #placeholder action
        fizzbuzz_action = QAction("FIZZBUZZ", self)
        fizzbuzz_action.triggered.connect(fizz_buzz)
        edit_menu.addAction(fizzbuzz_action)

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
        Add_Movie_Tree(path, self.pos())
        self.movie_table.destroy()
        self.initialize_movie_table_from_db()

    def create_delete_movie_list(self):
        Delete_Movie_List(self)
        self.movie_table.destroy()
        self.initialize_movie_table_from_db()

    def retrieve_movies_from_db(self):
        db = MySQLdb.connect(host="localhost", user="root", passwd=passwd, db="movie_tracker")
        cur = db.cursor()
        cur.execute("SELECT * FROM movies")
        db.close()
        return cur

    def initialize_movie_table_from_db(self):
        cur = self.retrieve_movies_from_db()
        self.movie_table = self.create_movie_table(cur)
        self.fill_movie_table(self.movie_table, cur)
        self.grid.addWidget(self.movie_table, 0, 0)

    def create_movie_table(self, cur):
        movie_table = QTableWidget(self)
        self.set_movie_table_layout(movie_table, cur)
        self.set_movie_table_selection_behaviour(movie_table)
        return movie_table

    def set_movie_table_layout(self, movie_table, cur):
        movie_table.setColumnCount(4)
        movie_table.setRowCount(cur.rowcount)
        movie_table.setColumnWidth(0, 313)
        movie_table.setHorizontalHeaderLabels(["Title", "Duration", "Resolution", "File Type"])
        movie_table.verticalHeader().hide()
        movie_table.setShowGrid(False)
        return movie_table

    def set_movie_table_selection_behaviour(self, movie_table):
        movie_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        movie_table.setSelectionMode(QAbstractItemView.SingleSelection)
        movie_table.setEditTriggers(movie_table.NoEditTriggers)
        return movie_table

    def fill_movie_table(self, movie_table, cur):
        for index, mov in enumerate(cur.fetchall()):
            movie_table.setItem(index,0, QTableWidgetItem(mov[0]))
            movie_table.setItem(index,1, QTableWidgetItem(mov[1]))
            movie_table.setItem(index,2, QTableWidgetItem(mov[2]))
            movie_table.setItem(index,3, QTableWidgetItem(mov[3]))
        return movie_table

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

#placeholder function
def fizz_buzz():
    for i in range(1, 101):
        if i % 3 == 0 and i % 5 == 0:
            print "FIZZBUZZ!"
        elif i % 3 == 0:
            print "FIZZ"
        elif i % 5 == 0:
            print "BUZZ"
        else:
            print i

if __name__ == "__main__":
    q_app = QApplication(sys.argv)
    q_window = Qt_window()
    sys.exit(q_app.exec_())