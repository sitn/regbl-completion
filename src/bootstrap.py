import os, sys
from parameters import *
from src.utils import *

DELIMITER = '\t'

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

            regbl_EGID = detect_database_header(first_line, "EGID")
            regbl_GKODE = detect_database_header(first_line, "GKODE")
            regbl_GKODN = detect_database_header(first_line, "GKODN")
            regbl_GBAUJ = detect_database_header(first_line, "GBAUJ")
            regbl_GAREA = detect_database_header(first_line, "GAREA")

            if regbl_EGID < 0 or regbl_GKODE < 0 or regbl_GKODN < 0 or regbl_GBAUJ < 0 or regbl_GAREA < 0:
                fatal_error(f"Unable to locate necessary fields in GEB database")

            for line in data_file:
                line = line.strip()

                regbl_x = float(detect_database_entry(line, regbl_GKODE))
                regbl_y = float(detect_database_entry(line, regbl_GKODN))
                regbl_token = detect_database_entry(line, regbl_EGID)
                regbl_rdate = detect_database_entry(line, regbl_GBAUJ)
                regbl_rarea = detect_database_entry(line, regbl_GAREA)

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


def bootstrap_entries(ein_path, export_egid, tiles_list):
    try:
        with open(ein_path, 'r') as ein_stream:
            regbl_head = ein_stream.readline().strip()
            regbl_EGID = detect_database_header(regbl_head, "EGID")
            regbl_DKODE = detect_database_header(regbl_head, "DKODE")
            regbl_DKODN = detect_database_header(regbl_head, "DKODN")

            if regbl_EGID < 0 or regbl_DKODE < 0 or regbl_DKODN < 0:
                print("error: unable to locate necessary fields in EIN database", file=sys.stderr)
                sys.exit(1)

            for regbl_line in ein_stream:
                regbl_line = regbl_line.strip()

                regbl_x = float(detect_database_entry(regbl_line, regbl_DKODE))
                regbl_y = float(detect_database_entry(regbl_line, regbl_DKODN))
                regbl_token = detect_database_entry(regbl_line, regbl_EGID)

                if os.path.isfile(os.path.join(export_egid, regbl_token)):
                    regbl_transfer = []

                    for regbl_parse in tiles_list:
                        regbl_u = round_coordinate(regbl_x, float(regbl_parse[1]), float(regbl_parse[2]), float(regbl_parse[5]))
                        regbl_v = round_coordinate(regbl_y, float(regbl_parse[3]), float(regbl_parse[4]), float(regbl_parse[6]))

                        if 0 <= regbl_u < int(regbl_parse[5]) and 0 <= regbl_v < int(regbl_parse[6]):
                            regbl_transfer.append([regbl_u, regbl_v])

                    if len(regbl_transfer) == len(tiles_list):
                        for regbl_parse in tiles_list:
                            output_path = os.path.join(POSITION_OUTPUT_PATH, regbl_parse[0], regbl_token)
                            with open(output_path, 'a') as regbl_output:
                                regbl_output.write(f"{regbl_transfer[regbl_parse][0]} {regbl_transfer[regbl_parse][1]}\n")

    except FileNotFoundError:
        fatal_error("unable to open EIN database")


def bootstrap(EIN_path=None):
    tiles_list = list(map( lambda line : line.split(' '), read_file(TILES_LIST_PATH)))
    if not tiles_list:
        fatal_error(f"Unable to read {TILES_LIST_PATH}")

    for line in tiles_list:
        os.makedirs(os.path.join(POSITION_OUTPUT_PATH, line[0]), exist_ok=True)

    bootstrap_extract(tiles_list)

    if EIN_path:
        bootstrap_entries(EIN_path, EGID_OUTPUT_PATH, tiles_list)
    else:
        print("Warning: EIN database not provided. Ignoring building entries")
