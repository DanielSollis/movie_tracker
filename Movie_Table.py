from PyQt5.QtWidgets import QWidget, \
                            QTableWidget, \
                            QAbstractItemView, \
                            QTableWidgetItem
from password import passwd
import MySQLdb

class Movie_Table(QWidget):
    def __init__(self, grid):
        super(Movie_Table, self).__init__()
        cur = self.retrieve_movies_from_db()
        self.movie_table = self.create_movie_table(cur)
        self.fill_movie_table(self.movie_table, cur)
        grid.addWidget(self.movie_table, 0, 0)

    def create_movie_table(self, cur):
        movie_table = QTableWidget()
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

    def retrieve_movies_from_db(self):
        db = MySQLdb.connect(host="localhost", user="root", passwd=passwd, db="movie_tracker")
        cur = db.cursor()
        cur.execute("SELECT * FROM movies")
        db.close()
        return cur
