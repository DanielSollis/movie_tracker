from hachoir_metadata import extractMetadata
from hachoir_parser import createParser
from password import passwd
from PyQt5.QtWidgets import QMessageBox
import MySQLdb
import os
import re

def add_movie_to_database(file_path):
    metadata = get_metadata(file_path)
    if metadata['duration'] is not None and metadata['resolution'] is not None and metadata['extension'] is not None:
        add_confirmed_movie(metadata)
        return True
    else:
        alert_file_not_video()
        return False

def add_confirmed_movie(metadata):
    db = MySQLdb.connect(host="localhost", user="root", passwd=passwd, db="movie_tracker")
    cur = db.cursor()
    cur.execute("INSERT INTO movies (Title,Duration,Resolution,Extension,path) VALUES (%s,%s,%s,%s,%s);",
                (metadata['title'], metadata['duration'], metadata['resolution'], metadata['extension'],
                 metadata['path']))
    db.commit()
    db.close()

def alert_file_not_video():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Selected file not movie")
    msg.setWindowTitle("Not a Movie!")
    msg.exec_()

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