import time
import sys
import numpy as np
import matplotlib.cm

# ==========================================
# 0. CONFIGURATION
# ==========================================
TARGET_FPS = 15      # Speed: How many steps per second
BRIGHTNESS = 0.5     # Brightness: Scalar 0.0 to 1.0

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

# Build the Permutation Matrix A (4096 x 4096)
# We want to shift rows DOWN.
# In block matrix terms, Row Block i comes from Row Block i-1.
print("Building Matrix A (4096 x 4096)...")
I_block = np.eye(N)
A = np.zeros((dim, dim))

for i in range(N):
    # Destination Block Row index
    dest_row = i
    # Source Block Row index (wrap around)
    src_row = (i - 1) % N
    
    # Place the Identity block to move the whole row of pixels
    # from src_row to dest_row
    A[dest_row*N : (dest_row+1)*N, src_row*N : (src_row+1)*N] = I_block

# Initial State (Vector x): A Vertical Color Gradient
# Row 0 = 0.0, Row 63 = 1.0
x_grid = np.zeros((N, N))
for row in range(N):
    x_grid[row, :] = row / N 

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
colormap = matplotlib.colormaps['jet']

def scalar_to_rgb(grid_2d):
    """
    Takes a 64x64 grid of floats (0.0-1.0)
    Returns a 64x64x3 grid of uint8s
    """
    # cmap returns (64, 64, 4) -> RGBA floats
    rgba = colormap(grid_2d) 
    # Drop Alpha, scale to 255, apply brightness scalar, convert to uint8
    rgb = (rgba[:, :, :3] * 255 * BRIGHTNESS).astype(np.uint8)
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
        x = A @ x

        # B. The Projection Step (Vector -> Image)
        current_grid = x.reshape(N, N)
        
        # C. The Rendering Step (Image -> Hardware)
        rgb_data = scalar_to_rgb(current_grid)
        framebuffer[:] = rgb_data
        matrix.show()

        # Frame pacing
        dt = time.time() - start_time
        sleep_time = (1.0 / TARGET_FPS) - dt
        if sleep_time > 0:
            time.sleep(sleep_time)

except KeyboardInterrupt:
    print("\nStopping...")
    framebuffer.fill(0)
    matrix.show()