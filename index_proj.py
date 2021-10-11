#TODO: Clean Up Code. Delete duplicate functions
# - Restructure Code. Move functions into Class structure
# - Switch Index from dict to list for now
#       - can abstract Index and make alternate implementations later
# - make index human readable (json/csv)
# - Define file constants for things like default index filename (for modifiability)
# - implement reverse index for faster search


import os
import pickle
import click
from os.path import normpath, join, realpath

class FileRecord():
    def __init__(
    self,
    fullpath=None,
    basename=None,
    size=None,
    type=None
    ):
        self.fullpath = fullpath
        self.basename = basename
        self.size = size
        self.type = type
        return

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str((self.fullpath, self.basename, self.size, self.type))

    def generate_info(self):
        """Update the record with file info"""
        #TODO: Protect against calling this with invalid path
        self.basename = os.path.basename(self.fullpath)
        self.size = os.path.getsize(self.fullpath)
        self.type = os.path.splitext(self.fullpath)[1]
        return self.basename, self.size, self.type

    def matches(self, query):
        #TODO figure out where this belongs
        if (query.basename is None) or (query.basename == self.basename):
            if (query.size is None) or (query.size == self.size):
                if (query.type is None) or (query.type == self.type):
                    return True
        return False


class Index():
    def __init__(self, map=None):
        self.map = map if map is not None else {}

    def __str__(self):
        return self.map.__str__()

    def add(self, record: FileRecord) -> None:
        self.map[record.fullpath] = record
        return




def get_dir_files(top):
    """Generates absolutized normalized paths of all files in directory tree"""
    filepaths = []
    for dirpath, subdirs, filenames in os.walk(top):
        for file in filenames:
            filepaths.append(realpath(join(dirpath, file)))
    return filepaths

def get_file_info(path):
    """Returns the basename, size, and type of a file"""
    basename = os.path.basename(path)
    size = os.path.getsize(path)
    type = os.path.splitext(path)[1]
    return basename, size, type

def get_matches(index: Index, basename, size, type):
    #Next step: migrate to be a method of Index.
    #Separate out the comparison logic to FileRecord class. Implement FileRecord.matches(record)
    match_list = []
    for record in index.map.values():
        if (basename is None) or (basename == record.basename):
            if (size is None) or (size == record.size):
                if (type is None) or (type == record.type):
                    match_list.append(record)
    return match_list

def to_file(index, filename):
    with open(filename, 'wb') as f:
        pickle.dump(index, f)
    return

def from_file(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


@click.group()
def index():
    """Use to traverse a base directory and create an index file that can be used to quickly lookup files by name, size, and content type"""
    pass

@index.command()
@click.option('--dir', type=click.Path(), help='The path of the directory to index. Defaults to current directory')
@click.option('--out', default='index.idx', type=click.File('wb'), help='The file name of the created index. Defaults to index.idx')
def create(dir, out):
    """Generates an index of all files in the directory tree"""
    if dir is None: dir = os.getcwd()
    file_table = Index()
    for path in get_dir_files(dir):
        record = FileRecord(path)
        record.generate_info()
        file_table.add(record)
    pickle.dump(file_table, out)

@index.command()
@click.argument('source', default='index.idx', type=click.File('rb'), required=False)
@click.option('--name', type=str, help='Finds only files with this name (Example: "file.txt")')
@click.option('--size', type=int, help='Finds only files with this size (Example: 1532)')
@click.option('--type', type=str, help='Finds only files with this extension (Example: ".png")')
@click.option('--out', type=click.File('w'), default='-', help='Writes the output to this file. Defaults to stdout')
def search(source, name, size, type, out):
    """Returns paths to the files in the directory tree which match all parameters. If no parameters are given, it finds all files. Requires an index file [SOURCE], which defaults to "index.idx"."""
    file_table = pickle.load(source)
    #click.echo(file_table)
    for record in get_matches(file_table, name, size, type):
        click.echo(record.fullpath, file=out)
