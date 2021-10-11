# Take Home Project

Challenge: A directory contains multiple files and directories of non-uniform file and directory names. Create a program that traverses a base directory and creates an index file that can be used to quickly lookup files by name, size, and content type.

# Usage

The project `takehome` can be installed as a python package with `pip` and run from the command line. It is recommended to install the commands within a `venv` virtual environment.

The project installs the command `index` which has two subcommands `index create` and  `index search`. To lookup a file, first navigate to the directory you wish to search and create an index for that directory tree:
  index create
By default this will create an index file named "index.idx" for the current directory. You can use the parameters `--dir` to index a different directory and `--out` to choose a different index file name.

Then you can search the index for a file using:
  index search --name <basename> --size <filesize> --type <extension>
where `--name <basename>`,  `--size <filesize>`, and `-- type <extension>` are optional parameters that define properties of the files you want to find. The command will make a list of files in your directory tree which fulfill all the parameter you chose and will print out that list. You can use `--out` to instead write the list to a file. If you did not use the default name for your index file, you will need to provide the command with new index file name as a positional argument.

All commands have help pages using the `--help` flag.
