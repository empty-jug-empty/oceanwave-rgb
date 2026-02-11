import time
import sys
import numpy as np

# ============================================================================
# NULLSPACE: THE RUNNING CIRCLE  —  Ax = 0
# ============================================================================
# RGB DIGITAL TWIN of math/nullspace-eddies.py
#
# QUESTION: How can flow move if the equation is Ax = 0 (Total Balance)?
# ANSWER:   It moves in a LOOP.
#
# The Nullspace contains every possible loop.
# Here we build one simple circle in the center.
#
# MATCHING LOGIC:
#   1. Static basis vectors (s1, s2) = Ring at 3 o'clock & 12 o'clock.
#   2. Dynamic state x(t) = cos(t)s1 + sin(t)s2
#   3. Result = Orbiting bright spot.
#
# GEOMETRY: 64×64 grid, row-major.  Pixel (r,c) → index 64r + c.
# ============================================================================

# ── 0. CONFIGURATION ───────────────────────────────────────────────────────
TARGET_FPS = 30       # Smooth motion
BRIGHTNESS = 0.5      # Scalar 0.0–1.0

# ── Hardware Import ─────────────────────────────────────────────────────────
try:
    import adafruit_blinka_raspberry_pi5_piomatter as piomatter
except ImportError:
    print("Error: adafruit_blinka_raspberry_pi5_piomatter library is required.")
    sys.exit(1)

# ── 1. LINEAR ALGEBRA SETUP ────────────────────────────────────────────────
N = 64

# Coordinate grids
cc, rr = np.meshgrid(np.arange(N, dtype=float), np.arange(N, dtype=float))

# Define the circle geometry
center = 32
radius = 16
dr = rr - center
dc = cc - center
angle = np.arctan2(dr, dc)
dist = np.sqrt(dr**2 + dc**2)

# Create the ring shape (Gaussian thickness)
ring_shape = np.exp(-((dist - radius)**2) / (2 * 2.0**2))

# Flatten basis vectors
grid_s1 = ring_shape * np.cos(angle)
grid_s2 = ring_shape * np.sin(angle)

s1 = grid_s1.flatten().reshape(-1, 1)
s2 = grid_s2.flatten().reshape(-1, 1)

# ── 2. HARDWARE SETUP ──────────────────────────────────────────────────────
print("Initializing 64×64 RGB Matrix...")

geometry = piomatter.Geometry(
    width=N, height=N, n_addr_lines=5, rotation=piomatter.Orientation.Normal
)
framebuffer = np.zeros((N, N, 3), dtype=np.uint8)
matrix = piomatter.PioMatter(
    geometry=geometry,
    pinout=piomatter.Pinout.AdafruitMatrixBonnet,
    colorspace=piomatter.Colorspace.RGB888Packed,
    framebuffer=framebuffer,
)

# ── 3. THE LOOP ────────────────────────────────────────────────────────────
print("Running Nullspace Loop... Press Ctrl+C to stop.")

frame = 0
try:
    while True:
        start_time = time.time()
        
        # Match speed of math file: 3 cycles over 200 frames
        # speed = (3 * 2π) / 200 ≈ 0.094 radians/frame
        t = frame * 0.094  

        # LINEAR COMBINATION (The core math)
        x = np.cos(t) * s1 + np.sin(t) * s2

        # REPRESENTATION LAYER
        grid = x.reshape(N, N)

        # 1. Separating the Signal
        #    Positive part (Crest) goes to Green
        #    Negative part (Trough) goes to Red (we flip sign to make it displayable)
        val_pos = np.maximum(grid, 0)
        val_neg = np.maximum(-grid, 0)

        # 2. Gamma Correction (Boost tails for both)
        val_pos = val_pos ** 0.6
        val_neg = val_neg ** 0.6
        
        # 3. Map to Colors
        #    Red Channel   = Negative Signal
        #    Green Channel = Positive Signal
        framebuffer[:, :, 0] = (val_neg * 255 * BRIGHTNESS).astype(np.uint8)
        framebuffer[:, :, 1] = (val_pos * 255 * BRIGHTNESS).astype(np.uint8)
        framebuffer[:, :, 2] = 0
        
        matrix.show()
        frame += 1

        # Frame pacing
        dt = time.time() - start_time
        sleep_time = (1.0 / TARGET_FPS) - dt
        if sleep_time > 0:
            time.sleep(sleep_time)

except KeyboardInterrupt:
    print("\nStopping...")
    framebuffer.fill(0)
    matrix.show()

