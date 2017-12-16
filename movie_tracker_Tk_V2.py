from Tkinter import *
import ttk

import hachoir_core
from hachoir_metadata import extractMetadata
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser

import time
import os

class Movie_Tree:
   def  __init__(self, frame, path):


            self.path = path
            self.metadata = read_metadata()
            self.tree_frame = Toplevel(frame)
            self.add_movie_tree = ttk.Treeview(self.tree_frame, columns=("filepath", "filetype"), displaycolumns='')
            self.create_add_tree()
            self.add_movie_tree.bind("<Double-1>", lambda event, fr=frame :  self.add_on_double_click(event, fr))
            self.add_movie_tree.bind("<<TreeviewOpen>>", lambda event, fr=frame : self.add_on_double_click(event, fr))

   def create_add_tree(self):
        add_movie_tree = self.add_movie_tree
        add_movie_tree.pack(fill="both", expand=True)
        start_path = os.path.abspath(self.path)  # make path absolute rather than relative
        root_node = add_movie_tree.insert('', 'end', text=start_path, values=[start_path, "directory"], open=True)  # insert the first node in the tree
        self.fill_add_tree(root_node, self.path, add_movie_tree)

   def fill_add_tree(self, parent, path, tree):
        for loop_file in os.listdir(path):
            loop_file_path = os.path.join(path, loop_file)  # concatenate 'path' and 'loop_file'
            loop_file_type = None
            if os.path.isdir(loop_file_path):
                loop_file_type = "directory"
            try:
                new_node = tree.insert(parent, 'end', text=loop_file, values=[loop_file_path, loop_file_type])
                if os.path.isdir(loop_file_path):
                    tree.insert(new_node, 'end', text='', values=['', loop_file_type])
            except UnboundLocalError:
                print "Unbound Local Error: node referenced before assignment"
            except UnicodeDecodeError:
                print "Could Not Read File: " + loop_file

   def add_on_double_click(self, event, frame):
        tree = event.widget  # get the tree widget used in the double click event
        tree_node = tree.focus()
        tree_path = tree.set(tree_node, "filepath")
        if os.path.isdir(tree_path):
            children = self.add_movie_tree.get_children(tree_node)
            if len(children) == 1:
                self.add_movie_tree.delete(children)
                self.fill_add_tree(tree_node, tree_path, self.add_movie_tree)
        if not os.path.isdir(tree_path):
            wfile = open("metadata.txt", "a")
            wfile.write(tree_path + "\n")
            wfile.close()
            self.tree_frame.destroy()
            update_labels(frame)

def clock_tick():
    current_time = "Time: " + time.strftime("%H:%M:%S:%p")
    current_clock = clock.cget("text")
    if current_time != current_clock:
        clock.config(text=current_time)
    clock.after(200, clock_tick)

def get_metadata(path):
    unicode_name = unicodeFilename(path.strip("\n"))
    parser = createParser(unicode_name)
    extract_metadata = extractMetadata(parser)
    metadata_text = str(extract_metadata).split("\n")
    resolution_height = ""
    resolution_width = ""
    metadata = {}
    for lines in metadata_text:
        if re.search(r'Duration:', lines) is not None: #if search of line contains 'Duration:'
            metadata_duration = re.search(r'Duration: (.*$)', lines).group(0) #retrieve line
            metadata_duration = re.sub(r' hours? ', ':', metadata_duration) #sub out 'hours' with ':'
            metadata_duration = re.sub(r' min ', ':', metadata_duration).strip(' sec') #sub out 'min' with ':' and remove 'sec'
            metadata['duration'] = re.sub("Duration: ", "", metadata_duration)

        elif re.search(r'Image width:', lines) is not None: #retrieve width
            metadata_width = re.search(r'width: (.*$)', lines).group(0)
            metadata['width'] = metadata_width
            resolution_width = re.sub('pixels', "", re.search(r'\d.*', metadata_width).group(0)).strip() #set width, strip whitespace at ends

        elif re.search(r'Image height:', lines) is not None: #retrieve height
            metadata_height = re.search(r'height: (.*$)', lines).group(0)
            metadata['height'] = metadata_height
            resolution_height = re.sub('pixels', "", re.search(r'\d.*', metadata_height).group(0)).strip() #set height

    metadata['resolution'] = resolution_width + ' X ' + resolution_height #set resolution as width X height
    metadata['title'] = os.path.basename(os.path.normpath(path)).replace("_", ' ').title().split(".")[0] #remove file extension and underscores from title and upper case first letters
    metadata['extension'] = os.path.basename(os.path.normpath(path)).split(".")[1].strip("\n")
    return metadata

def read_metadata():
    metadata = []
    read_metadata = open("metadata.txt")  # read metadata
    metadata_text = read_metadata.readlines()
    for lines in metadata_text:
        try:
            metadata.append(get_metadata(lines)) #retrieve metadata
        except UnboundLocalError: #catch if file not video
            print "File Error: hachoir could not parse file" + os.path.basename(os.path.normpath(lines))
        except hachoir_core.stream.input.InputStreamError:
            print "Error: Line Break in metadata.txt"
    return metadata

def make_labels(frame):
    data = read_metadata()
    movieList = Listbox(frame, bd=0)
    if data is not None:
        for index, metadata in enumerate(data):
            movieList.insert(index, metadata["title"])
    movieList.grid()

def update_labels(frame):
    data = read_metadata()
    list_of_widgets = frame.winfo_children()
    movieList = None
    for wid in list_of_widgets:
        if wid.winfo_class() == "Listbox":
            movieList = wid
    movieList.delete(0, END)
    for index, metadata in enumerate(data):
        movieList.insert(index, metadata["title"])

def delete_list(frame):
    rfile = open("metadata.txt", "r")
    metadata = rfile.readlines()
    rfile.close()
    top_level = Toplevel(frame)
    deleteList = Listbox(top_level, bd=0)
    for index, line in enumerate (metadata):
        file_name = os.path.split(line)[1]
        deleteList.insert(index, line)
    deleteList.pack(fill='both', expand=True)
    #deleteList.bind("<Double-1>",
                    #lambda event, tl=top_level, dl=deleteList, md=metadata, fr=frame : delete_on_double_click(event, tl, dl, md,fr))

def delete_on_double_click(self, event, top_level, list, metadata, frame):
       list = list.focus()
       list_text = list.set(list_item, "filepath").strip()
       for index, line, in enumerate(metadata):
           check_line = line.strip("\n")
           if check_line == tree_text:
               del metadata[index]
       wfile = open("metadata.txt", "w")
       for line in metadata:
           wfile.write(line)
       wfile.close()
       top_level.destroy()
       update_labels(frame)

def make_tree(frame):
    path = os.path.join(os.path.dirname(__file__), '..')
    tree = Movie_Tree(frame, path) #add_movie_tree

root = Tk()
root.geometry("700x400")
hachoir_core.config.quit = True

if __name__ == "__main__":
    main_frame = Frame(root)
    main_frame.config(width=500, height=380, bg="grey")
    bottom_frame = Frame(root)
    bottom_frame.config(height=20, bg="red")
    side_frame = Frame(root)
    side_frame.config(width=50, bg="yellow")

    side_frame.pack(side=RIGHT, expand=False, fill="both")
    bottom_frame.pack(side=BOTTOM, expand=False, fill="x")
    main_frame.pack(side=LEFT, expand=True, fill="both")

    main_menu = Menu(main_frame)
    file_menu = Menu(main_frame, tearoff=False)
    main_menu.add_cascade(menu=file_menu, label="File")
    file_menu.add_command(label="Add Movie", command=lambda add=True, frame=main_frame : make_tree(frame))
    file_menu.add_command(label="Delete Movie", command=lambda add=False, frame=main_frame : delete_list(frame))
    root.config(menu=main_menu)

    clock = Label(bottom_frame, text="")
    clock.pack(side=LEFT)
    clock_tick()

    make_labels(main_frame)
root.mainloop()