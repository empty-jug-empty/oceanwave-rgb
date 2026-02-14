"""
VALENTINE PATTERN 3: THE IMPLICIT ROSE (REFINED)

CALCULATION LAYER:
    We define a sophisticated "Full and Slender" rose using layered polar functions.
    We add a "Falling Petals" effect using modular arithmetic on the coordinate field.

MATH:
    1. The Rose Head: Constructed from multiple overlapping implicit regions.
       - Core: A spiral function.
       - Petals: Rotated ellipses that "unfold".
    2. Falling Petals: A "Wind Field" simulation.
       - We generate pseudo-random petal positions using coordinate hashing.
       - Movement: y' = (y + speed*t) % Height.

GEOMETRY: 
    64x64 grid. (0,0) is center.
"""
import numpy as np

N = 64
PULSE_SPEED = 0.1
WIND_SPEED = 0.2

def build_coordinate_basis():
    """
    Build coordinate vectors u (y-axis) and v (x-axis).
    Returns vectors in R^{4096x1}.
    """
    R_grid, C_grid = np.meshgrid(np.arange(N), np.arange(N), indexing='ij')

    # Center at (31.5, 31.5), Scale divisor 20.0 to fit board
    center = 31.5
    scale = 22.0 
    
    # Invert u so +y is UP in math. u is vertical, v is horizontal.
    u_vec = -(R_grid.flatten().reshape(-1, 1) - center) / scale
    v_vec = (C_grid.flatten().reshape(-1, 1) - center) / scale
    
    return u_vec, v_vec

def evaluate_rose_head(u, v, t):
    """
    Constructs an ORGANIC SIDE-VIEW Rose Profile.
    Shape: A Bell/Tulip body with layered petals and green sepals at the base.
    """
    # 1. Coordinate System for the Head
    # y=0 is the base of the flower
    y = u - 0.4
    x = v 
    
    # 2. THE MAIN RED BLOOM (Bell Shape)
    # The body is roughly defined by y > A*x^2
    # But it widens at the top.
    # We use a mix of Parabola and Ellipse.
    
    # Central Bell (The main mass)
    # y < 0.8 (Height Limit)
    # |x| < 0.35 * (1 + y) (Widening as we go up)
    # y > -0.2 (Bottom limit, rounded)
    
    # Let's model it as an Intersection of curves:
    # Curve 1 (Bottom Cup): x^2 + (y/0.6)^2 < 0.4
    base_cup = (x**2 + ((y-0.2)/0.8)**2) < 0.25
    
    # Curve 2 (The Opening Petals):
    # Left Petal: An ellipse rotated slightly left
    # Center (-0.1, 0.4)
    p_left = (((x+0.15)*0.9 - (y-0.3)*0.4)**2 * 3 + ((x+0.15)*0.4 + (y-0.3)*0.9)**2 * 0.8) < 0.15
    
    # Right Petal: Mirror of left
    p_right = (((x-0.15)*0.9 + (y-0.3)*0.4)**2 * 3 + ((x-0.15)*0.4 - (y-0.3)*0.9)**2 * 0.8) < 0.15
    
    # Center Petal (The Bud): Vertical Eillipse
    p_center = (x**2 * 8 + (y-0.3)**2 * 2) < 0.12
    
    # The Full Red Shape
    mask_bloom = base_cup | p_left | p_right | p_center
    
    # SCULPTING (The Cuts)
    # We cut gaps between the petals to define them
    # Gap 1 (Left-Center): Line y > 2x + offset
    gap_left = (np.abs(x - (-0.15)) < 0.02) & (y > 0.3)
    # Gap 2 (Right-Center): Line y > -2x + offset
    gap_right = (np.abs(x - 0.15) < 0.02) & (y > 0.3)
    
    mask_rose = mask_bloom & ~(gap_left | gap_right)
    
    # 3. THE SEPALS (Green jagged leaves at base)
    # Three small triangles at the bottom of the bloom
    # y ranges from -0.1 to 0.1 
    # Center Sepal
    sepal_c = (np.abs(x) < 0.05) & (y > -0.25) & (y < 0.0)
    # Left Sepal (Rotated)
    sepal_l = (np.abs(x*0.8 + y*0.6 + 0.15) < 0.04) & (y < 0.0) & (y > -0.2)
    # Right Sepal
    sepal_r = (np.abs(x*0.8 - y*0.6 - 0.15) < 0.04) & (y < 0.0) & (y > -0.2)
    
    mask_sepals = sepal_c | sepal_l | sepal_r
    
    # Return both masks so we can color them differently!
    # But the function signature only returns one mask?
    # We will need to return a TUPLE or combine them cleverly.
    # For now, let's treat sepals as part of the "stem_leaves" function 
    # effectively by returning them here but knowing I need to refactor x_to_rgb slightly.
    # Actually, better: Let's only return the RED part here.
    # And add Sepals to valid "Green" areas in the stem function.
    
    return mask_rose

def evaluate_stem(u, v):
    """
    A slender green stem with leaves and Sepals.
    """
    # 1. Main Stem
    curve = 0.05 * np.sin(3 * u)
    thickness = 0.03
    mask_stem = (np.abs(v - curve) < thickness) & (u < 0.4) & (u > -1.5)
    
    # 2. Leaves on Stem
    # Leaf 1 (Left - Higher) pointing UP-LEFT
    # Center at (-0.3, -0.2). Rotation ~45 degrees.
    # To point UP, the major axis of ellipse (u) should align with vertical.
    # To point UP-LEFT, we rotate +45 deg.
    u_l1 = (u + 0.2)*0.707 - (v - 0.4)*0.707
    v_l1 = (u + 0.2)*0.707 + (v - 0.4)*0.707
    mask_leaf1 = (u_l1**2 * 8 + v_l1**2 * 2) < 0.12

    # Leaf 2 (Right - Lower) pointing UP-RIGHT
    # Center at (0.3, -0.7). Rotation -45 degrees.
    u_l2 = (u + 0.7)*0.707 + (v + 0.4)*0.707
    v_l2 = -(u + 0.7)*0.707 + (v + 0.4)*0.707
    mask_leaf2 = (u_l2**2 * 8 + v_l2**2 * 2) < 0.12
    
    # 3. THE SEPALS (Re-calculated here for Green Color)
    # Relative to Flower Head position (y_head ~ u=0.4)
    y_rel = u - 0.4
    x_rel = v
    
    # Sepals are at the base of the head (y_rel approx -0.2 to 0.0)
    # Simple spikes: |x| < (y - bottom) * slope
    # Or just small ellipses/lines
    sepal_c = (np.abs(x_rel) < 0.04) & (y_rel > -0.25) & (y_rel < -0.05)
    sepal_l = (np.abs(x_rel + 0.15) < 0.04 + 0.1*(y_rel+0.2)) & (y_rel > -0.25) & (y_rel < -0.05)
    sepal_r = (np.abs(x_rel - 0.15) < 0.04 + 0.1*(y_rel+0.2)) & (y_rel > -0.25) & (y_rel < -0.05)
    # Added symmetric sepal on the right (sepal_r2) instead of left (sepal_l2)
    sepal_r2 = (np.abs(x_rel - 0.25) < 0.03 + 0.15*(y_rel+0.22)) & (y_rel > -0.25) & (y_rel < -0.08)

    mask_sepals = sepal_c | sepal_l | sepal_r | sepal_r2
    
    return mask_stem | mask_leaf1 | mask_leaf2 | mask_sepals

def evaluate_falling_petals(u, v, t):
    """
    Simulates petals falling in the wind using Modular Arithmetic.
    We create a "field" of potential petals.
    """
    # 1. Coordinate Transformation for "Infinite Fall"
    # We shift the y-coordinate by time * speed
    # y_flow moves UP, so the texture moves DOWN
    y_flow = u + t * WIND_SPEED
    
    # 2. Grid Cells (The "Hash" trick)
    # Divide space into "cells" of size 0.8 x 0.8
    # Within each cell, we place a petal
    cell_size = 0.8
    cell_y = np.floor(y_flow / cell_size)
    cell_x = np.floor(v / cell_size)
    
    # Local coordinates within the cell (-0.5 to 0.5)
    local_y = (y_flow % cell_size) - 0.5 * cell_size
    local_x = (v % cell_size) - 0.5 * cell_size
    
    # 3. Pseudo-Random Selection
    # We only want petals in SOME cells, not all.
    # We use a math hash based on integer cell indices
    # Simple hash: (x*3 + y*7) % 5 == 0 -> This cell has a petal
    has_petal = ((cell_x * 3 + cell_y * 7) % 5) == 0
    
    # 4. Petal Shape (Small Ellipse)
    # Randomize position slightly based on cell index
    offset_x = 0.1 * np.sin(cell_y) 
    
    petal_mask = (((local_x - offset_x)**2 * 20 + local_y**2 * 5) < 0.02)
    
    # Result: Mask is True only if cell has petal AND pixel is inside shape
    # AND we are below the main flower (u < 0.1) so they don't overlap the head
    return has_petal & petal_mask & (u < 0.3)

def x_to_rgb(mask_rose, mask_stem, mask_petals):
    """
    Bridge to RGB.
    Layer Order: Falling Petals (Bottom) -> Stem -> Rose Head (Top)
    """
    rgb = np.zeros((N * N, 3), dtype=np.uint8)
    
    # 1. Falling Petals (Darker Red/Pink)
    rgb[mask_petals.flatten()] = [200, 50, 100]
    
    # 2. Stem (Green)
    rgb[mask_stem.flatten()] = [34, 139, 34]
    
    # 3. Rose Head (Crimson Red)
    # We create a gradient for the rose? No, solid for MVP.
    rgb[mask_rose.flatten()] = [220, 20, 60]
    
    return rgb.reshape(N, N, 3)

def frames():
    """
    Generator.
    """
    u, v = build_coordinate_basis()
    t = 0.0
    
    while True:
        # CALCULATION
        rose = evaluate_rose_head(u, v, t)
        stem = evaluate_stem(u, v)
        petals = evaluate_falling_petals(u, v, t)
        
        # REPRESENTATION
        yield x_to_rgb(rose, stem, petals)
        
        t += PULSE_SPEED
