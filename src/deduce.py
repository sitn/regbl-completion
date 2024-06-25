import os, csv
from parameters import *
from src.utils import *

def deduce():
    print(f"Exporting results to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, mode='w', newline='') as csv_file:
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
            previous_shape_changed = False
            first_year = int(lines[-1].split()[0])

            detected_year   = 9999
            last_not_detected_year = 0

            notes = []
            changes_counter = 0
            shape_changed = False

            i=0
            for line in lines:
                year, state, x, y, area, shape_change = [to_int_or_float(x) for x in line.split()]
                shape_changed = shape_change > 0.3

                if (previous_state == 0 and state == 1) or (state == 1 and previous_shape_changed and not shape_changed) :
                    detected_year = year
                    last_not_detected_year = previous_year
                
                # If detection oscillates between found / not found, we add a note
                if state != previous_state :
                    changes_counter+=1

                previous_state = state
                previous_year  = year
                previous_shape_changed = shape_changed
                i+=1

            shape_changed = False
            for line in lines:
                year, state, x, y, area, shape_change = [to_int_or_float(x) for x in line.split()]
                if shape_change > 0.3 and year != first_year and not last_not_detected_year <= year <= detected_year :
                    shape_changed = True

            if shape_changed:
                notes.append("SHAPE_CHANGED")
            if changes_counter > 1 :
                notes.append("OSCILLATE")

            csv_writer.writerow([file_name, last_not_detected_year, detected_year, ' '.join(notes)])
            with open(DEDUCE_OUTPUT_PATH+file_name, mode='w') as deduce_file: 
                deduce_file.write(str(detected_year) + " " + str(last_not_detected_year))
