import math, os, shutil, multiprocessing
from src.utils import *
from parameters import *
from src.bootstrap import bootstrap
from src.segment import segment
from src.detect import detect
from src.deduce import deduce
from src.track import track

def write_tiles_list(year, tfw_path):
    tfw = read_file(tfw_path)
    minX = math.floor(float(tfw[4]))
    maxX = minX+FRAMES_SIZE[0]*float(tfw[0])
    maxY = math.floor(float(tfw[5]))
    minY = maxY-FRAMES_SIZE[1]*-float(tfw[3])
    with open(TILES_LIST_PATH, 'a') as file_out:
        file_out.write(f'{year} {minX} {maxX} {minY} {maxY} {FRAMES_SIZE[0]} {FRAMES_SIZE[1]}\n')


def initialize(input_folders, tile_id):
    print_subtitle("Extracting images from raw data...")
    for folder in input_folders:
        for filename in os.listdir(folder):
            filepath  = os.path.join(folder, filename)

            if os.path.splitext(filename)[1] == '.tif':
                filename_year = filename.split('_')[-2]
                filename_tile = filename.split('_')[-3]

                if filename_tile == tile_id :
                    output_file = os.path.join(INPUT_FRAMES_FOLDER, filename_year+".tif")
                    print(f"Copying and resizing year {filename_year} .tif / .tfw")
                    shutil.copy(filepath, output_file)
                    original_size = resize_image(output_file, FRAMES_SIZE)
                    tfw_from = os.path.join(folder, os.path.splitext(filename)[0]+".tfw")
                    tfw_to = os.path.join(INPUT_FRAMES_FOLDER, filename_year+".tfw")
                    shutil.copy(tfw_from, tfw_to)
                    tfw = read_file(tfw_from)

                    new_pixel_size_x = float(tfw[0])*(original_size[0]/FRAMES_SIZE[0])
                    new_pixel_size_y = float(tfw[3])*(original_size[1]/FRAMES_SIZE[1])
                    with open(tfw_to, 'w') as tfw_file:
                        for i in range(len(tfw)):
                            if i == 0:
                                tfw_file.write(str(new_pixel_size_x))
                            elif i == 3 :
                                tfw_file.write(str(new_pixel_size_y))
                            elif i == 4 :
                                tfw_file.write(str(float(tfw[i]) - float(tfw[0])/2 + new_pixel_size_x/2 ))
                            elif i == 5 :
                                tfw_file.write(str(float(tfw[i]) + float(tfw[3])/2 + new_pixel_size_y/2 ))
                            else :
                                tfw_file.write(tfw[i])
                            tfw_file.write('\n')

    frames = os.listdir(INPUT_FRAMES_FOLDER)
    frames.sort(reverse=True)
    for frame in frames:
        if os.path.splitext(frame)[1] == '.tif':
            year = os.path.splitext(frame)[0]
            write_tiles_list(year, os.path.join(INPUT_FRAMES_FOLDER, year+".tfw"))


def test(truth_file, output_file, min_year, max_year):
    truth_rows = read_csv(truth_file)
    output_rows = read_csv(output_file)

    correct = 0
    incorrect = 0
    correct_filtered = 0
    incorrect_filtered = 0
    build_before_first_year = 0
    build_after_last_year = 0
    for truth_row in truth_rows:
        for output_row in output_rows:
            if truth_row[1] == output_row[0]: # Compare EGID
                built_year =  int(truth_row[6])
                estimated_built_min = int(output_row[1])
                estimated_built_max = int(output_row[2])
                if estimated_built_min <= built_year <= estimated_built_max:
                    print(f"CORRECT {truth_row[1]} {','.join(output_row[3].split(' '))}")
                    correct += 1
                else:
                    print(f"INCORRECT {truth_row[1]} {','.join(output_row[3].split(' '))}")
                    incorrect += 1

                if estimated_built_min < min_year:
                    build_before_first_year += 1
                if estimated_built_max > max_year:
                    build_after_last_year += 1
                if output_row[3] == "":
                    if estimated_built_min <= built_year <= estimated_built_max:
                        correct_filtered += 1
                    else:
                        incorrect_filtered += 1

    total = incorrect + correct
    total_filtered = incorrect_filtered + correct_filtered
    print(f"Results :")
    print(f"Non filtered :")
    print(f"Correct : {correct}/{total} ({percent(correct,total)})")
    print(f"Incorrect : {incorrect}/{total} ({percent(incorrect,total)})\n")
    print(f"Filtered :")
    print(f"Built before first year : {build_before_first_year}")
    print(f"Built after last year : {build_after_last_year}")
    print(f"Correct : {correct_filtered}/{total_filtered} ({percent(correct_filtered,total_filtered)})")
    print(f"Incorrect : {incorrect_filtered}/{total_filtered} ({percent(incorrect_filtered,total_filtered)})")


def main():
    print_title("RegBL Completion - Starting")

    for tile_id in TILES_TO_PROCESS :
        print_title(f"Processing tile {tile_id}")
    
        print_subtitle(f"Removing folder {PROCESSING_FOLDER}")
        shutil.rmtree(PROCESSING_FOLDER, ignore_errors=True)

        output_folder = os.path.join(OUTPUT_FOLDER, tile_id)

        create_folders([
            INPUT_FRAMES_FOLDER, 
            PROCESSING_FOLDER, 
            PROCESSED_FRAME_FOLDER,
            DETECT_OUTPUT_PATH, 
            FRAME_OUTPUT_PATH, 
            OUTPUT_FOLDER, 
            DEDUCE_OUTPUT_PATH,
            EGID_OUTPUT_PATH,
            REFERENCE_OUTPUT_PATH,
            SURFACE_OUTPUT_PATH,
            output_folder
        ])

        print_title(f"Tile {tile_id} - Initializing")
        initialize(INPUT_FOLDERS, tile_id)
        
        print_title(f"Tile {tile_id} - Segmenting")
        segment_paths = []
        for file in os.listdir(INPUT_FRAMES_FOLDER):
            if file.endswith(".tif"):
                segment_paths.append( (os.path.join(INPUT_FRAMES_FOLDER, file), os.path.join(PROCESSED_FRAME_FOLDER, file)) )
        with multiprocessing.Pool() as pool:
            pool.starmap(segment, segment_paths)


        print_title(f"Tile {tile_id} - Bootstrapping")
        bootstrap()
        
        print_title(f"Tile {tile_id} - Detection")
        detect()

        output_file = os.path.join(output_folder, "result.csv")
        
        print_title(f"Tile {tile_id} - Deduction")
        deduce(output_file)
        
        
        print_title(f"Tile {tile_id} - Test")
        test(GROUND_TRUTH, output_file, 1956, 2021)
        
        
        print_title(f"Tile {tile_id} - Tracking")
        for egid in os.listdir(EGID_OUTPUT_PATH):
            print(f"Processing EGID {egid}")
            track(egid, output_folder)

    print("Finished")


if __name__ == "__main__": main()