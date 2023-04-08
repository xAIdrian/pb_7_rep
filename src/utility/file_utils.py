import sys
import os
sys.path.append("../src")

def get_file_name_from_video_path( file_path ):
    # Split the path into a list of directories and the file name
    directories = file_path.split('/')
    file_name = None

    # Traverse the directories list backwards to find the last .mp4 file
    for directory in reversed(directories):
        if directory.endswith('.mp4'):
            file_name = directory
            break

    # Check if a .mp4 file was found
    if file_name is None:
        print("There is no .mp4 file in the path.")
        return ''
    else:
        print("The last .mp4 file name is:", file_name)
        return file_name