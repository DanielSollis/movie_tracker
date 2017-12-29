from Add_Movie_Tree import *
from Delete_Movie_List import *
from Movie_Table import *
from hachoir_metadata import extractMetadata
from hachoir_parser import createParser
import MySQLdb
import os
import re
import sys

class Qt_window(QMainWindow):
    def __init__(self):
        super(Qt_window, self).__init__()
        self.grid = QGridLayout()
        self.main_window = QWidget(self)
        self.movie_table = Movie_Table()
        self.initUI()

    def initUI(self):
        self.setCentralWidget(self.main_window)
        self.setGeometry(600, 300, 650, 450)
        self.setWindowTitle("Movie Tracker")
        self.set_grid_layout(self.grid)
        self.create_menu_bar()
        self.setup_movie_table()
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

    def setup_movie_table(self):
        self.movie_table.fill_movie_table(retrieve_movies_from_db())
        self.grid.addWidget(self.movie_table, 0, 0)

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
        self.movie_table.update_table_contents()

    def create_delete_movie_list(self):
        delete_movie_list = Delete_Movie_List(self)
        delete_movie_list.exec_()
        self.movie_table.update_table_contents()

def add_movie_to_database(file_path):
    metadata = get_metadata(file_path)
    if metadata['duration'] is not None and metadata['resolution'] is not None and metadata['extension'] is not None:
        db = MySQLdb.connect(host = "localhost", user = "root", passwd = passwd, db = "movie_tracker")
        cur = db.cursor()
        cur.execute("INSERT INTO movies (Title,Duration,Resolution,Extension,path) VALUES (%s,%s,%s,%s,%s);",
            (metadata['title'], metadata['duration'], metadata['resolution'], metadata['extension'], metadata['path']))
        db.commit()
        db.close()
    else:
        print "foo"

def retrieve_movies_from_db():
    db = MySQLdb.connect(host="localhost", user="root", passwd=passwd, db="movie_tracker")
    cur = db.cursor()
    cur.execute("SELECT * FROM movies")
    db.close()
    return cur

def get_metadata(path):
    parser = createParser(path)
    extract_metadata = extractMetadata(parser)
    metadata_text = str(extract_metadata).split("\n")
    metadata = {}
    metadata['duration'] = get_metadata_duration(metadata_text)
    metadata['resolution'] = get_metadata_resolution(metadata_text)
    metadata['title'] = os.path.basename(os.path.normpath(path)).replace("_", ' ').title().split(".")[0]
    metadata['extension'] = os.path.basename(os.path.normpath(path)).split(".")[1].strip("\n")
    metadata['path'] = path

    return metadata

def get_metadata_duration(metadata_text):
    for line in metadata_text:
        if re.search(r'Duration:', line) is not None:
            duration = re.search(r'Duration: (.*$)', line).group(0)
            duration = re.sub(r' hours? ', ':', duration)
            duration = re.sub(r' min ', ':', duration).strip(' sec')
            return re.sub("Duration: ", "", duration)
    return None

def get_metadata_resolution(metadata_text):
    resolution_width = None
    resolution_height = None
    for line in metadata_text:
        if re.search(r'Image width:', line) is not None:
            metadata_width = re.search(r'width: (.*$)', line).group(0)
            resolution_width = re.sub('pixels', "", re.search(r'\d.*', metadata_width).group(0)).strip()
        elif re.search(r'Image height:', line) is not None:
            metadata_height = re.search(r'height: (.*$)', line).group(0)
            resolution_height = re.sub('pixels', "", re.search(r'\d.*', metadata_height).group(0)).strip()
    if resolution_width is not None and resolution_height is not None:
        return resolution_width + ' X ' + resolution_height
    return None

if __name__ == "__main__":
    q_app = QApplication(sys.argv)
    q_window = Qt_window()
    sys.exit(q_app.exec_())