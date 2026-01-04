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

# 3. INITIAL STATE (Vector x): A vertical line (wave front)
x_grid = np.zeros((N, N))
x_grid[:,5] = 1.0  # Start with a line at column 5
x = x_grid.flatten() # Flatten to 4,096-dimensional vector

# 4. ANIMATION: b = Ax
fig, ax = plt.subplots()
img = ax.imshow(x.reshape(N, N), cmap='ocean')

def update(frame):
    global x
    x = A @ x  # THE LINEAR ALGEBRA ACTION: Apply the permutation
    img.set_array(x.reshape(N, N))
    return [img]

ani = FuncAnimation(fig, update, frames=64, interval=50, blit=True)
plt.title("Movement as Matrix Multiplication (Ax)")
plt.show()