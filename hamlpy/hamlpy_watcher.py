# haml-watcher.py
# Author: Christian Stefanescu (st.chris@gmail.com)
#
# Watch a folder for files with the given extensions and call the HamlPy
# compiler if the modified time has changed since the last check.
from time import gmtime, strftime
import argparse
import sys
import codecs
import os
import os.path
import time
import hamlpy

try:
    str = unicode
except NameError:
    pass

class Options(object):
    CHECK_INTERVAL = 3  # in seconds
    DEBUG = False  # print file paths when a file is compiled
    VERBOSE = False
    OUTPUT_EXT = '.html'

# dict of compiled files [fullpath : timestamp]
compiled = dict()


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-v', '--verbose', help = 'Display verbose output', action = 'store_true')
arg_parser.add_argument('-i', '--input-extension', metavar = 'EXT', default = '.hamlpy', help = 'The file extensions to look for', type = str, nargs = '+')
arg_parser.add_argument('-ext', '--extension', metavar = 'EXT', default = Options.OUTPUT_EXT, help = 'The output file extension. Default is .html', type = str)
arg_parser.add_argument('-r', '--refresh', metavar = 'S', default = Options.CHECK_INTERVAL, help = 'Refresh interval for files. Default is {} seconds'.format(Options.CHECK_INTERVAL), type = int)
arg_parser.add_argument('input_dir', help = 'Folder to watch', type = str)
arg_parser.add_argument('output_dir', help = 'Destination folder', type = str, nargs = '?')

def watched_extension(extension):
    """Return True if the given extension is one of the watched extensions"""
    for ext in hamlpy.VALID_EXTENSIONS:
        if extension.endswith('.' + ext):
            return True
    return False

def watch_folder():
    """Main entry point. Expects one or two arguments (the watch folder + optional destination folder)."""
    argv = sys.argv[1:] if len(sys.argv) > 1 else []
    args = arg_parser.parse_args(sys.argv[1:])
    
    input_folder = os.path.realpath(args.input_dir)
    if not args.output_dir:
        output_folder = input_folder
    else:
        output_folder = os.path.realpath(args.output_dir)
    
    if args.verbose:
        Options.VERBOSE = True
        print "Watching {} at refresh interval {} seconds".format(input_folder, args.refresh)
    
    if args.extension:
        Options.OUTPUT_EXT = args.extension
        
    
    if args.input_extension:
        hamlpy.VALID_EXTENSIONS += args.input_extension
    
    while True:
        try:
            _watch_folder(input_folder, output_folder)
            time.sleep(args.refresh)
        except KeyboardInterrupt:
            # allow graceful exit (no stacktrace output)
            sys.exit(0)

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
    return os.path.join(destination, filename[:filename.rfind('.')] + Options.OUTPUT_EXT)

def compile_file(fullpath, outfile_name):
    """Calls HamlPy compiler."""
    if Options.VERBOSE:
        print '%s %s -> %s' % (strftime("%H:%M:%S", gmtime()), fullpath, outfile_name)
    try:
        if Options.DEBUG:
            print "Compiling %s -> %s" % (fullpath, outfile_name)
        haml_lines = codecs.open(fullpath, 'r', encoding = 'utf-8').read().splitlines()
        compiler = hamlpy.Compiler()
        output = compiler.process_lines(haml_lines)
        outfile = codecs.open(outfile_name, 'w', encoding = 'utf-8')
        outfile.write(output)
    except Exception, e:
        # import traceback
        print "Failed to compile %s -> %s\nReason:\n%s" % (fullpath, outfile_name, e)
        # print traceback.print_exc()

if __name__ == '__main__':
    watch_folder()
