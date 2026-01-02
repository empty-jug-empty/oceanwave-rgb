import time
import sys
import numpy as np

# Hardware Dependency: Adafruit Blinka Piomatter for Pi 5
try:
    import adafruit_blinka_raspberry_pi5_piomatter as piomatter
except ImportError:
    print("Error: adafruit_blinka_raspberry_pi5_piomatter library is required.")
    sys.exit(1)

# --- 1. Linear Algebra Setup: The Basis of the Ocean ---
# We define our state space in R^4096 (64x64 grid)
size = 64
pixels = size * size
x_coord = np.linspace(0, 1, size)
y_coord = np.linspace(0, 1, size)
X, Y = np.meshgrid(x_coord, y_coord)

# Define the Column Space of A
# These 4 vectors form the basis for our ocean simulation.
# Any wave state 'b' will be a linear combination: b = Ax
v1 = np.sin(2 * np.pi * X).flatten()   # Basis 1: Low-Freq Horizontal
v2 = np.sin(10 * np.pi * X).flatten()  # Basis 2: High-Freq Horizontal
v3 = np.sin(2 * np.pi * Y).flatten()   # Basis 3: Low-Freq Vertical
v4 = np.sin(10 * np.pi * Y).flatten()  # Basis 4: High-Freq Vertical

# Matrix A (4096 rows x 4 columns)
A = np.column_stack((v1, v2, v3, v4))

def generate_ocean_state(weights):
    """
    Computes the matrix-vector product Ax = b.
    x: weights (4-dimensional vector)
    b: ocean height map (4096-dimensional vector)
    """
    b = A @ weights
    return b.reshape((size, size))

# --- 2. Hardware Configuration: Adafruit Bonnet (Pi 5 / Piomatter) ---
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 64

# Initialize Geometry
# n_addr_lines=5 is required for 64x64 panels (1/32 scan)
geometry = piomatter.Geometry(
    width=DISPLAY_WIDTH,
    height=DISPLAY_HEIGHT,
    n_addr_lines=5, 
    rotation=piomatter.Orientation.Normal
)

# Create a framebuffer (Shared memory with the hardware)
# The library expects (H, W, 3) uint8 array for RGB888Packed
framebuffer = np.zeros((DISPLAY_HEIGHT, DISPLAY_WIDTH, 3), dtype=np.uint8)

# Initialize the matrix
matrix = piomatter.PioMatter(
    geometry=geometry,
    pinout=piomatter.Pinout.AdafruitMatrixBonnet,
    colorspace=piomatter.Colorspace.RGB888Packed,
    framebuffer=framebuffer
)

# --- 3. Vectorized Color Mapping (Engineering Rigor) ---
# We map the scalar field 'b' (height) to R^3 (Color Space)
# Define color basis vectors for interpolation
DEEP_BLUE = np.array([0, 0, 50], dtype=np.float32)
CREST_WHITE = np.array([100, 150, 255], dtype=np.float32)

def scalar_field_to_rgb(field):
    """
    Maps wave heights to RGB colors using vectorized NumPy operations.
    Avoids Python loops for performance on the Pi's ARM CPU.
    """
    # Normalize field from [-2, 2] to [0, 1]
    # We clip to ensure we stay within bounds even if waves get wild
    normalized = np.clip((field + 2) / 4.0, 0, 1)
    
    # Broadcasting: (64, 64, 1) * (3,) -> (64, 64, 3)
    # Linear Interpolation: Color = Deep + t * (Crest - Deep)
    # This is effectively a projection into Color Space
    delta = CREST_WHITE - DEEP_BLUE
    rgb_data = DEEP_BLUE + (normalized[..., np.newaxis] * delta)
    
    return rgb_data.astype(np.uint8)

# --- 4. Real-Time Simulation Loop ---
print("Starting Ocean Wave Simulation on RGB Matrix (Piomatter)...")
print("Press Ctrl+C to stop.")

try:
    t = 0.0
    dt = 0.1
    
    while True:
        start_time = time.time()
        
        # Dynamic weights x(t)
        # Changing the coefficients of our linear combination
        current_weights = np.array([
            1.5 * np.cos(t),       # v1
            0.5 * np.sin(t * 2),   # v2
            0.3 * np.cos(t * 0.5), # v3
            0.2                    # v4
        ])
        
        # 1. Compute the state b = Ax
        wave_heights = generate_ocean_state(current_weights)
        
        # 2. Map to RGB Space
        rgb_array = scalar_field_to_rgb(wave_heights)
        
        # 3. Push to Hardware
        # Copy the calculated RGB data into the framebuffer
        # The shapes must match: (64, 64, 3)
        framebuffer[:] = rgb_array
        matrix.show()
        
        # Time step
        t += dt
        
        # Frame pacing
        elapsed = time.time() - start_time
        # Optional: print(f"FPS: {1/elapsed:.1f}")

except KeyboardInterrupt:
    print("\nExiting...")
    framebuffer.fill(0)
    matrix.show()
