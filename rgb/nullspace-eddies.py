import time
import sys
import numpy as np

# ============================================================================
# NULLSPACE: TWO RUNNING CIRCLES  —  Ax = 0  (Strang Ch. 3)
# ============================================================================
# RGB DIGITAL TWIN of math/nullspace-eddies.py
#
# The linear algebra is IDENTICAL — only the output layer changes:
#   math/ version  →  matplotlib (laptop)
#   rgb/  version  →  piomatter  (Pi 5 + 64×64 LED matrix)
#
# THE ONE IDEA:
#   N(A) is a SUBSPACE.  If s₁, s₂ ∈ N(A), then
#       x(t) = cos(ωt)·s₁ + sin(ωt)·s₂   is ALSO in N(A).
#
#   cos(ωt)·s₁ + sin(ωt)·s₂ = ring · cos(θ − ωt)  →  a spot that ORBITS
#
# Two circles: Blue = big center loop, Red = small corner loop.
#
# GEOMETRY: 64×64 grid, row-major.  Pixel (r,c) → index 64r + c.
# ============================================================================

# ── 0. CONFIGURATION ───────────────────────────────────────────────────────
TARGET_FPS = 25       # Frame rate on the LED matrix
BRIGHTNESS = 0.4      # Scalar 0.0–1.0  (keep ≤0.5 to avoid high current)

# ── Hardware Import ─────────────────────────────────────────────────────────
try:
    import adafruit_blinka_raspberry_pi5_piomatter as piomatter
except ImportError:
    print("Error: adafruit_blinka_raspberry_pi5_piomatter library is required.")
    print("This script is meant for the Raspberry Pi 5 + RGB Matrix.")
    sys.exit(1)

# ── 1. LINEAR ALGEBRA SETUP (identical to math/nullspace-eddies.py) ────────
N = 64
dim = N * N  # 4096

# Coordinate grids
cc, rr = np.meshgrid(np.arange(N, dtype=float), np.arange(N, dtype=float))


# ── BUILD BASIS VECTORS FOR ONE RING ────────────────────────────────────────

def make_ring_pair(center_r, center_c, radius, width=3.0):
    """
    Build TWO nullspace basis vectors for a running circle.

    s₁ = ring · cos(θ)   — bright at 3 o'clock
    s₂ = ring · sin(θ)   — bright at 12 o'clock

    The ring is a Gaussian annulus: bright at distance=radius, fades away.
    Width controls how thick the ring is.

    Returns s_cos, s_sin as column vectors (4096, 1).
    """
    dr = rr - center_r
    dc = cc - center_c
    dist = np.sqrt(dr**2 + dc**2)
    theta = np.arctan2(dr, dc)            # angle around center

    # Ring envelope: peaks at dist == radius
    ring = np.exp(-((dist - radius)**2) / (2 * width**2))

    # Two basis vectors: same ring, 90° apart
    grid_cos = ring * np.cos(theta)       # bright at 3 o'clock
    grid_sin = ring * np.sin(theta)       # bright at 12 o'clock

    # Flatten to strict column vectors (4096, 1)
    s_cos = grid_cos.flatten().reshape(-1, 1)
    s_sin = grid_sin.flatten().reshape(-1, 1)

    # Normalise so peak = 1
    peak = max(np.max(np.abs(s_cos)), np.max(np.abs(s_sin)))
    s_cos /= peak
    s_sin /= peak

    return s_cos, s_sin


# ── Circle 1: BIG loop in the center ───────────────────────────────────────
s1_cos, s1_sin = make_ring_pair(center_r=32, center_c=32, radius=16, width=4.0)

# ── Circle 2: SMALL loop in the top-right ──────────────────────────────────
s2_cos, s2_sin = make_ring_pair(center_r=16, center_c=48, radius=9, width=3.0)


# ── 2. HARDWARE SETUP ──────────────────────────────────────────────────────
print("Initializing 64×64 RGB Matrix...")

geometry = piomatter.Geometry(
    width=N,
    height=N,
    n_addr_lines=5,
    rotation=piomatter.Orientation.Normal,
)

framebuffer = np.zeros((N, N, 3), dtype=np.uint8)

matrix = piomatter.PioMatter(
    geometry=geometry,
    pinout=piomatter.Pinout.AdafruitMatrixBonnet,
    colorspace=piomatter.Colorspace.RGB888Packed,
    framebuffer=framebuffer,
)

# ── 3. THE LOOP ────────────────────────────────────────────────────────────
# Same update logic as math/nullspace-eddies.py:
#   circle(t) = cos(ωt)·s_cos + sin(ωt)·s_sin   ∈ N(A)

print("Starting Two Running Circles in the Nullspace (Ax = 0)")
print("Press Ctrl+C to stop")

frame = 0
try:
    while True:
        start_time = time.time()

        t = frame * 0.06

        # ── NULLSPACE LINEAR COMBINATION ────────────────────────────────
        # Circle 1: clockwise
        x1 = np.cos(1.0 * t) * s1_cos + np.sin(1.0 * t) * s1_sin

        # Circle 2: counter-clockwise (flip sin → minus)
        x2 = np.cos(1.8 * t) * s2_cos - np.sin(1.8 * t) * s2_sin

        # ── REPRESENTATION LAYER ────────────────────────────────────────
        # Column vectors (4096,1) → reshape to 64×64 → RGB uint8
        spot1 = np.clip(x1.reshape(N, N), 0, 1)
        spot2 = np.clip(x2.reshape(N, N), 0, 1)

        framebuffer[:, :, 0] = (spot2 * 255 * BRIGHTNESS).astype(np.uint8)  # Red
        framebuffer[:, :, 1] = 0                                             # Green
        framebuffer[:, :, 2] = (spot1 * 255 * BRIGHTNESS).astype(np.uint8)  # Blue
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
    print("Display cleared.")
