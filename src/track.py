import cv2, os, math
import numpy as np
from parameters import *
from src.utils import *

CROP_SIZE = 50
FONT = cv2.FONT_HERSHEY_PLAIN
BAND_HEIGHT = 18

WHITE = (255, 255, 255)
GREY = (64, 64, 64)
PURPLE = (224, 16, 224)
FOUND_COLOR = (98, 142, 22)
NOT_FOUND_COLOR = (78, 66, 192)

def draw_border(img, center, detected):
    margin = int(CROP_SIZE * 0.75)
    x, y = center
    height, width, depth = img.shape
    color = FOUND_COLOR if detected else NOT_FOUND_COLOR
    cv2.rectangle(img, (0, -1), (width, height + 2), color, 1)
    cv2.line(img, (x, 0),      (x, y - margin), color)
    cv2.line(img, (0, y),      (x - margin, y), color)
    cv2.line(img, (x, height), (x, y + margin), color)
    cv2.line(img, (width, y),  (x + margin, y), color)

def draw_building_marker(img, center):
    cv2.circle(img, center, 1, PURPLE, cv2.FILLED)

def draw_surface(img, center, surface):
    if surface > 0 : cv2.circle(img, center, int(math.sqrt(surface / math.pi)), PURPLE)

def draw_detect_cross(img, center, offset, size):
    x, y = int(center[0]+offset[0]), int(center[1]+offset[1])
    cv2.circle(img, (x, y), int(math.sqrt(size / math.pi)), FOUND_COLOR)
    cv2.line(img, (x, y-3), (x, y+3), FOUND_COLOR)
    cv2.line(img, (x-3, y), (x+3, y), FOUND_COLOR)

def draw_year(year, detect):
    result = np.full((BAND_HEIGHT, CROP_SIZE*2, 3), FOUND_COLOR if detect else NOT_FOUND_COLOR, dtype=np.uint8)
    cv2.putText(result, year, (40 , 14), FONT, 1, WHITE)
    return result


def draw_bottom_band(year, year_min):
    color = FOUND_COLOR if int(year) >= year_min else NOT_FOUND_COLOR
    return np.full((BAND_HEIGHT, CROP_SIZE*2, 3), color, dtype=np.uint8)


def draw_title(width, egid, ref_year, year_min, year_max):
    if ref_year == "NO_REF":
        color = GREY
    else:
        color = FOUND_COLOR if year_min >= int(ref_year) > year_max else NOT_FOUND_COLOR
    result = np.full((BAND_HEIGHT, width, 3), color, dtype=np.uint8)
    cv2.putText(result, f"{egid} {year_max}-{year_min} {ref_year}", (0, 14), FONT, 1, WHITE)
    return result

def draw(frame, center, isDetected, area, detect_size, delta_position_detected):
    draw_border(frame, center, isDetected)
    draw_building_marker(frame, center)
    draw_surface(frame, center, area)
    if isDetected :
        draw_detect_cross(frame, center, delta_position_detected, detect_size)

def stack_frame(frame, stack):
    return frame if stack is None else np.hstack((frame, stack))

def track(egid):
    tiles_list = list(map(lambda x: x.split(" "), read_file(TILES_LIST_PATH)))

    try:
        with open(os.path.join(DEDUCE_OUTPUT_PATH, egid), 'r') as f:
            deduce_year_min, deduce_year_max = map(int, f.readline().split())
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

    frame_input_img = None
    frame_processed_img = None
    years_band_img = None
    bottom_band_img = None

    for index, line in enumerate(detect_content):
        year, detect_flag, detected_x, detected_y, detect_size, shape_factor = line.split()
        detected = detect_flag == '1'
        detected_x = float(detected_x)
        detected_y = float(detected_y)
        detect_size = float(detect_size)
        shape_factor = float(shape_factor)

        frame_shape = (int(tiles_list[index][5]), int(tiles_list[index][6]))

        scaled_area = area * (frame_shape[0] / (float(tiles_list[index][2]) - float(tiles_list[index][1])))

        try:
            with open(os.path.join(POSITION_OUTPUT_PATH, year, egid), 'r') as f:
                pos_x, pos_y = map(int, f.readline().split())
        except FileNotFoundError:
            fatal_error(f"Unable to access position file for year {year} and egid {egid}")
        
        pos_y = frame_shape[1] - pos_y - 1
        detected_y = frame_shape[1] - detected_y - 1

        crop_minx = pos_x - CROP_SIZE
        crop_miny = pos_y - CROP_SIZE
        crop_maxx = pos_x + CROP_SIZE
        crop_maxy = pos_y + CROP_SIZE

        local_center = [CROP_SIZE, CROP_SIZE]

        if crop_minx < 0:
            local_center[0] += crop_minx
            crop_minx = 0
            crop_maxx = 2*CROP_SIZE
        elif crop_maxx >= frame_shape[0]:
            local_center[0] += frame_shape[0]-crop_maxx
            crop_minx = frame_shape[0]-2*CROP_SIZE
            crop_maxx = frame_shape[0]

        if crop_miny < 0:
            local_center[1] += crop_miny
            crop_miny = 0
            crop_maxy = 2*CROP_SIZE
        elif crop_maxy >= frame_shape[1]:
            local_center[1] += frame_shape[1]-crop_maxy
            crop_miny = frame_shape[1]-2*CROP_SIZE
            crop_maxy = frame_shape[1]

        if crop_maxx - crop_minx != 100 or crop_maxy - crop_miny != 100 :
            print("ERROR : ")
            print(f"Width : {crop_maxx - crop_minx}")
            print(f"Height : {crop_maxy - crop_miny}")


        delta_position_detected = (detected_x - pos_x, detected_y - pos_y)

        frame_input = cv2.imread(os.path.join(INPUT_FRAMES_FOLDER, f"{year}.tif"))
        if frame_input is None:
            fatal_error(f"Unable to import original map of {year}")

        frame_processed = cv2.imread(os.path.join(PROCESSED_FRAME_FOLDER, f"{year}.tif"))
        if frame_processed is None:
            fatal_error(f"Unable to import segmented map {year}")

        input_cropped = frame_input[crop_miny:crop_maxy, crop_minx:crop_maxx]
        draw(input_cropped, local_center, detected, scaled_area, detect_size, delta_position_detected)
        frame_input_img = stack_frame(input_cropped, frame_input_img)

        processed_cropped = frame_processed[crop_miny:crop_maxy, crop_minx:crop_maxx]
        draw(processed_cropped, local_center, detected, scaled_area, detect_size, delta_position_detected)
        frame_processed_img = stack_frame(processed_cropped, frame_processed_img)

        years_band_img = stack_frame(draw_year(year, detected), years_band_img)
        bottom_band_img = stack_frame(draw_bottom_band(year, deduce_year_min), bottom_band_img)

    detect_content.close()

    try:
        with open(os.path.join(REFERENCE_OUTPUT_PATH, egid), 'r') as f:
            ref_year = f.readline().strip()
    except FileNotFoundError:
        ref_year = "NO_REF"

    title_img = draw_title(frame_input_img.shape[1], egid, ref_year, deduce_year_min, deduce_year_max)
    final_img = np.vstack((title_img, frame_input_img, years_band_img, frame_processed_img, bottom_band_img))
    cv2.imwrite(os.path.join(OUTPUT_FOLDER, f"{egid}.png"), final_img)
