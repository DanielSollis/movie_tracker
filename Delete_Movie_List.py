from PyQt5.QtWidgets import QDialog, \
                            QListWidget, \
                            QGridLayout
import MySQLdb
from password import passwd

class Delete_Movie_List(QDialog):
    def __init__(self, frame):
        super(Delete_Movie_List, self).__init__()
        self.movie_list = QListWidget()
        self.fill_movie_list_from_db()
        self.movie_list.doubleClicked.connect(lambda: self.file_selected())
        self.setup_layout()

    def fill_movie_list_from_db(self):
        db = MySQLdb.connect(host="localhost", user="root", passwd=passwd, db="movie_tracker")
        cur = db.cursor()
        cur.execute("SELECT * FROM movies")
        for index, mov in enumerate(cur.fetchall()):
            self.movie_list.insertItem(index, mov[0])
        db.close()

    def setup_layout(self):
        self.setGeometry(625, 375, 200, 250)
        layout = QGridLayout(self)
        layout.addWidget(self.movie_list)
        self.setLayout(layout)

    def file_selected(self):
        db = MySQLdb.connect(host="localhost", user="root", passwd=passwd, db="movie_tracker")
        selected_item = self.movie_list.currentItem().text()
        cur = db.cursor()
        cur.execute("DELETE FROM movies WHERE Title = '%s';" % selected_item)
        db.commit()
        db.close()
        self.close()