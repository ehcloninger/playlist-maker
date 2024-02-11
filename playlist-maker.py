import os
import sys
import argparse

def process_dir(dir, recurse, case, types):
    my_list = []

    for root, subFolders, files in os.walk(dir):
        for file in files:
            file_path = os.path.splitext(file)
            if (len(file_path) > 1):
                ext = file_path[1]
                if (case):
                    ext = ext.lower()
                if (ext in types):
                    my_list.append(dir + os.sep + file)

        if (recurse):
            for folder in subFolders:
                new_list = process_dir(dir + os.sep + folder, recurse, case, types)
                for new_file in new_list:
                    my_list.append(new_file)

        return my_list
    
def process(args):
    
    music_files = []
    for dir in args.input_dirs:
        dir_files = process_dir(dir, args.recurse, args.case, args.type);
        for file in dir_files:
            music_files.append(file)
    

    return music_files

def outputPlayList(my_list, args):
    output_file = sys.stdout
    if (args.output is None):
        output_file = sys.stdout
    else:
        try:
            output_file = open(args.output, "w", encoding="utf-8")
        except:
            print("Could not open " + args.output + " for output.", file=sys.stderr)
            return -1

    if (output_file is None): 
        return -1

    output_file.write("#EXTM3U\n")

    for file in my_list:
        parts = os.path.split(file)
        play_time = 0 # TODO: Calculate this from metadata
        song_title = parts[len(parts) - 1]
        parts = os.path.splitext(song_title)
        song_title = parts[0]

        output_file.write("#EXTINF:%d,%s\n" % (play_time, song_title))
        output_file.write("%s\n" % (file))

    output_file.close()

    return 0

# Initialize parser
parser = argparse.ArgumentParser(prog="playlist-maker", description="Create a playlist from a directory of music files.")
parser.add_argument("-R", "--recurse", action="store_true", help="Recurse source directory")
parser.add_argument("-F", "--fullpath", action="store_true", help="Use full path when working from current dir")
parser.add_argument("-c", "--case", action="store_true", help="Enforce case of input files [default=OFF]")
parser.add_argument("-t", "--type", nargs=1, action='append', help="Extension to include [.mp3,.wav,.flac,.aiff]")
parser.add_argument("-o", "--output", help="Name of output file [STDOUT]")
parser.add_argument("-f", "--format", help="Format of output file [.m3u8]", choices=[".m3u8"])
parser.add_argument("input_dirs", nargs="*", action='extend', help="Uses current directory by default")
parser.add_argument("-S", "--sortlist", action="store_true", help="Sort output list alphabetically")

try:
    args = parser.parse_args()
except:
    pass

# After parsing, do some stuff with the args
if (args is None):
    sys.exit(-1)

# If no input path, use current directory. Here, it can be full path or partial
if (len(args.input_dirs) == 0):
    if (args.fullpath):
        args.input_dirs.append(os.getcwd())
    else:
        args.input_dirs.append(".")

# If no file types are specified on the command line, choose these defaults
if (args.type is None):
    args.type = []
    args.type.append(".mp3")
    args.type.append(".wav")
    args.type.append(".aiff")
    args.type.append(".flac")

# If case insensitive, set the default compare to lower case
new_exts = []
if (args.case):
    for ext in args.type:
        new_exts.append(ext[0].lower())
    args.type = new_exts

# Process the directories and store the file names in a list
my_list = process(args)
if (my_list is None):
    sys.exit(-1)

# Sort the output if necessary
if (args.sortlist):
    my_list.sort()

ret_val = outputPlayList(my_list, args)
sys.exit(0) 
