# haml-watcher.py
# Author: Christian Stefanescu (st.chris@gmail.com)
#
# Watch a folder for files with the given extensions and call the HamlPy
# compiler if the modified time has changed since the last check.
from time import gmtime, strftime
import sys
import codecs
import os
import os.path
import time
from hamlpy import Compiler

EXTENSIONS = ['.haml', '.hamlpy']    # watched extensions
CHECK_INTERVAL = 3          # in seconds
DEBUG = False               # print file paths when a file is compiled

# dict of compiled files [fullpath : timestamp]
compiled = dict()

def watched_extension(extension):
    """Return True if the given extension is one of the watched extensions"""
    for ext in EXTENSIONS:
        if extension.endswith(ext):
            return True
    return False

def watch_folder():
    """Main entry point. Expects one or two arguments (the watch folder + optional destination folder)."""
    argv_len = len(sys.argv)
    if argv_len in (2, 3):
        folder = os.path.realpath(sys.argv[1])
        destination = os.path.realpath(argv_len == 3 and os.path.realpath(sys.argv[2]) or folder)
        
        print "Watching %s at refresh interval %s seconds" % (folder,CHECK_INTERVAL)
        while True:
            try:
                _watch_folder(folder, destination)
                time.sleep(CHECK_INTERVAL)
            except KeyboardInterrupt:
                # allow graceful exit (no stacktrace output)
                sys.exit(0)
                pass
    else:
        print "Usage: hamlpy-watcher.py <watch_folder> [destination_folder]"

def _watch_folder(folder, destination):
    """Compares "modified" timestamps against the "compiled" dict, calls compiler
    if necessary."""
    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            # Ignore filenames starting with ".#" for Emacs compatibility
            if watched_extension(filename) and not filename.startswith('.#'):
                fullpath = os.path.join(dirpath, filename)
                subfolder = os.path.relpath(dirpath, folder)
                mtime = os.stat(fullpath).st_mtime
				
                # Create subfolders in target directory if they don't exist
                compiled_folder = os.path.join(destination, subfolder)
                if not os.path.exists(compiled_folder):
                    os.makedirs(compiled_folder)
				
                compiled_path = _compiled_path(compiled_folder, filename)
                if (not fullpath in compiled or
                    compiled[fullpath] < mtime or
                    not os.path.isfile(compiled_path)):
                    compile_file(fullpath, compiled_path)
                    compiled[fullpath] = mtime

def _compiled_path(destination, filename):
    return os.path.join(destination, filename[:filename.rfind('.')] + '.html')

def compile_file(fullpath, outfile_name):
    """Calls HamlPy compiler."""
    print '%s %s -> %s' % ( strftime("%H:%M:%S", gmtime()), fullpath, outfile_name )
    try:
        if DEBUG:
            print "Compiling %s -> %s" % (fullpath, outfile_name)
        haml_lines = codecs.open(fullpath, 'r', encoding='utf-8').read().splitlines()
        compiler = Compiler()
        output = compiler.process_lines(haml_lines)
        outfile = codecs.open(outfile_name, 'w', encoding='utf-8')
        outfile.write(output)
    except Exception, e:
        # import traceback
        print "Failed to compile %s -> %s\nReason:\n%s" % (fullpath, outfile_name, e)
        # print traceback.print_exc()

if __name__ == '__main__':
    watch_folder()
