import cv2, os
import numpy as np
from parameters import *
from src.utils import *

SEARCH_RADIUS = 4

def get_connected(image, mask, x, y, erase):
    connected = []
    head = 0
    neighbors = [(+1, +0), (-1, +0), (+0, +1), (+0, -1)]
    connected.append([x, y])
    mask[y, x] = 255
    while head < len(connected) and len(connected) < 5000:
        for lc_i in range(len(neighbors)):
            lc_u = connected[head][0] + neighbors[lc_i][0]
            lc_v = connected[head][1] + neighbors[lc_i][1]

            if lc_u < 0 or lc_v < 0 or lc_u >= image.shape[1] or lc_v >= image.shape[0]:
                continue

            if mask[lc_v, lc_u] == 0:
                if image[lc_v, lc_u] == 0:
                    connected.append([lc_u, lc_v])
                    mask[lc_v, lc_u] = 255
        head += 1

    if erase:
        for i in range(len(connected)):
            mask[connected[i][1], connected[i][0]] = 0
    return connected

def detect_on_map(map, center):
    for x in range(-SEARCH_RADIUS, SEARCH_RADIUS+1):
        for y in range(-SEARCH_RADIUS, SEARCH_RADIUS+1):
            if x*x + y*y <= SEARCH_RADIUS**2:
                u = center[0] + x
                v = center[1] + y
                if 0 <= u < map.shape[1] and 0 <= v < map.shape[0] and map[v, u] == 0:
                    return (u,v)
    return None

# Returns the ratio of pixels that changed from the previous call
SIDE = 10
SHAPES = {}
def shape_ratio_changed(map, x, y, egid, side=10):
    half_side = side // 2
    count_different = 0

    if egid not in SHAPES :
        SHAPES[egid] =  np.zeros((SIDE, SIDE), dtype=np.uint8)

    for cur_x in range(SIDE):
        for cur_y in range(SIDE):
            map_x = x+cur_x-half_side
            map_y = y+cur_y-half_side
            if map_x < 0 or map_y < 0  or map_x >= map.shape[1] or map_y >= map.shape[0] :
                continue
            if SHAPES[egid][cur_x, cur_y] != map[map_y, map_x] :
                count_different += 1
            SHAPES[egid][cur_x, cur_y] = map[map_y, map_x]
    return count_different / (SIDE*SIDE)

def regbl_detect(map, track, mask, year):
    for egid_file in os.listdir(EGID_OUTPUT_PATH):
        if os.path.isfile(os.path.join(EGID_OUTPUT_PATH, egid_file)):
            egid = os.path.basename(egid_file)
            with open(os.path.join(POSITION_OUTPUT_PATH, year, egid), 'r') as input:
                found = False
                total = 0
                while not found:
                    line = input.readline().strip()
                    if line:
                        line_split = line.split(" ")
                        found_x = int(line_split[0])
                        found_y = int(line_split[1])
                        found_pos = detect_on_map(map, (found_x, found_y))
                        if found_pos != None:
                            found = True
                            found_x, found_y = found_pos
                            color = (0, 255, 0, 255)
                        else:
                            color = (0, 0, 255, 255)
                        cv2.line(track, (found_x, found_y - 3), (found_x, found_y + 3), color)
                        cv2.line(track, (found_x - 3, found_y), (found_x + 3, found_y), color)
                        total += 1
                    else:
                        break

                if total == 0:
                    fatal_error("Unable to import position from position file")
                
                area = len(get_connected(map, mask, found_x, found_y, True)) if found else 0
                shape_changed = shape_ratio_changed(map, found_x, found_y, egid)

                with open(os.path.join(DETECT_OUTPUT_PATH, egid), 'a') as f:
                    f.write(f"{year} {'1' if found else '0'} {found_x} {found_y} {area} {shape_changed}\n")

def detect():
    regbl_list = []
    with open(TILES_LIST_PATH, 'r') as list_file:
        for line in list_file:
            regbl_list.append(line.split(" "))

    if len(regbl_list) == 0:
        fatal_error(f"Unable to import storage list file from {TILES_LIST_PATH}")

    for list_line in regbl_list:
        current_year = list_line[0]
        list_height, list_width = int(list_line[5]), int(list_line[6])
        print(f"Processing year {current_year} ...")

        map = cv2.imread(os.path.join(PROCESSED_FRAME_FOLDER,current_year+".tif"), cv2.IMREAD_GRAYSCALE)
        if map is None:
            fatal_error(f"Unable to import map for year {current_year}")
        
        if list_height != map.shape[1] or list_width != map.shape[0]:
            fatal_error(f"Inconsistency between map size and storage list size")

        mask = np.zeros(map.shape, dtype=np.uint8)
        track = np.zeros((map.shape[0], map.shape[1], 4), dtype=np.uint8)

        regbl_detect(cv2.flip(map, 0), track, mask, current_year)
        cv2.imwrite(os.path.join(PROCESSING_FOLDER, FRAME_OUTPUT_PATH+current_year+".tif"), cv2.flip(track, 0))
