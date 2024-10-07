import os
from parameters import *
from src.utils import *

DELIMITER = ';'

def detect_database_header(line, target):
    try:
        return line.strip().split(DELIMITER).index(target)
    except ValueError:
        return -1

def detect_database_entry(line, target_index):
    tokens = line.strip().split(DELIMITER)
    return tokens[target_index] if target_index < len(tokens) else ''

def round_coordinate(value, min_value, max_value, scale):
    return round(((value - min_value) / (max_value - min_value)) * scale)

def bootstrap_extract(tiles_list):
    try:
        with open(DATA_LOCATION, 'r') as data_file:
            first_line = data_file.readline().strip()

            egid = detect_database_header(first_line, "EGID")
            gkode = detect_database_header(first_line, "GKODE")
            gkodn = detect_database_header(first_line, "GKODN")
            gbauj = detect_database_header(first_line, "GBAUJ")
            garea = detect_database_header(first_line, "GAREA")

            if egid < 0 or gkode < 0 or gkodn < 0 or gbauj < 0 or garea < 0:
                fatal_error(f"Unable to locate necessary fields in GEB database")

            for line in data_file:
                line = line.strip()
                regbl_x = float(detect_database_entry(line, gkode))
                regbl_y = float(detect_database_entry(line, gkodn))
                regbl_token = detect_database_entry(line, egid)
                regbl_rdate = detect_database_entry(line, gbauj)
                regbl_rarea = detect_database_entry(line, garea)

                regbl_transfer = []

                for line in tiles_list:
                    u = round_coordinate(regbl_x, float(line[1]), float(line[2]), float(line[5]))
                    v = round_coordinate(regbl_y, float(line[3]), float(line[4]), float(line[6]))

                    if 0 <= u < int(line[5]) and 0 <= v < int(line[6]):
                        regbl_transfer.append([u, v])

                if len(regbl_transfer) != len(tiles_list):
                    if len(regbl_transfer) > 0:
                        print(f"Warning: rejected building ({regbl_token}) as partially appearing on spatio-temporal raster")
                else:
                    create_file(os.path.join(EGID_OUTPUT_PATH, regbl_token))

                    for index, line in enumerate(tiles_list):
                        with open(os.path.join(POSITION_OUTPUT_PATH, line[0], regbl_token), 'w') as f:
                            f.write(f"{regbl_transfer[index][0]} {regbl_transfer[index][1]}\n")

                    if regbl_rdate:
                        with open(os.path.join(REFERENCE_OUTPUT_PATH, regbl_token), 'w') as f:
                            f.write(f"{regbl_rdate}\n")

                    with open(os.path.join(SURFACE_OUTPUT_PATH, regbl_token), 'w') as f:
                        f.write(f"{regbl_rarea}\n")

    except FileNotFoundError:
        fatal_error(f"Unable to open GEB database in {DATA_LOCATION}")


def bootstrap():
    tiles_list = list(map( lambda line : line.split(' '), read_file(TILES_LIST_PATH)))
    if not tiles_list:
        fatal_error(f"Unable to read {TILES_LIST_PATH}")

    for line in tiles_list:
        os.makedirs(os.path.join(POSITION_OUTPUT_PATH, line[0]), exist_ok=True)

    bootstrap_extract(tiles_list)
