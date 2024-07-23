import os

# List of folder where the national maps are location.
# Maps will be search for in each folder.
INPUT_FOLDERS = ['./data/LKGREL25', './data/PK25', './data/SMR25']

# List of tiles to process. Each tile will be process independently.
TILES_TO_PROCESS = ["1164"]

# Input file that contains columns EGID, GKODE, GKODN
DATA_LOCATION = "./input/DATA_NE.csv"

# Ground truth to evaluate the detection. Must be similar to the file in DATA_LOCATION
# with an additional GBAUJ column
GROUND_TRUTH = "./test/GBAUP_TEST_DATA.csv"

# Folder where the result will be written. One subfolder will be created per tile.
OUTPUT_FOLDER = "./output/"

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