import time
import sys
import numpy as np
import matplotlib.cm

# Hardware Import
try:
    import adafruit_blinka_raspberry_pi5_piomatter as piomatter
except ImportError:
    print("Error: adafruit_blinka_raspberry_pi5_piomatter library is required.")
    sys.exit(1)

# ==========================================
# 1. LINEAR ALGEBRA SETUP (The Math)
# ==========================================
N = 64
dim = N * N  # 4,096 dimensions

# Create the Shift Matrix (S) for a single row
# We want to shift columns RIGHT (axis=0 in roll logic for the row vector)
row_shift = np.eye(N)
row_shift = np.roll(row_shift, 1, axis=0) 

# Build the Block Diagonal Matrix A (4096 x 4096)
# This applies the shift to every row independently
print("Building Matrix A (4096 x 4096)...")
A = np.zeros((dim, dim))
for i in range(N):
    A[i*N : (i+1)*N, i*N : (i+1)*N] = row_shift

# Initial State (Vector x): A Color Gradient
# Column 0 = 0.0, Column 63 = 1.0
x_grid = np.zeros((N, N))
for col in range(N):
    x_grid[:, col] = col / N 

x = x_grid.flatten() # The state vector

# ==========================================
# 2. HARDWARE SETUP (The Physics)
# ==========================================
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 64

geometry = piomatter.Geometry(
    width=DISPLAY_WIDTH,
    height=DISPLAY_HEIGHT,
    n_addr_lines=5, 
    rotation=piomatter.Orientation.Normal
)

framebuffer = np.zeros((DISPLAY_HEIGHT, DISPLAY_WIDTH, 3), dtype=np.uint8)

matrix = piomatter.PioMatter(
    geometry=geometry,
    pinout=piomatter.Pinout.AdafruitMatrixBonnet,
    colorspace=piomatter.Colorspace.RGB888Packed,
    framebuffer=framebuffer
)

# Helper to convert Math (0.0-1.0) to RGB (0-255)
# We use the 'jet' colormap to match your simulation
colormap = matplotlib.colormaps['jet']

def scalar_to_rgb(grid_2d):
    """
    Takes a 64x64 grid of floats (0.0-1.0)
    Returns a 64x64x3 grid of uint8s
    """
    # cmap returns (64, 64, 4) -> RGBA floats
    rgba = colormap(grid_2d) 
    # Drop Alpha, scale to 255, convert to uint8
    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
    return rgb

# ==========================================
# 3. THE LOOP (Ax = b)
# ==========================================
print("Starting Simulation: x_new = A @ x_old")
print("Press Ctrl+C to stop")

try:
    while True:
        start_time = time.time()

        # A. The Linear Algebra Step
        # Note: Matrix multiplication of 4096^2 is heavy! 
        # On Pi 5, this emphasizes the cost of O(N^2) operations.
        x = A @ x

        # B. The Projection Step (Vector -> Image)
        current_grid = x.reshape(N, N)
        
        # C. The Rendering Step (Image -> Hardware)
        rgb_data = scalar_to_rgb(current_grid)
        framebuffer[:] = rgb_data
        matrix.show()

        # Frame pacing
        # Calculate how long the math took
        dt = time.time() - start_time
        # print(f"FPS: {1.0/dt:.1f}") # Uncomment to check performance

except KeyboardInterrupt:
    print("\nStopping...")
    framebuffer.fill(0)
    matrix.show()