"""
VALENTINE PATTERN 1: THE IMPLICIT HEART

CALCULATION LAYER:
    We define the heart strictly via Algebraic Geometry on column vectors.
    We do NOT paint pixels. We evaluate the state of the board.

MATH:
    Coordinate Vectors u, v ∈ ℝ^{4096×1} are normalized to [-1.5, 1.5].
    
    The Heart Region is the set of points where:
        (x² + y² - 1)³ - x²y³ ≤ 0
    
    The Blue Edge is the "Epsilon Neighborhood" just outside:
        0 < F(x,y) < ε

GEOMETRY: 64×64 grid, row-major. Pixel (r, c) -> index 64r + c.
"""
import numpy as np

N = 64
PULSE_SPEED = 0.15  # Heartbeat speed

def build_coordinate_basis():
    """
    Build the fundamental coordinate vectors for the grid.
    
    Returns:
        u: Vertical coordinate vector (y-axis) (4096, 1)
        v: Horizontal coordinate vector (x-axis) (4096, 1)
    """
    # 1. Meshgrid: Create 2D arrays of indices
    # indexing='ij' ensures matrix indexing (row, col)
    # R_grid = Row indices, C_grid = Column indices
    R_grid, C_grid = np.meshgrid(np.arange(N), np.arange(N), indexing='ij')

    # 2. Flatten to Column Vectors (The Linear Algebra Format)
    # We center the coordinates at 31.5 (halfway)
    # We invert 'u' because row 0 is at the top, but mathematical +y is up.
    center = 31.5
    
    # Raw vectors centered at (0,0)
    u_raw = -(R_grid.flatten().reshape(-1, 1) - center)
    v_raw = (C_grid.flatten().reshape(-1, 1) - center)
    
    return u_raw, v_raw

def evaluate_heart_field(u, v, scale):
    """
    Evaluates the Heart Equation on the input vectors.
    
    Args:
        u, v: Centered coordinate vectors (4096, 1)
        scale: Scalar, controls the size of the heart.
        
    Returns:
        F: The scalar field result (4096, 1)
    """
    # Normalize by scale to get mathematical x, y approx range [-1.5, 1.5]
    y = u / scale
    x = v / scale
    
    # Equation: (x² + y² - 1)³ - x²y³
    # Note: We use typical x,y math notation here, where u=y, v=x
    term1 = x**2 + y**2 - 1
    F = (term1**3) - (x**2) * (y**3)
    
    return F

def x_to_rgb(mask_red, mask_blue):
    """
    Convert boolean state masks to RGB.
    
    REPRESENTATION BRIDGE:
        Maps the abstract boolean states to actual LED colors.
        Blue mask is the background heart. Red mask is the foreground heart.
    """
    # Initialize Black Background (4096, 3)
    rgb_flat = np.zeros((N * N, 3), dtype=np.uint8)
    
    # Apply Blue to the Outer Heart (Background Layer)
    rgb_flat[mask_blue.flatten()] = [50, 50, 255]   # Bright Blue

    # Apply Red to the Inner Heart (Foreground Layer)
    rgb_flat[mask_red.flatten()] = [220, 20, 60]  # Crimson Red
    
    return rgb_flat.reshape(N, N, 3)

def frames():
    """
    Generator yielding pulsating Heart frames.
    Two hearts: One larger (blue), one smaller (red).
    """
    u_raw, v_raw = build_coordinate_basis()
    t = 0.0
    
    while True:
        # ANIMATION: Heartbeat Pulse
        # Base scale for the heart
        base_scale = 13.0 + 1.5 * (np.sin(t)**20 + np.sin(t + np.pi/3)**8)
        
        # 1. CALCULATION LAYER
        # We define two scales: Outer (Blue) and Inner (Red)
        scale_blue = base_scale + 1  # Slightly larger
        scale_red = base_scale         # The main heart
        
        # Evaluate field for both scales
        F_blue = evaluate_heart_field(u_raw, v_raw, scale_blue)
        F_red = evaluate_heart_field(u_raw, v_raw, scale_red)
        
        # Define Regions (Boolean Logic on Vectors)
        # Inside the implicit curve F <= 0
        mask_blue = F_blue <= 0
        mask_red = F_red <= 0
        
        # 2. REPRESENTATION LAYER
        # Pass both masks to the renderer
        yield x_to_rgb(mask_red, mask_blue)
        
        t += PULSE_SPEED
