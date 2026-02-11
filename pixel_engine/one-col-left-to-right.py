import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 1. THE SPACE: 64x64 Grid
N = 64
dim = N * N  # 4,096 dimensions

# 2. CREATE THE SHIFT MATRIX (P)
# First, create a 64x64 shift for a single row
row_shift = np.eye(N)

row_shift = np.roll(row_shift, 1, axis=0) # Shift the 1s one position

# Now, build the 4096x4096 matrix A
# This is a "Block Diagonal" matrix: it applies the row_shift to every row
A = np.zeros((dim, dim))
for i in range(N):
    A[i*N : (i+1)*N, i*N : (i+1)*N] = row_shift

# 3. INITIAL STATE (Vector x): A Color Gradient
# Instead of a single line, we fill the grid so every column has a unique value (0.0 to 1.0)
x_grid = np.zeros((N, N))
for col in range(N):
    # Assign a value based on the column index
    # Column 0 = 0.0 (Black/Purple), Column 63 = 1.0 (Red/White)
    x_grid[:, col] = col / N 

x = x_grid.flatten().reshape(-1, 1)  # Shape: (4096, 1) - explicit column vector
x = (A @ x).flatten()  # Result is also (4096, 1), then flatten for next iteration # Flatten to 4,096-dimensional vector

# 4. ANIMATION: b = Ax
fig, ax = plt.subplots()
# Use 'nipy_spectral' or 'jet' to see distinct colors for every column value
img = ax.imshow(x.reshape(N, N), cmap='jet') 

def update(frame):
    global x
    x = A @ x  # THE LINEAR ALGEBRA ACTION: Apply the permutation
    img.set_array(x.reshape(N, N))
    return [img]

ani = FuncAnimation(fig, update, frames=64, interval=100, blit=True)
plt.title("Movement as Matrix Multiplication (Ax)")
plt.show()