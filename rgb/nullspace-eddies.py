import time
import sys
import numpy as np

# ============================================================================
# NULLSPACE EDDIES — Ax = 0  (Strang Ch. 3)
# ============================================================================
# RGB DIGITAL TWIN of math/nullspace-eddies.py
#
# The linear algebra is IDENTICAL — only the output layer changes:
#   math/ version  →  matplotlib (laptop)
#   rgb/  version  →  piomatter  (Pi 5 + 64×64 LED matrix)
#
# N(A) = { x : Ax = 0 }  is a SUBSPACE.
#
# For each eddy we build TWO basis vectors: sₖᴬ and sₖᴮ (90° apart).
# The combination  x(t) = cos(ωt)·sₖᴬ + sin(ωt)·sₖᴮ
# traces a CIRCLE in the Nullspace → visible rotation on the board.
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


# ── NULLSPACE BASIS VECTORS ─────────────────────────────────────────────────

def make_vortex_pair(center_r, center_c, radius, clockwise=True):
    """
    Build a PAIR of nullspace basis vectors for one eddy.

    Both are divergence-free loops (Ax = 0).
    They are 90° apart, so cos/sin mixing produces visible rotation.

    Returns (uA, vA), (uB, vB) — each is (N, N).
    """
    dr = rr - center_r
    dc = cc - center_c
    dist = np.sqrt(dr**2 + dc**2) + 1e-8

    # Ring-shaped envelope: peaks at r = radius, fades outside
    envelope = (dist / radius) * np.exp(-(dist**2) / (2 * radius**2))

    # Normalised direction vectors
    dr_hat = dr / dist
    dc_hat = dc / dist

    # Phase A: tangential flow (perpendicular to radius)
    uA = -dc_hat * envelope
    vA =  dr_hat * envelope

    # Phase B: rotated 90° → orthogonal partner
    uB =  dr_hat * envelope
    vB =  dc_hat * envelope

    sign = -1.0 if clockwise else 1.0
    uA, vA = sign * uA, sign * vA
    uB, vB = sign * uB, sign * vB

    return (uA, vA), (uB, vB)


# s₁: Large CLOCKWISE eddy — center
(u1a, v1a), (u1b, v1b) = make_vortex_pair(32, 32, 14, clockwise=True)

# s₂: Small COUNTER-CLOCKWISE eddy — top-left corner
(u2a, v2a), (u2b, v2b) = make_vortex_pair(14, 14, 8, clockwise=False)

# s₃: Small COUNTER-CLOCKWISE eddy — bottom-right corner
(u3a, v3a), (u3b, v3b) = make_vortex_pair(50, 50, 8, clockwise=False)


# ── FLATTEN TO COLUMN VECTORS: sₖ ∈ ℝ^{4096×1} ────────────────────────────

def to_col(grid):
    """Flatten (64,64) grid → strict column vector (4096,1)."""
    return grid.flatten().reshape(-1, 1)

# Phase A vectors
s1a_u, s1a_v = to_col(u1a), to_col(v1a)
s2a_u, s2a_v = to_col(u2a), to_col(v2a)
s3a_u, s3a_v = to_col(u3a), to_col(v3a)

# Phase B vectors (90° rotated partners)
s1b_u, s1b_v = to_col(u1b), to_col(v1b)
s2b_u, s2b_v = to_col(u2b), to_col(v2b)
s3b_u, s3b_v = to_col(u3b), to_col(v3b)

# Normalise each pair so peak speed = 1
all_pairs = [
    (s1a_u, s1a_v, s1b_u, s1b_v),
    (s2a_u, s2a_v, s2b_u, s2b_v),
    (s3a_u, s3a_v, s3b_u, s3b_v),
]
for (au, av, bu, bv) in all_pairs:
    peak = max(np.max(np.abs(au)), np.max(np.abs(av)),
               np.max(np.abs(bu)), np.max(np.abs(bv)))
    au /= peak; av /= peak; bu /= peak; bv /= peak


# ── COLOR MAPPING ───────────────────────────────────────────────────────────
# Identical angle→hue logic, but output is uint8 (0–255) for the LED matrix.

def angle_to_rgb_uint8(u, v):
    """
    Representation Layer Bridge (Hardware):
        Column vectors (4096,1) → reshape(64,64) → grid.
        Row-major order: pixel (r,c) = index 64r + c.

    Color:  angle of (u, v) → hue,  magnitude → brightness.
    Output: (64, 64, 3) uint8 array ready for the framebuffer.
    """
    u2d = u.reshape(N, N)
    v2d = v.reshape(N, N)

    angle = np.arctan2(v2d, u2d)             # −π to π
    mag = np.sqrt(u2d**2 + v2d**2)
    mag = mag / (np.max(mag) + 1e-8)         # normalise to [0, 1]

    # Hue from angle
    hue = (angle + np.pi) / (2 * np.pi)      # [0, 1]

    # HSV to RGB (S=1, V=magnitude)
    rgb = np.zeros((N, N, 3))
    h6 = hue * 6.0
    sector = h6.astype(int) % 6
    frac = h6 - np.floor(h6)

    p = 0.0
    q = mag * (1.0 - frac)
    t = mag * frac

    for s_val, (r_val, g_val, b_val) in enumerate([
        (mag, t,   p),    # sector 0
        (q,   mag, p),    # sector 1
        (p,   mag, t),    # sector 2
        (p,   q,   mag),  # sector 3
        (t,   p,   mag),  # sector 4
        (mag, p,   q),    # sector 5
    ]):
        mask = (sector == s_val)
        rgb[mask, 0] = r_val[mask] if isinstance(r_val, np.ndarray) else r_val
        rgb[mask, 1] = g_val[mask] if isinstance(g_val, np.ndarray) else g_val
        rgb[mask, 2] = b_val[mask] if isinstance(b_val, np.ndarray) else b_val

    # Scale to 0–255 with brightness cap, convert to uint8
    return (np.clip(rgb, 0, 1) * 255 * BRIGHTNESS).astype(np.uint8)


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
#   x(t) = Σₖ [ cos(ωₖt)·sₖᴬ + sin(ωₖt)·sₖᴮ ]   ∈ N(A)

print("Starting Nullspace Eddies — orbiting in N(A)")
print("Press Ctrl+C to stop")

frame = 0
try:
    while True:
        start_time = time.time()

        t = frame * 0.04

        # Time-varying coefficients (identical to math/ version)
        c1a, c1b = 0.7 * np.cos(0.8 * t), 0.7 * np.sin(0.8 * t)
        c2a, c2b = 0.5 * np.cos(1.5 * t), 0.5 * np.sin(1.5 * t)
        c3a, c3b = 0.5 * np.cos(2.1 * t), 0.5 * np.sin(2.1 * t)

        # ── NULLSPACE ORBIT ─────────────────────────────────────────────
        x_u = (c1a*s1a_u + c1b*s1b_u
             + c2a*s2a_u + c2b*s2b_u
             + c3a*s3a_u + c3b*s3b_u)

        x_v = (c1a*s1a_v + c1b*s1b_v
             + c2a*s2a_v + c2b*s2b_v
             + c3a*s3a_v + c3b*s3b_v)

        # Representation Layer: column vectors → RGB → framebuffer
        framebuffer[:] = angle_to_rgb_uint8(x_u, x_v)
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
