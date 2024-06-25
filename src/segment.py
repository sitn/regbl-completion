import os, cv2, numpy as np
from src.utils import *

state_counter = 0
def save_tmp_state(image, path):
    global state_counter
    if path:
        cv2.imwrite(os.path.join(path, f"state-{state_counter}.png"), image)
        state_counter += 1

def equalize_image(image):
    ycrcb_image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    channels = list(cv2.split(ycrcb_image))
    mean, std = cv2.meanStdDev(channels[0])
    channels[0] = (((channels[0] - mean[0]) / std[0]) * 128 + mean[0]).astype(np.uint8)
    cv2.merge(channels, ycrcb_image)
    cv2.cvtColor(ycrcb_image, cv2.COLOR_YCrCb2BGR, image)

def extract_black(input_image, tolerance=60):
    r = input_image[:,:,0] < tolerance
    g = input_image[:,:,1] < tolerance
    b = input_image[:,:,2] < tolerance
    return np.where(r & g & b, 0, 255)

def get_black_neighbors(image, start_x, start_y, limit=10):
    neighbors = [[start_x, start_y]]
    head = 0
    neighbors_mask = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]])
    while head < len(neighbors) and len(neighbors) < limit:
        candidates = np.array(neighbors[head]) + neighbors_mask
        new_neighbors = [(u, v) for u, v in candidates if 0 <= u < image.shape[1] and 0 <= v < image.shape[0] and image[v, u] == 0]
        for u, v in new_neighbors:
            if [u, v] not in neighbors:
                neighbors.append([u, v])
        head += 1
    return neighbors

def iterate(input_image, kernel_size, blackRatio, nbIterations = 15, minClusterSize = 5):
    rows, cols = input_image.shape
    result = input_image.copy()
    kernel = np.ones((2*kernel_size+1, 2*kernel_size+1))
    cell_count = kernel.sum()

    # At each iterations, keep only the black pixels with more than blackRatio ratio of black pixels around them
    for _ in range(nbIterations):
        black_cell_count = cv2.filter2D((result == 0).astype(np.uint8), -1, kernel, borderType=cv2.BORDER_CONSTANT)
        result = np.where( (result == 0) & (black_cell_count/cell_count > blackRatio), 0, 255).astype(np.uint8)

    # Remove clusters of less than minClusterSize black pixels, considered artifacts
    for x in range(cols):
        for y in range(rows):
            if result[y, x] == 0:
                neighbors = get_black_neighbors(result, x, y, minClusterSize)
                if len(neighbors) < minClusterSize:
                    for n in neighbors:
                        result[n[1], n[0]] = 255
    return result

def segment(input_path, output_path, equalize=False, invert=False, intermediate_states_path=False):
    print(f"Segmenting {input_path} ...")
    global state_counter
    state_counter=0

    source = cv2.imread(input_path, cv2.IMREAD_COLOR)
    save_tmp_state(source, intermediate_states_path)

    if invert:
        source = 255 - source
        save_tmp_state(source, intermediate_states_path)

    if equalize:
        equalize_image(source)
        save_tmp_state(source, intermediate_states_path)

    black_mask = extract_black(source)
    save_tmp_state(black_mask, intermediate_states_path)

    result = iterate(black_mask, 2, 7.0/25.0)
    save_tmp_state(result, intermediate_states_path)
    cv2.imwrite(output_path, result)

"""
def segmentation_process_extract_building(clean_image, source_image, output_image, tolerance):
    tracker = np.zeros_like(source_image, dtype=np.uint8)
    output_image[:] = 255
    rows, cols = clean_image.shape
    for x in range(cols):
        for y in range(rows):
            if tracker[y, x] == 0 and clean_image[y, x] == 0:
                component = lc_connect_get(clean_image, tracker, x, y, False)
                if len(component) > 1:
                    for u, v in component:
                        lu, hu = max(u - tolerance, 0), min(u + tolerance, cols - 1)
                        lv, hv = max(v - tolerance, 0), min(v + tolerance, rows - 1)
                        for nx in range(lu, hu + 1):
                            for ny in range(lv, hv + 1):
                                if source_image[ny, nx] == 0:
                                    output_image[ny, nx] = 0
                        output_image[v, u] = 0
"""