"""
NULLSPACE: THE RUNNING CIRCLE — Ax = 0

CALCULATION LAYER ONLY. No display code lives here.

QUESTION: How can flow move if the equation is Ax = 0 (Total Balance)?
ANSWER:   It moves in a LOOP.

MATH:
  We build two static basis vectors s₁ and s₂ in the Nullspace.
    s₁ = Ring bright at 3 o'clock  (modulated by cos(angle))
    s₂ = Ring bright at 12 o'clock (modulated by sin(angle))

  Then we mix them linearly:
    x(t) = cos(t)·s₁ + sin(t)·s₂

  Because s₁, s₂ ∈ Nullspace(A), x(t) ∈ Nullspace(A) for all t.
  Result: A bright spot that ORBITS the center.

GEOMETRY: 64×64 grid, row-major.  Pixel (r,c) → index 64r + c.
"""
import numpy as np

N = 64
SPEED = 0.094  # ≈ (3 × 2π) / 200 radians per frame
BRIGHTNESS = 0.5


def build_basis():
    """
    Build the two Nullspace basis vectors s₁, s₂ ∈ ℝ^{4096×1}.

    These are the "Special Solutions" to Ax = 0.
      s₁ = ring shape × cos(angle)  → bright at 3 o'clock
      s₂ = ring shape × sin(angle)  → bright at 12 o'clock

    Returns:
        s1: np.ndarray, shape (4096, 1)
        s2: np.ndarray, shape (4096, 1)
    """
    cc, rr = np.meshgrid(np.arange(N, dtype=float), np.arange(N, dtype=float))

    center = 32
    radius = 16
    dr = rr - center
    dc = cc - center
    angle = np.arctan2(dr, dc)
    dist = np.sqrt(dr**2 + dc**2)

    # Gaussian ring shape
    ring_shape = np.exp(-((dist - radius) ** 2) / (2 * 2.0**2))

    # Two basis vectors — static snapshots of the ring
    s1 = (ring_shape * np.cos(angle)).flatten().reshape(-1, 1)  # (4096, 1)
    s2 = (ring_shape * np.sin(angle)).flatten().reshape(-1, 1)  # (4096, 1)
    return s1, s2


def x_to_rgb(x_state, brightness=BRIGHTNESS):
    """
    Convert column vector x ∈ ℝ^{4096×1} to an RGB frame (64, 64, 3) uint8.

    REPRESENTATION BRIDGE:
        x.reshape(64, 64) reverses the row-major flattening.
        Pixel (r, c) = x[64r + c].

    COLOR MAP (simulation-specific):
        Positive values (crests)  → Green channel
        Negative values (troughs) → Red channel
        Gamma correction (^0.6) boosts the tails so you can see the ring.
    """
    grid = x_state.reshape(N, N)

    val_pos = np.maximum(grid, 0) ** 0.6
    val_neg = np.maximum(-grid, 0) ** 0.6

    rgb = np.zeros((N, N, 3), dtype=np.uint8)
    rgb[:, :, 0] = (val_neg * 255 * brightness).astype(np.uint8)  # Red = trough
    rgb[:, :, 1] = (val_pos * 255 * brightness).astype(np.uint8)  # Green = crest
    # Blue = 0
    return rgb


def frames(speed=SPEED):
    """
    Generator that yields RGB frames (64, 64, 3) uint8 forever.

    Each yield is one frame ready for display.
    The consumer (display driver) does NOT interpret values —
    it just shows the pixels.

    x(t) = cos(t)·s₁ + sin(t)·s₂
    """
    s1, s2 = build_basis()
    t = 0.0
    while True:
        # LINEAR COMBINATION in the Nullspace
        x_state = np.cos(t) * s1 + np.sin(t) * s2

        # Convert to display-ready RGB
        yield x_to_rgb(x_state)

        t += speed
