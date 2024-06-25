import os, sys, csv
from PIL import Image

def print_title(title):
    print(f"\n*****************\n{title}\n*****************")


def print_subtitle(title):
    print(f"\n****** {title} ******")


def create_folders(paths):
    for path in paths:
        os.makedirs(path, exist_ok=True)


def create_file(path):
    open(path, 'a').close()


def fatal_error(msg):
    print(f"Fatal error : {msg}")
    sys.exit(1)


def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().splitlines() 
    

def read_csv(file_path, ignore_header=True):
    result = []
    with open(file_path, mode='r') as f:
        f_csv = csv.reader(f, delimiter=',')
        if ignore_header : next(f_csv)
        for line in f_csv:
            result.append(line)
    return result
    
    
def resize_image(path, size):
    with Image.open(path) as img:
        original_size = img.size
        img.resize(size).save(path)
    return original_size


def to_int_or_float(s):
    try:
        return int(s)
    except ValueError:
        return float(s)
    

def percent(count, total):
    return f"{round(100*count/total,1)}%"