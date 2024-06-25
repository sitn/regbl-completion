import cv2, os, math
import numpy as np
from parameters import *
from src.utils import *

CROP_SIZE = 50
FONT = cv2.FONT_HERSHEY_PLAIN

WHITE = (255, 255, 255)
GREY = (64, 64, 64)
PURPLE = (224, 16, 224)
FOUND_COLOR = (98, 142, 22)
NOT_FOUND_COLOR = (78, 66, 192)

def draw_border(img, x, y, detected):
    margin = int(CROP_SIZE * 0.75)
    height, width, depth = img.shape
    color = FOUND_COLOR if detected else NOT_FOUND_COLOR
    cv2.rectangle(img, (0, -1), (width, height + 2), color, 1)
    cv2.line(img, (x, 0),      (x, y - margin), color)
    cv2.line(img, (0, y),      (x - margin, y), color)
    cv2.line(img, (x, height), (x, y + margin), color)
    cv2.line(img, (width, y),  (x + margin, y), color)


def tracker_building(img, regbl_cnx, regbl_cny, file):
    pos_x, pos_y = map(float, file.readline().split())
    cv2.circle(img, (regbl_cnx, regbl_cny), 1, PURPLE, cv2.FILLED)
    file.seek(0)
    for line in file:
        regbl_ux, regbl_uy = map(float, line.split())
        regbl_ux -= pos_x
        regbl_uy -= pos_y
        regbl_ux = regbl_cnx + round(regbl_ux)
        regbl_uy = regbl_cny - round(regbl_uy)
        cv2.circle(img, (int(regbl_ux), int(regbl_uy)), 1, PURPLE, cv2.FILLED)
        cv2.line(img, (regbl_cnx, regbl_cny), (int(regbl_ux), int(regbl_uy)), PURPLE)


def draw_surface(img, x, y, surface):
    if surface > 0:
        cv2.circle(img, (x, y), int(math.sqrt(surface / math.pi)), PURPLE)


def draw_detect_cross(img, x, y, size):
    x, y = int(x), int(y)
    cv2.circle(img, (x, y), int(math.sqrt(size / math.pi)), FOUND_COLOR)
    cv2.line(img, (x, y-3), (x, y+3), FOUND_COLOR)
    cv2.line(img, (x-3, y), (x+3, y), FOUND_COLOR)


def tracker_timeline(width, year, detect):
    result = np.full((18, width, 3), FOUND_COLOR if detect else NOT_FOUND_COLOR, dtype=np.uint8)
    cv2.putText(result, year, (40 + (width - (CROP_SIZE * 2)) // 2, 14), FONT, 1, WHITE)
    return result


def tracker_detection(width, year, hbound):
    regbl_color = FOUND_COLOR if int(year) >= int(hbound) else NOT_FOUND_COLOR
    return np.full((18, width, 3), regbl_color, dtype=np.uint8)


def tracker_reference(width, egid, ref_year, udeduce, ldeduce):
    if ref_year == "NO_REF":
        regbl_color = GREY
    else:
        regbl_color = FOUND_COLOR if int(udeduce) >= int(ref_year) > int(ldeduce) else NOT_FOUND_COLOR
    result = np.full((18, width, 3), regbl_color, dtype=np.uint8)
    cv2.putText(result, f"{egid} {ldeduce}-{udeduce} {ref_year}", (0, 14), FONT, 1, WHITE)
    return result


def track(egid):
    tiles_list = list(map(lambda x: x.split(" "), read_file(TILES_LIST_PATH)))

    try:
        with open(os.path.join(DEDUCE_OUTPUT_PATH, egid), 'r') as f:
            regbl_udeduce, regbl_ldeduce = f.readline().split()
    except FileNotFoundError:
        fatal_error(f"Unable to import building deduced range")

    try:
        with open(os.path.join(SURFACE_OUTPUT_PATH, egid), 'r') as f:
            area = int(f.readline().strip())
    except Exception:
        print("Warning: Building surface file not found: surface not displayed")
        area = -1

    try:
        detect_content = open(os.path.join(DETECT_OUTPUT_PATH, egid), 'r')
    except FileNotFoundError:
        fatal_error(f"Unable to locate deduction file")

    regbl_ftln = None
    regbl_stln = None
    regbl_alin = None
    regbl_adet = None

    for index, line in enumerate(detect_content):
        year, detect_flag, regbl_detx, regbl_dety, detect_size, shape_factor = line.split()
        detected = detect_flag == '1'
        regbl_detx = float(regbl_detx)
        regbl_dety = float(regbl_dety)
        detect_size = float(detect_size)
        shape_factor = float(shape_factor)

        frame_width = int(tiles_list[index][5])
        frame_height = int(tiles_list[index][6])

        try:
            with open(os.path.join(POSITION_OUTPUT_PATH, year, egid), 'r') as f:
                pos_x, pos_y = map(int, f.readline().split())
        except FileNotFoundError:
            fatal_error(f"Unable to access position file for year {year} and egid {egid}")

        scale_factor = frame_width / (float(tiles_list[index][2]) - float(tiles_list[index][1]))
        pos_y = frame_height - pos_y - 1
        regbl_dety = frame_height - regbl_dety - 1

        crop_minx = pos_x - CROP_SIZE
        crop_miny = pos_y - CROP_SIZE

        regbl_cnx = CROP_SIZE
        regbl_cny = CROP_SIZE

        if crop_minx < 0:
            regbl_cnx += crop_minx
            crop_minx = 0
        if crop_miny < 0:
            regbl_cny += crop_miny
            crop_miny = 0

        crop_maxx = min(pos_x+CROP_SIZE, frame_width)
        crop_maxy = min(pos_y+CROP_SIZE, frame_height)

        frame = cv2.imread(os.path.join(INPUT_FRAMES_FOLDER, f"{year}.tif"))
        if frame is None:
            fatal_error(f"Unable to import original map of {year}")



        frame_cropped = frame[crop_miny:crop_maxy, crop_minx:crop_maxx]
        draw_border(frame_cropped, regbl_cnx, regbl_cny, detected)
        with open(os.path.join(POSITION_OUTPUT_PATH, year, egid), 'r') as f:
            tracker_building(frame_cropped, regbl_cnx, regbl_cny, f)
        draw_surface(frame_cropped, regbl_cnx, regbl_cny, area * scale_factor)
        if detected :
            draw_detect_cross(frame_cropped, regbl_cnx + (regbl_detx - pos_x), regbl_cny + (regbl_dety - pos_y), detect_size)



        regbl_ftln = frame_cropped if regbl_ftln is None else np.hstack((frame_cropped, regbl_ftln))

        frame = cv2.imread(os.path.join(PROCESSED_FRAME_FOLDER, f"{year}.tif"))
        if frame is None:
            fatal_error(f"Unable to import segmented map {year}")



        frame_cropped = frame[crop_miny:crop_maxy, crop_minx:crop_maxx]
        draw_border(frame_cropped, regbl_cnx, regbl_cny, detected)
        with open(os.path.join(POSITION_OUTPUT_PATH, year, egid), 'r') as f:
            tracker_building(frame_cropped, regbl_cnx, regbl_cny, f)
        draw_surface(frame_cropped, regbl_cnx, regbl_cny, area * scale_factor)
        if detected : 
            draw_detect_cross(frame_cropped, regbl_cnx + (regbl_detx - pos_x), regbl_cny + (regbl_dety - pos_y), detect_size)



        regbl_stln = frame_cropped if regbl_stln is None else np.hstack((frame_cropped, regbl_stln))

        frame_cropped = tracker_timeline(frame_cropped.shape[1], year, detected)
        regbl_alin = frame_cropped if regbl_alin is None else np.hstack((frame_cropped, regbl_alin))

        frame_cropped = tracker_detection(frame_cropped.shape[1], year, regbl_udeduce)
        regbl_adet = frame_cropped if regbl_adet is None else np.hstack((frame_cropped, regbl_adet))

    detect_content.close()

    try:
        with open(os.path.join(REFERENCE_OUTPUT_PATH, egid), 'r') as f:
            ref_year = f.readline().strip()
    except FileNotFoundError:
        ref_year = "NO_REF"

    regbl_aref = tracker_reference(regbl_ftln.shape[1], egid, ref_year, regbl_udeduce, regbl_ldeduce)
    regbl_aref = np.vstack((regbl_aref, regbl_ftln, regbl_alin, regbl_stln, regbl_adet))

    cv2.imwrite(os.path.join(OUTPUT_FOLDER, f"{egid}.png"), regbl_aref)
