import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================================
# NULLSPACE: TWO RUNNING CIRCLES  —  Ax = 0  (Strang Ch. 3)
# ============================================================================
#
# THE ONE IDEA:
#   N(A) is a SUBSPACE.  If s₁, s₂ ∈ N(A), then
#       x(t) = cos(ωt)·s₁ + sin(ωt)·s₂   is ALSO in N(A).
#
# WHY A LOOP IS IN THE NULLSPACE:
#   A loop = flow goes around and comes back.
#   Nothing accumulates at any node → Ax = 0.
#
# WHAT YOU SEE:
#   A bright spot running around a ring.
#   That motion comes from two STATIC basis vectors
#     s₁ = ring · cos(θ)    (bright at 3 o'clock)
#     s₂ = ring · sin(θ)    (bright at 12 o'clock)
#   combined with cos/sin coefficients:
#
#     cos(ωt)·s₁ + sin(ωt)·s₂ = ring · cos(θ − ωt)
#                                        ^^^^^^^^^^
#                                    a spot that ORBITS
#
# TWO CIRCLES:
#   Blue = big loop in the center (clockwise)
#   Red  = small loop in the corner (counter-clockwise)
#   Both are in N(A).  Their sum is in N(A).  Always.
#
# GEOMETRY: 64×64 grid, row-major.  Pixel (r,c) → index 64r + c.
# ============================================================================

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


# ── ANIMATION ───────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_title("Two Running Circles in the Nullspace (Ax = 0)")
ax.set_xlabel("Column (c)")
ax.set_ylabel("Row (r)")

img = ax.imshow(np.zeros((N, N, 3)), interpolation='nearest')


def update(frame):
    """
    Each frame:
      circle₁(t) = cos(ω₁t)·s₁_cos + sin(ω₁t)·s₁_sin   (clockwise)
      circle₂(t) = cos(ω₂t)·s₂_cos − sin(ω₂t)·s₂_sin   (counter-clockwise)

    Both are in N(A).  Their sum is in N(A).
    The subspace property does ALL the work.
    """
    t = frame * 0.06

    # ── NULLSPACE LINEAR COMBINATION ────────────────────────────────────
    # Circle 1: clockwise
    x1 = np.cos(1.0 * t) * s1_cos + np.sin(1.0 * t) * s1_sin

    # Circle 2: counter-clockwise (flip sin → minus)
    x2 = np.cos(1.8 * t) * s2_cos - np.sin(1.8 * t) * s2_sin

    # ── REPRESENTATION LAYER ────────────────────────────────────────────
    # Column vectors (4096,1) → reshape to 64×64 → RGB
    spot1 = np.clip(x1.reshape(N, N), 0, 1)   # only positive half = lit
    spot2 = np.clip(x2.reshape(N, N), 0, 1)

    rgb = np.zeros((N, N, 3))
    rgb[:, :, 2] = spot1    # Blue  = circle 1
    rgb[:, :, 0] = spot2    # Red   = circle 2

    img.set_array(rgb)
    return [img]


ani = FuncAnimation(fig, update, frames=600, interval=40, blit=True)
plt.tight_layout()
plt.show()
