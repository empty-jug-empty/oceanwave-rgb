import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================================
# THE MATH: Nullspace of a Flow-Conservation Matrix  —  Ax = 0
# ============================================================================
#
# Strang Ch. 3: The Nullspace N(A) is the set of all x satisfying Ax = 0.
#
# PHYSICS INTERPRETATION:
#   A encodes "Conservation of Mass" at every node of the 64×64 grid:
#       (flow in) − (flow out) = 0
#   Any solution x ∈ N(A) is a flow field where mass is perfectly conserved
#   everywhere.  Physically these solutions are *closed loops* — eddies,
#   vortices, circulation patterns where water spins but never accumulates.
#
# LINEARITY (Strang Ch. 3, §3.2):
#   If s₁, s₂, s₃ ∈ N(A), then ANY linear combination
#       x = c₁ s₁ + c₂ s₂ + c₃ s₃
#   is also in N(A).  (The nullspace is a subspace.)
#   We animate the coefficients c₁(t), c₂(t), c₃(t) with sine waves so the
#   eddies pulse, breathe, and interfere — yet Ax = 0 holds at every frame.
#
# THE GEOMETRY: 64×64 Grid → ℝ⁴⁰⁹⁶
#   Flattening convention: row-major ('C' order).
#   Pixel (r, c) ↦ index 64r + c.
#   Each nullspace vector s ∈ ℝ^{4096×1}.
#
# COLOR MAP (Flow → RGB):
#   We compute horizontal flow u(r,c) at every pixel.
#     u > 0  (rightward)  → Blue channel
#     u < 0  (leftward)   → Red channel
#     u = 0               → Black
# ============================================================================

# ── 1. THE SPACE ────────────────────────────────────────────────────────────
N = 64
dim = N * N  # 4,096 dimensions

# Row / column coordinate grids (used to build vortex fields)
rows = np.arange(N)
cols = np.arange(N)
cc, rr = np.meshgrid(cols, rows)  # cc[r,c]=c, rr[r,c]=r  (each 64×64)

# ── 2. NULLSPACE BASIS VECTORS (Vortex Stream Functions) ────────────────────
# A divergence-free (Ax = 0) 2-D velocity field can be derived from a
# scalar "stream function" ψ(r,c):
#     u = −∂ψ/∂r   (horizontal flow component)
#     v =  ∂ψ/∂c   (vertical flow component)
# Any such (u, v) automatically satisfies ∂u/∂c + ∂v/∂r = 0  (mass
# conservation), so the velocity field lives in the Nullspace of the
# discrete divergence operator A.
#
# We define three stream functions whose vortex patterns are visually
# distinct.  Each one yields a nullspace vector sₖ.

def gaussian_vortex(rr, cc, center_r, center_c, radius, clockwise=True):
    """
    Build a 2-D velocity field (u, v) from a Gaussian stream function
        ψ(r,c) = exp(−((r−r₀)² + (c−c₀)²) / (2σ²))
    Returns
    -------
    u_grid, v_grid : ndarray (N, N)
        Horizontal and vertical velocity components.
    """
    dr = rr - center_r
    dc = cc - center_c
    sigma = radius
    psi = np.exp(-(dr**2 + dc**2) / (2 * sigma**2))

    # Finite-difference derivatives (central, with periodic boundary via roll)
    #   u = −∂ψ/∂r  ≈  −(ψ[r+1,c] − ψ[r−1,c]) / 2
    #   v =  ∂ψ/∂c  ≈   (ψ[r,c+1] − ψ[r,c−1]) / 2
    u_grid = -(np.roll(psi, -1, axis=0) - np.roll(psi, 1, axis=0)) / 2.0
    v_grid =  (np.roll(psi, -1, axis=1) - np.roll(psi, 1, axis=1)) / 2.0

    if clockwise:
        u_grid, v_grid = -u_grid, -v_grid

    return u_grid, v_grid


# ── Vortex 1: Large CLOCKWISE swirl in the center ──────────────────────────
u1, v1 = gaussian_vortex(rr, cc, center_r=32, center_c=32, radius=14,
                         clockwise=True)

# ── Vortex 2: Smaller COUNTER-CLOCKWISE swirl — top-left corner ────────────
u2, v2 = gaussian_vortex(rr, cc, center_r=12, center_c=12, radius=7,
                         clockwise=False)

# ── Vortex 3: Smaller COUNTER-CLOCKWISE swirl — bottom-right corner ────────
u3, v3 = gaussian_vortex(rr, cc, center_r=52, center_c=52, radius=7,
                         clockwise=False)

# ── 3. FLATTEN TO STRICT COLUMN VECTORS: sₖ ∈ ℝ^{4096×1} ──────────────────
# We pack each velocity field as a column vector.  Since we ultimately
# colour by *horizontal* flow only, we keep the u-component.
# (The full nullspace vector would be [u; v] ∈ ℝ^{8192×1}, but we only
# need the horizontal slice for our RGB mapping.)

s1 = u1.flatten().reshape(-1, 1)  # Shape: (4096, 1)
s2 = u2.flatten().reshape(-1, 1)  # Shape: (4096, 1)
s3 = u3.flatten().reshape(-1, 1)  # Shape: (4096, 1)

# Normalise each basis vector so peak magnitude = 1
s1 = s1 / np.max(np.abs(s1))
s2 = s2 / np.max(np.abs(s2))
s3 = s3 / np.max(np.abs(s3))

# ── 4. ANIMATION SETUP ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_title("Nullspace Eddies:  x = c₁s₁ + c₂s₂ + c₃s₃  (Ax = 0)")
ax.set_xlabel("Column (c)")
ax.set_ylabel("Row (r)")

# Initial blank RGB frame  (Representation Layer: 64×64×3)
rgb_frame = np.zeros((N, N, 3))
img = ax.imshow(rgb_frame, interpolation='nearest')


def flow_to_rgb(x_col):
    """
    Map horizontal-flow column vector x ∈ ℝ^{4096×1} to an RGB image.

    Representation Layer Bridge:
        1. x_col is the column vector produced by the linear combination.
        2. Reshape to 64×64 to recover the grid layout (row-major).
        3. Positive flow (rightward) → Blue channel.
           Negative flow (leftward)  → Red channel.
           Zero flow                 → Black.

    Parameters
    ----------
    x_col : ndarray, shape (4096, 1)
        Horizontal flow at every pixel.

    Returns
    -------
    rgb : ndarray, shape (64, 64, 3)
        Displayable image with values in [0, 1].
    """
    # Bridge: column vector → 64×64 grid  (row-major / 'C' order)
    u = x_col.reshape(N, N)

    rgb = np.zeros((N, N, 3))
    rgb[:, :, 0] = np.clip(-u, 0, 1)  # Red  = leftward  (negative u)
    rgb[:, :, 2] = np.clip( u, 0, 1)  # Blue = rightward (positive u)
    return rgb


def update(frame):
    """
    Each frame computes a new linear combination of nullspace vectors:
        x(t) = c₁(t) · s₁  +  c₂(t) · s₂  +  c₃(t) · s₃

    The coefficients cₖ(t) oscillate with sine waves at different
    frequencies so the eddies pulse, grow, shrink, and interfere.
    Because each sₖ ∈ N(A) and the nullspace is a subspace,
    x(t) ∈ N(A)  for ALL t.   (Ax = 0 always holds.)
    """
    t = frame * 0.05  # Time parameter

    # Time-varying coefficients (sine waves at different frequencies)
    c1 = 0.8 * np.sin(1.0 * t)           # Slow, dominant pulse
    c2 = 0.5 * np.sin(2.3 * t + 1.0)     # Faster, phase-shifted
    c3 = 0.5 * np.sin(1.7 * t + 2.5)     # Different frequency & phase

    # ── THE LINEAR ALGEBRA ──────────────────────────────────────────────
    # Linear combination in ℝ^{4096×1}:
    #   x = c₁ s₁ + c₂ s₂ + c₃ s₃
    # This is a point in the Nullspace N(A), since N(A) is closed under
    # addition and scalar multiplication (it is a subspace).
    x_flow = c1 * s1 + c2 * s2 + c3 * s3  # Shape: (4096, 1)

    # Representation Layer: map flow vector → RGB image
    rgb = flow_to_rgb(x_flow)
    img.set_array(rgb)
    return [img]


ani = FuncAnimation(fig, update, frames=500, interval=40, blit=True)
plt.tight_layout()
plt.show()
