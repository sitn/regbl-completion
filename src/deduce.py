import os, csv
from parameters import *
from src.utils import *

MAX_SHAPE_CHANGED = 0.5

def deduce(output_file):
    print(f"Exporting results to {output_file}")
    with open(output_file, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['EGID', 'LAST_NOT_DETECTED', 'FIRST_DETECTED', 'NOTE'])

        for file_name in os.listdir(DETECT_OUTPUT_PATH):
            file_path = os.path.join(DETECT_OUTPUT_PATH, file_name)

            lines = []
            if os.path.isfile(file_path):
                with open(file_path, 'r') as input_file: 
                    for line in input_file:
                        lines.insert(0, line)

            previous_year = 0
            previous_state = 0
            first_year = int(lines[-1].split()[0])

            detected_year   = 9999
            last_not_detected_year = 2021

            notes = []
            changes_counter = 0

            i=0
            for line in lines:
                year, state, x, y, area, shape_change = [to_int_or_float(x) for x in line.split()]

                # TODO : To consider, if the shape changes, we assume that the building year was after the change happened
                if previous_state == 0 and state == 1 :
                    detected_year = year
                    last_not_detected_year = previous_year
                
                # If detection oscillates between found / not found, we add a note
                if state != previous_state :
                    changes_counter+=1

                previous_state = state
                previous_year  = year
                i+=1

            shape_changed = False
            for line in lines:
                year, state, x, y, area, shape_change = [to_int_or_float(x) for x in line.split()]
                # TODO : We have to check this condition
                #if shape_change > 0.3 and year != first_year and not last_not_detected_year <= year <= detected_year :
                if shape_change > MAX_SHAPE_CHANGED and year != first_year :
                    shape_changed = True

            if shape_changed:
                notes.append("SHAPE_CHANGED")
            if changes_counter > 1 :
                notes.append("OSCILLATE")

            csv_writer.writerow([file_name, last_not_detected_year, detected_year, ' '.join(notes)])
            with open(DEDUCE_OUTPUT_PATH+file_name, mode='w') as deduce_file: 
                deduce_file.write(str(detected_year) + " " + str(last_not_detected_year))
