import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================================
# NULLSPACE: THE RUNNING CIRCLE  —  Ax = 0
# ============================================================================
#
# QUESTION: How can flow move if the equation is Ax = 0 (Total Balance)?
# ANSWER:   It moves in a LOOP.
#
# The Nullspace contains every possible loop.
# Here we build one simple circle in the center.
#
# MATH:
#   We build two static basis vectors s₁ and s₂ in the Nullspace.
#     s₁ = Ring bright at 3 o'clock
#     s₂ = Ring bright at 12 o'clock
#
#   Then we mix them linearly:
#     x(t) = cos(t)·s₁ + sin(t)·s₂
#
#   Result: A bright spot that ORBITS the center.
# ============================================================================

N = 64
dim = N * N

# ── 1. THE MATH: BUILD THE BASIS VECTORS ────────────────────────────────────
# We need coordinate grids to calculate angles and distances
cc, rr = np.meshgrid(np.arange(N), np.arange(N))

# Define the circle geometry
center = 32
radius = 16
dr = rr - center
dc = cc - center
angle = np.arctan2(dr, dc)
dist = np.sqrt(dr**2 + dc**2)

# Create the ring shape (Gaussian thickness)
ring_shape = np.exp(-((dist - radius)**2) / (2 * 2.0**2))

# Create the two basis vectors (Static snapshots)
# s1: Bright spot at angle 0 (Right/3 o'clock)
grid_s1 = ring_shape * np.cos(angle)

# s2: Bright spot at angle 90 (Top/12 o'clock)
grid_s2 = ring_shape * np.sin(angle)

# Flatten to strict Column Vectors (Dimensions: 4096 x 1)
# These are our "Special Solutions" to Ax=0
s1 = grid_s1.flatten().reshape(-1, 1)
s2 = grid_s2.flatten().reshape(-1, 1)


# ── 2. THE ANIMATION ────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_title("One Moving Solution in the Nullspace")
img = ax.imshow(np.zeros((N, N, 3)))

def update(frame):
    # FIX: Map 200 frames to exactly 3 full circles (3 * 2π).
    # This prevents the visual jump/glitch when the loop restarts.
    total_frames = 200
    cycles = 3
    t = (frame / total_frames) * (cycles * 2 * np.pi)

    # LINEAR COMBINATION
    # We are just adding two vectors. That's it.
    # Because s1 and s2 are in Nullspace, x is in Nullspace.
    x = np.cos(t) * s1 + np.sin(t) * s2

    # ── REPRESENTATION LAYER ──────────────────────────
    # Map the vector x back to the 64x64 grid
    grid = x.reshape(N, N)

    # Visualization: Red ring
    rgb = np.zeros((N, N, 3))
    # We use absolute value so the "negative" side of the wave is also visible
    rgb[:, :, 1] = np.clip(grid + 0.2, 0, 1) # Red channel

    img.set_array(rgb)
    return [img]

ani = FuncAnimation(fig, update, frames=200, interval=20, blit=True)
plt.show()
