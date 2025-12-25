import numpy as np
import matplotlib.pyplot as plt

# 1. THE SPACE: 128x64 Grid
ROWS, COLS = 64, 128
N = ROWS * COLS

# 2. THE VECTOR v: A Simple Sine Wave (Chapter 1)
x = np.linspace(0, 4 * np.pi, COLS)
# Create one row of a sine wave and tile it 64 times
single_row = np.sin(x)
# Reshape to (N, 1) to be a proper Column Vector
v = np.tile(single_row, ROWS).reshape(N, 1)

# 3. THE OPERATOR S: The Shift Matrix (Chapter 2.4)
# We use np.roll for efficiency, but mathematically it is Sv
def move_right(vector, pixels=1):
    # This is the equivalent of multiplying by S^pixels
    # We reshape to grid for the operation, but input/output are column vectors
    grid = vector.reshape((ROWS, COLS))
    shifted_grid = np.roll(grid, shift=pixels, axis=1)
    return shifted_grid.reshape(N, 1)

# 4. MANIPULATION: Scaling and Addition (Linear Combination)
v_half_speed = move_right(v, 1)  # Shift 1 pixel
v_double_height = 0.1 * v        # Scale (Chapter 2.1)

# 5. THE DIGITAL TWIN: Matplotlib Visualization
def show_ocean(vector, title):
    plt.figure(figsize=(10, 5))
    plt.imshow(vector.reshape((ROWS, COLS)), cmap='ocean')
    plt.title(title)
    plt.axis('on')
    plt.show()

# Visualize the initial state
show_ocean(v, "Original Wave (v)")

# Visualize movement (The result of matrix-vector multiplication)
v_moved = move_right(v, 5)
show_ocean(v_moved, "The Wave After 10 Shifts (S^10 v)")

show_ocean(v_double_height, "half Height Wave (0.5 v)")