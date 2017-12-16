from Tkinter import *
import ttk

import hachoir_core
from hachoir_metadata import extractMetadata
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser

import time
import re
import os

#CLASSES================================================================================

class Add_Movie_Tree:

	def __init__(self, frame, path):
		metadata = read_metadata()
		top_level = Toplevel(frame) #create top level for new popup window
		add_movie_tree = ttk.Treeview(top_level, columns=("filepath", "filetype"), displaycolumns='') #create the movie tree and set "filepath" and "filetype" as values
		self.create_tree(add_movie_tree, path)
		add_movie_tree.bind("<Double-1>", lambda event, arg=top_level, frame=frame, metadata=metadata:  self.on_double_click(event, arg, frame, metadata)) #use the lambda function to pass an argument while binding

	def create_tree(self, tree, path):
		tree.pack(fill='both', expand=True)
		start_path = os.path.abspath(path) #make path absolute rather than relative
		root_node = tree.insert('', 'end', text=start_path, values=[start_path, "directory"], open=True) #insert the first node in the tree
		self.fill_tree(root_node, start_path, tree)

	def fill_tree(self, parent, path, tree):
		for loop_file in os.listdir(path):
			loop_file_path = os.path.join(path, loop_file) #concatenate 'path' and 'loop_file'
			loop_file_type = None
			if os.path.isdir(loop_file_path):
				loop_file_type = "directory"
			try:
				new_node = tree.insert(parent, 'end', text=loop_file, values=[loop_file_path, loop_file_type])
				if os.path.isdir(loop_file_path):
					self.fill_tree(new_node, loop_file_path, tree) #recurse if loop_file is a directory
			except UnboundLocalError:
				print "Unbound Local Error: node referenced before assignment"
			except UnicodeDecodeError:
				print "Could Not Read File: " + loop_file

	def on_double_click(self, event, top_level, frame, metadata):
		tree = event.widget #get the tree widget used in the double click event
		tree_node = tree.focus()
		tree_path = tree.set(tree_node, "filepath")
		if not os.path.isdir(tree_path):
			wfile = open("metadata.txt", "a")
			wfile.write(tree_path + "\n")
			wfile.close()
			top_level.destroy()
		update_labels(frame)

class Delete_Movie_Tree:

	def __init__(self, frame):
		rfile = open("metadata.txt", "r")
		read_metadata = rfile.readlines()
		rfile.close()
		top_level = Toplevel(frame)
		tree = ttk.Treeview(top_level, columns=("filepath"), displaycolumns='')
		for line in read_metadata:
			file_name = os.path.split(line)[1]
			tree.insert('', 'end', text=file_name, values=[line], open=False)
		tree.pack(fill='both', expand=True)
		tree.bind("<Double-1>", lambda event, arg=top_level, file_tree=tree, metadata=read_metadata, rframe=frame : self.on_double_click(event, arg, file_tree, metadata, rframe))

	def on_double_click(self, event, top_level, tree, metadata, frame):
		tree_item = tree.focus()
		tree_text = tree.set(tree_item, "filepath").strip()
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

#FUNCTIONS================================================================================

def clock_tick():
	current_time = "Time: " + time.strftime('%H:%M:%S %p') #get current time and format it with strftime
	current_clock = clock.cget("text") 	#get clock label text with cget
	if current_clock != current_time: #if clock label isn't the current time, update label
		clock.config(text=current_time)
	clock.after(200, clock_tick) #call self after 200 milliseconds

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

def on_label_selection(event):
	print "foo"

def add_movie(frame):
	path = os.path.join( os.path.dirname( __file__ ), '..' )
	tree = Add_Movie_Tree(frame, path)

def delete_movie():
	tree = Delete_Movie_Tree(frame)

#MAIN=====================================================================================

root = Tk()
root.geometry("700x400")
hachoir_core.config.quiet = True

if __name__ == "__main__":

	#Tkinter Window creation
	frame = Frame(root)
	frame.config(width=500, height=380, bg="grey")
	bottom_frame = Frame(root)
	bottom_frame.config(height=10, width=500, bg="yellow")
	side_frame=Frame(root)
	side_frame.config(width=20, bg="red")
	side_frame.lift(aboveThis=frame)

	#Tkinter Window Packing
	side_frame.pack(side=RIGHT, expand=False, fill="both")
	bottom_frame.pack(side=BOTTOM, expand=False, fill="x")
	frame.pack(side=LEFT, expand=True, fill="both")

	#working with movies
	make_labels(frame)
	metadata = read_metadata()

	for i in  range(0, len(metadata)):
		try:
			print metadata[i]["title"]
			print metadata[i]["resolution"]
			print metadata[i]["duration"]
			print metadata[i]["extension"] + "\n"
		except KeyError:
			print "KeyError: Not a Movie File"

	#ToolBar
	main_menu = Menu(frame) #create main menu
	file_menu = Menu(frame, tearoff=False) #tearoff false gets rid of dotted line at top of dropdown
	edit_menu = Menu(frame, tearoff=False)
	main_menu.add_cascade(label="File", menu=file_menu) #create file label
	file_menu.add_cascade(label="Add Movie", command=lambda : add_movie(frame)) #create label in file tab
	file_menu.add_cascade(label="Delete Movie", command=delete_movie)
	main_menu.add_cascade(label="Edit", menu=edit_menu)
	root.configure(menu=main_menu) #create menu

	#clock
	clock = Label(bottom_frame, text="") #create clock label
	clock.pack(side=LEFT)
	clock_tick()

root.mainloop()