#TODO: Clean Up Code. Delete duplicate functions
# - Restructure Code. Move functions into Class structure
# - can abstract Index and make alternate implementations later

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

    @classmethod
    def generate(cls, filepath):
        """Creates a FileRecord with completed properties from filepath"""
        record = cls(fullpath=filepath)
        record.basename = os.path.basename(record.fullpath)
        record.size = os.path.getsize(record.fullpath)
        record.type = os.path.splitext(record.fullpath)[1]
        return record

    def matches(self, query) -> bool:
        #TODO figure out where this belongs
        if (query.basename is None) or (query.basename == self.basename):
            if (query.size is None) or (query.size == self.size):
                if (query.type is None) or (query.type == self.type):
                    return True
        return False

class Index():
    def __init__(self, root='.', table=None):
        self.table = table if table is not None else []
        self.root = root
    def __str__(self):
        return "{" + str(self.root) + ", " + str(self.table) + "}"

    def add(self, record: FileRecord) -> None:
        self.table.append(record)
        return

    @classmethod
    def generate(cls, path):
        """Generate an Index for a given directory path"""
        created_index = cls(root=path)
        for dirpath, subdirs, filenames in os.walk(path):
            for file in filenames:
                filepath = os.path.realpath(os.path.join(dirpath, file))
                record = FileRecord.generate(filepath)
                created_index.add(record)
        return created_index

    def get_matches(self, basename, size, type):
        query = FileRecord(None, basename, size, type)
        return [file for file in self.table if file.matches(query)]


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
    file_table = Index.generate(dir)
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
    for record in file_table.get_matches(name, size, type):
        click.echo(record.fullpath, file=out)
