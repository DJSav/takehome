#TODO: Clean Up Code. Delete duplicate functions
# - Restructure Code. Move functions into Class structure
# - Switch Index from dict to list for now
#       - can abstract Index and make alternate implementations later

# - Define file constants for things like default index filename (for modifiability)

# Possible Features:
# - make index human readable (json/csv)
# - implement reverse index for faster search
# - support regex expressions


import os
import pickle
import click

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
        return repr((self.fullpath, self.basename, self.size, self.type))

    def generate_info(self):
        """Update the record with file info"""
        #TODO: Protect against calling this with invalid path
        self.basename = os.path.basename(self.fullpath)
        self.size = os.path.getsize(self.fullpath)
        self.type = os.path.splitext(self.fullpath)[1]
        return self.basename, self.size, self.type

    def matches(self, query) -> bool:
        #TODO figure out where this belongs
        if (query.basename is None) or (query.basename == self.basename):
            if (query.size is None) or (query.size == self.size):
                if (query.type is None) or (query.type == self.type):
                    return True
        return False

class Index():
    def __init__(self, table=None, root='.'):
        self.table = table if table is not None else []
        self.root = root
    def __str__(self):
        return "{" + str(self.root) + ", " + str(self.table) + "}"

    def add(self, record: FileRecord) -> None:
        self.table.append(record)
        return



def get_dir_files(top):
    """Generates absolutized normalized paths of all files in directory tree"""
    filepaths = []
    for dirpath, subdirs, filenames in os.walk(top):
        for file in filenames:
            filepaths.append(os.path.realpath(os.path.join(dirpath, file)))
    return filepaths

def get_matches(index: Index, basename, size, type):
    #Next step: migrate to be a method of Index.
    #Separate out the comparison logic to FileRecord class. Implement FileRecord.matches(record)
    match_list = []
    for record in index.table:
        if (basename is None) or (basename == record.basename):
            if (size is None) or (size == record.size):
                if (type is None) or (type == record.type):
                    match_list.append(record)
    return match_list


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
    for record in get_matches(file_table, name, size, type):
        click.echo(record.fullpath, file=out)
