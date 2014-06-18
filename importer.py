import os

def list_files(directory):

	file_list = []
	for file in os.listdir(directory):
		dirfile = os.path.join(directory, file)
		if os.path.isfile(dirfile):
			print file
			file_list.append(dirfile)

list_files("./xls")