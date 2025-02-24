import os
import random

def read_pbm(file_path):
    """Reads a PBM file and returns a flattened binary matrix."""
    # ensuring file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File does not exist.")
    
    # opening file
    with open(file_path, 'r') as f:
        # stripping leading and trailing spaces + ignoring empty lines
        lines = [line.strip() for line in f if line.strip()]
    
    # basic error checking for file format and dimensions
    if lines[0] is not 'P1':
        raise ValueError(f"File is not in ASCII PBM format.")
    
    if lines[1] is not "16 16":
        raise ValueError(f"PBM file does not have 16x16 dimensions.")

    if len(lines[2:]) != 16:
        raise ValueError(f"Expected 16 rows.")


    # creating binary matrix
    binary_matrix = []

    # copying data from list into matrix
    for row in lines[2:]:
        if len(row.split()) is not 16:
            raise ValueError(f"Expected 16 pixels.")
        binary_matrix.extend([int(pixel) for pixel in row.split()])
    
    return binary_matrix

def write_pbm(state, file_path, size=(16, 16)):
    # check if file path is correnct
    if not isinstance(file_path, str) or not file_path.endswith(".pbm"):
        raise ValueError("Invalid file path.")
    
    # check input state size
    if len(state) != size[0] * size[1]:
        raise ValueError(f"Input state size is incorrect.")

    try:
        with open(file_path, 'w') as f:
            # writing file header and dimensions
            f.write(f"P1\n{size[0]} {size[1]}\n")
            
            # writing data
            for i in range(size[0]):
                row = state[i * size[1]:(i + 1) * size[1]]
                # converting (-1, 1) to (0, 1)
                row = [(p + 1) // 2 for p in row] 
                f.write(" ".join(map(str, row)) + "\n")
    
    except IOError as e:
        print(f"Error writing to file")

# loading pbm files from dataset directory
def load_pbm_dataset(directory):
    # get a list of all pbm files in directory
    pbm_files = [f for f in os.listdir(directory) if f.endswith('.pbm')]
    patterns = []
    # loop through each pbm file in directory
    for file in pbm_files:
        # join directory path with filename, creating full path name
        file_path = os.path.join(directory, file)
        # append pbm data (flattened binary matrix) to patterns (2D list)
        patterns.append(read_pbm(file_path))
    
    return patterns

# IT'S ALIVE!!!
def hebbian_learning(patterns):
    """Training Hopfield Network using Hebbian Learning"""
    num_neurons = len(patterns[0])
    
    # initializing all weights to 0
    weight_matrix = [[0 for _ in range(num_neurons)] for _ in range(num_neurons)]

    # taking each flattened matrix from patterns
    for pattern in patterns:
        # changing (0,1) to (-1, 1) 
        # i.e. implementing bipolar values
        bipolar_pattern = [(2 * p - 1) for p in pattern]

        # iterating over each neuron
        for i in range(num_neurons):
            for j in range(num_neurons):
                # w(i, i) remains 0, all other weights are updated
                if i != j:
                    # hebbian learning rule
                    weight_matrix[i][j] += bipolar_pattern[i] * bipolar_pattern[j]
    
    return weight_matrix

# corrupting memory either by:
# flipping pixels with probability p,
# or using a bounding box and flipping all pixels outside that box
# switch input parameter method to crop if you want to use cropping method of corruption
# default bounding box size is 10x10
# default probability of flipping is 0.3
def corrupt_memory(memory, p=0.3, method='flip', box_size=(10, 10)):
    
    # creating a copy of pbm file
    corrupted = memory[:]

    # corrupting by flipping pixels
    if method == 'flip':
        # iterating through each pixel 
        for i in range(len(corrupted)):
            # flipping with probability p
            if random.random() < p:
                corrupted[i] = 1 - corrupted[i]
    
    # corrupting by cropping
    elif method == 'crop':
        width, height = 16, 16
        
        # centering the bounding box
        x = (width - box_size[0]) // 2
        y = (height - box_size[1]) // 2
        
        for i in range(height):
            for j in range(width):
                # setting everything outside bounding box to black (0)
                if not (y <= i < y + box_size[0] and x <= j < x + box_size[1]):
                    corrupted[i * width + j] = 0
    
    return corrupted
