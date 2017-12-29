from Add_Movie_Tree import *
from Delete_Movie_List import *
from Movie_Table import *
from PyQt5.QtWidgets import QWidget, \
                            QMainWindow, \
                            QAction, \
                            QApplication
from Database_Functions import *
import os
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

if __name__ == "__main__":
    q_app = QApplication(sys.argv)
    q_window = Qt_window()
    sys.exit(q_app.exec_())