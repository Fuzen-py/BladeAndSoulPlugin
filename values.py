from os import mkdir, path

PATH = path.dirname(path.realpath(__file__))
DATA = path.join(PATH, 'Data')
if not path.exists(DATA):
    mkdir(DATA)
