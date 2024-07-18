import os

INPUT_FOLDERS = ['./data/LKGREL25', './data/PK25', './data/SMR25']
"""
TILES_TO_PROCESS = [
    "1123", "1124", "1125",
    "1143", "1144", "1145",
    "1162", "1163", "1164", "1165",
    "1182", "1183"
]
"""
TILES_TO_PROCESS = ["1164"]
DATA_LOCATION = "./input/DATA_NE.csv"
GROUND_TRUTH = "./test/GBAUP_TEST_DATA.csv"

FRAMES_SIZE = (7000, 4800)
PROCESSING_FOLDER = "./regbl_process/"
INPUT_FRAMES_FOLDER = PROCESSING_FOLDER+'frames/'
PROCESSED_FRAME_FOLDER = PROCESSING_FOLDER+"regbl_frame/frame/"

TILES_LIST_FILENAME = "tiles_list"
TILES_LIST_PATH = os.path.join(PROCESSING_FOLDER, TILES_LIST_FILENAME)

EGID_OUTPUT_PATH      = os.path.join(PROCESSING_FOLDER, "output/egid/")
POSITION_OUTPUT_PATH  = os.path.join(PROCESSING_FOLDER, "output/position/")
DETECT_OUTPUT_PATH    = os.path.join(PROCESSING_FOLDER, "output/detect/")
FRAME_OUTPUT_PATH     = os.path.join(PROCESSING_FOLDER, "output/frame/")
DEDUCE_OUTPUT_PATH    = os.path.join(PROCESSING_FOLDER, "output/deduce/")
SURFACE_OUTPUT_PATH   = os.path.join(PROCESSING_FOLDER, "output/surface/")
REFERENCE_OUTPUT_PATH = os.path.join(PROCESSING_FOLDER, "output/reference/")

OUTPUT_FOLDER = "./output/"