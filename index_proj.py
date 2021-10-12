#TODO:
# - can abstract Index and make alternate implementations later
# Possible Features:
# - make index human readable (json/csv)
# - implement reverse index for faster search
# - support regex expressions


import os
import pickle
import click

INDEX_DEFAULT="index.idx"

class FileRecord():
    """A FileRecord contains the file path and relevant metadata for indexing"""
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
        """FileRecords will match if attributes are equal or None"""
        if not isinstance(query, FileRecord):
            return False
        path_match = (query.fullpath is None) or (self.fullpath is None) or (query.fullpath == self.fullpath)
        name_match = (query.basename is None) or (self.basename is None) or (query.basename == self.basename)
        size_match = (query.size is None) or (self.size is None) or (query.size == self.size)
        type_match = (query.type is None) or (self.type is None) or (query.type == self.type)
        return path_match and name_match and size_match and type_match


class Index():
    """A searchable index for a directory tree"""
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

    def get_matches(self, query):
        return [file for file in self.table if file.matches(query)]



# The command line interface:

@click.group()
def index():
    """Use to traverse a base directory and create an index file that can be used to quickly lookup files by name, size, and content type"""
    pass

@index.command()
@click.option('--dir', type=click.Path(), help='The path of the directory to index. Defaults to current directory')
@click.option('--out', default=INDEX_DEFAULT, type=click.File('wb'), help=f'The file name of the created index. Defaults to {INDEX_DEFAULT}')
def create(dir, out):
    """Generates an index of all files in the directory tree"""
    if dir is None: dir = os.getcwd()
    file_table = Index.generate(dir)
    pickle.dump(file_table, out)

@index.command()
@click.argument('source', default=INDEX_DEFAULT, type=click.File('rb'), required=False)
@click.option('--name', type=str, help='Finds only files with this name (Example: "file.txt")')
@click.option('--size', type=int, help='Finds only files with this size (Example: 1532)')
@click.option('--type', type=str, help='Finds only files with this extension (Example: ".png")')
@click.option('--out', type=click.File('w'), default='-', help='Writes the output to this file. Defaults to stdout')
def search(source, name, size, type, out):
    """Returns paths to the files in the directory tree which match all parameters. If no parameters are given, it finds all files. Requires an index file."""
    file_table = pickle.load(source)
    query = FileRecord(None, name, size, type)
    for record in file_table.get_matches(query):
        click.echo(record.fullpath, file=out)
