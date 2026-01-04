import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 1. THE SPACE: 64x64 Grid
N = 64
dim = N * N  # 4,096 dimensions

I_block = np.eye(N)
# Now, build the 4096x4096 matrix A
# This is a "Block Diagonal" matrix: it applies the row_shift to every row
A = np.zeros((dim, dim))
for i in range(N):
    # We want: Row_i(new) = Row_{i-1}(old)
    # In Matrix terms: Block[i, i-1] = I
    
    row_idx = i
    col_idx = (i - 1) % N # Wrap around: Row 0 gets data from Row 63
    
    # Place the Identity block
    A[row_idx*N : (row_idx+1)*N, col_idx*N : (col_idx+1)*N] = I_block


# 3. INITIAL STATE (Vector x): A vertical line (wave front)
x_grid = np.zeros((N, N))
x_grid[0, :] = 1.0   # Start with a line at column 5
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