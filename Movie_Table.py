from PyQt5.QtWidgets import QTableWidget, \
                            QAbstractItemView, \
                            QTableWidgetItem
import movie_trackerQt

class Movie_Table(QTableWidget):
    def __init__(self):
        super(Movie_Table, self).__init__()
        cur = movie_trackerQt.retrieve_movies_from_db()
        self.set_layout(cur)
        self.set_selection_behavior()
        self.setAcceptDrops(True)

    def set_layout(self, cur):
        self.setColumnCount(4)
        self.setRowCount(cur.rowcount)
        self.setColumnWidth(0, 313)
        self.setHorizontalHeaderLabels(["Title", "Duration", "Resolution", "File Type"])
        self.verticalHeader().hide()
        self.setShowGrid(False)

    def set_selection_behavior(self):
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(self.NoEditTriggers)

    def fill_movie_table(self, cur):
        for index, mov in enumerate(cur.fetchall()):
            self.setItem(index,0, QTableWidgetItem(mov[0]))
            self.setItem(index,1, QTableWidgetItem(mov[1]))
            self.setItem(index,2, QTableWidgetItem(mov[2]))
            self.setItem(index,3, QTableWidgetItem(mov[3]))

    def update_table_contents(self):
        for row in reversed(range(self.rowCount())):
            self.removeRow(row)
        cur = movie_trackerQt.retrieve_movies_from_db()
        self.setRowCount(cur.rowcount)
        self.fill_movie_table(cur)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()

    def dragMoveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        for file in e.mimeData().urls():
            path = file.toLocalFile()
            movie_trackerQt.add_movie_to_database(path)
            self.update_table_contents()