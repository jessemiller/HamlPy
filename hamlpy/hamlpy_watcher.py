"""
Based on original haml-watcher.py by Christian Stefanescu (st.chris@gmail.com)

Watches a folder for files with the given extensions and calls the HamlPy compiler if the modified time has changed
since the last check.
"""

import argparse
import sys
import codecs
import os
import os.path
import time

from time import strftime

from hamlpy import HAML_EXTENSIONS
from hamlpy.compiler import Compiler


class Options(object):
    CHECK_INTERVAL = 3  # in seconds
    DEBUG = False  # print file paths when a file is compiled
    VERBOSE = False
    OUTPUT_EXT = '.html'


# dict of compiled files, fullpath => timestamp
compiled = dict()


class StoreNameValueTagPair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        tags = getattr(namespace, 'tags', {})
        for item in values:
            n, v = item.split(':')
            tags[n] = v

        setattr(namespace, 'tags', tags)


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-v', '--verbose', help='Display verbose output', action='store_true')
arg_parser.add_argument('-i', '--input-extension', metavar='EXT',
                        help='The file extensions to look for.', type=str, nargs='+')
arg_parser.add_argument('-ext', '--extension', metavar='EXT', default=Options.OUTPUT_EXT,
                        help='The output file extension. Default is .html', type=str)
arg_parser.add_argument('-r', '--refresh', metavar='S', default=Options.CHECK_INTERVAL, type=int,
                        help='Refresh interval for files. Default is %d seconds. Ignored if the --once flag is set.'
                             % Options.CHECK_INTERVAL)
arg_parser.add_argument('input_dir', help='Folder to watch', type=str)
arg_parser.add_argument('output_dir', help='Destination folder', type=str, nargs='?')
arg_parser.add_argument('--tag', type=str, nargs=1, action=StoreNameValueTagPair,
                        help='Add self closing tag. eg. --tag macro:endmacro')
arg_parser.add_argument('--attr-wrapper', dest='attr_wrapper', type=str, choices=('"', "'"), default="'",
                        action='store',
                        help="The character that should wrap element attributes. This defaults to ' (an apostrophe).")
arg_parser.add_argument('--django-inline', dest='django_inline', action='store_true',
                        help="Whether to support ={...} syntax for inline variables in addition to #{...}")
arg_parser.add_argument('--jinja', default=False, action='store_true',
                        help='Makes the necessary changes to be used with Jinja2.')
arg_parser.add_argument('--once', default=False, action='store_true',
                        help='Runs the compiler once and exits on completion. '
                             'Returns a non-zero exit code if there were any compile errors.')


def watch_folder():
    """Main entry point. Expects one or two arguments (the watch folder + optional destination folder)."""
    args = arg_parser.parse_args(sys.argv[1:])
    compiler_args = {}

    input_folder = os.path.realpath(args.input_dir)
    if not args.output_dir:
        output_folder = input_folder
    else:
        output_folder = os.path.realpath(args.output_dir)

    if args.verbose:
        Options.VERBOSE = True
        print("Watching {} at refresh interval {} seconds".format(input_folder, args.refresh))

    if args.extension:
        Options.OUTPUT_EXT = args.extension

    if getattr(args, 'tags', False):
        compiler_args['custom_self_closing_tags'] = args.tags

    if args.input_extension:
        input_extensions = [(e[1:] if e.startswith('.') else e) for e in args.input_extension]  # strip . chars
    else:
        input_extensions = HAML_EXTENSIONS

    if args.attr_wrapper:
        compiler_args['attr_wrapper'] = args.attr_wrapper

    if args.django_inline:
        compiler_args['django_inline_style'] = args.django_inline

    if args.jinja:
        compiler_args['tag_config'] = 'jinja2'

    # compile once, then exist
    if args.once:
        (total_files, num_failed) = _watch_folder(input_folder, input_extensions, output_folder, compiler_args)
        print('Compiled %d of %d files.' % (total_files - num_failed, total_files))
        if num_failed == 0:
            print('All files compiled successfully.')
        else:
            print('Some files have errors.')
        sys.exit(num_failed)

    while True:
        try:
            _watch_folder(input_folder, input_extensions, output_folder, compiler_args)
            time.sleep(args.refresh)
        except KeyboardInterrupt:
            # allow graceful exit (no stacktrace output)
            sys.exit(0)


def _watch_folder(folder, extensions, destination, compiler_args):
    """
    Compares "modified" timestamps against the "compiled" dict, calls compiler if necessary. Returns a tuple of the
    number of files hit and the number of failed compiles
    """
    total_files = 0
    num_failed = 0

    print('_watch_folder(%s, %s, %s)' % (folder, repr(extensions), destination))

    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            # ignore filenames starting with ".#" for Emacs compatibility
            if filename.startswith('.#'):
                continue

            if not _has_extension(filename, extensions):
                continue

            fullpath = os.path.join(dirpath, filename)
            subfolder = os.path.relpath(dirpath, folder)
            mtime = os.stat(fullpath).st_mtime

            # create subfolders in target directory if they don't exist
            compiled_folder = os.path.join(destination, subfolder)
            if not os.path.exists(compiled_folder):
                os.makedirs(compiled_folder)

            compiled_path = _compiled_path(compiled_folder, filename)
            if fullpath not in compiled or compiled[fullpath] < mtime or not os.path.isfile(compiled_path):
                compiled[fullpath] = mtime
                total_files += 1
                if not compile_file(fullpath, compiled_path, compiler_args):
                    num_failed += 1

    return total_files, num_failed


def _has_extension(filename, extensions):
    """
    Checks if the given filename has one of the given extensions
    """
    for ext in extensions:
        if filename.endswith('.' + ext):
            return True
    return False


def _compiled_path(destination, filename):
    return os.path.join(destination, filename[:filename.rfind('.')] + Options.OUTPUT_EXT)


def compile_file(fullpath, outfile_name, compiler_args):
    """
    Calls HamlPy compiler. Returns True if the file was compiled and written successfully.
    """
    if Options.VERBOSE:
        print('%s %s -> %s' % (strftime("%H:%M:%S"), fullpath, outfile_name))
    try:
        if Options.DEBUG:  # pragma: no cover
            print("Compiling %s -> %s" % (fullpath, outfile_name))
        haml = codecs.open(fullpath, 'r', encoding='utf-8').read()
        compiler = Compiler(compiler_args)
        output = compiler.process(haml)
        outfile = codecs.open(outfile_name, 'w', encoding='utf-8')
        outfile.write(output)

        return True
    except Exception as e:
        # import traceback
        print("Failed to compile %s -> %s\nReason:\n%s" % (fullpath, outfile_name, e))
        # print traceback.print_exc()

    return False


if __name__ == '__main__':  # pragma: no cover
    watch_folder()
