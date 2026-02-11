import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================================
# THE MATH: Permutation Matrix for Vertical Motion
# ============================================================================
# Goal: Move rows downward using matrix multiplication
#       Row_i(new) = Row_{i-1}(old)
#       Row 0 wraps around from Row 63
#
# Mathematical Framework (Strang Ch. 2):
#   - A ∈ ℝ^{4096×4096}: Block off-diagonal permutation matrix
#   - x ∈ ℝ^{4096×1}: Column vector (strict convention)
#   - b = Ax: Linear transformation in 4096-dimensional space
#
# THE GEOMETRY: 64×64 Grid → ℝ^{4096}
#   - Flatten grid row-major: [Row0_pixels, Row1_pixels, ..., Row63_pixels]
#   - Each row = 64 consecutive elements in the vector
# ============================================================================

# 1. THE SPACE: 64x64 Grid
N = 64
dim = N * N  # 4,096 dimensions

# 2. BUILD THE PERMUTATION MATRIX A (Block Off-Diagonal Structure)
# Each block is a 64×64 identity matrix
I_block = np.eye(N)

# Initialize the transformation matrix
A = np.zeros((dim, dim))

for i in range(N):
    # Block placement: Row_i ← Row_{i-1}
    # In terms of 4096-vector indices:
    #   Elements [i*64 : (i+1)*64] ← Elements [(i-1)*64 : i*64]
    
    row_block_idx = i
    col_block_idx = (i - 1) % N  # Wrap: Row 0 gets Row 63
    
    # Place identity block at off-diagonal position
    A[row_block_idx*N : (row_block_idx+1)*N, 
      col_block_idx*N : (col_block_idx+1)*N] = I_block

# 3. INITIAL STATE: x ∈ ℝ^{4096×1} (Explicit Column Vector)
# Start with a horizontal line at the top row
x_grid = np.zeros((N, N))
x_grid[0, :] = 1.0  # Horizontal line at row 0

# STRICT COLUMN VECTOR: x ∈ ℝ^{4096×1}
x = x_grid.flatten().reshape(-1, 1)  # Shape: (4096, 1)

# 4. ANIMATION: Visualize b = Ax
fig, ax = plt.subplots()
img = ax.imshow(x.reshape(N, N), cmap='ocean')

def update(frame):
    global x
    # MATRIX-VECTOR MULTIPLICATION: b = Ax
    # A: (4096, 4096) @ x: (4096, 1) = b: (4096, 1)
    x = A @ x  # x remains a column vector throughout
    img.set_array(x.reshape(N, N))
    return [img]

ani = FuncAnimation(fig, update, frames=64, interval=50, blit=True)
plt.title("Vertical Motion as Block Permutation (Ax)")
plt.show()