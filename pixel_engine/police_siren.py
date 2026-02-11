"""
POLICE SIREN: ORTHOGONAL ALTERNATION

CALCULATION LAYER ONLY. No display code lives here.

QUESTION: How do we coordinate two distinct zones (Top vs Bottom) independently?
ANSWER:   We define two ORTHOGONAL regions in our vector space.

MATH:
  We build two disjoint basis vectors (masks):
    u_{top} ∈ ℝ^{4096} : 1 on rows 0-31, 0 elsewhere.
    u_{bot} ∈ ℝ^{4096} : 1 on rows 32-63, 0 elsewhere.
  
  Since dot(u_{top}, u_{bot}) = 0, they are orthogonal.
  We can drive them with independent time-series signals f(t) and g(t).
  
  State x(t) = f(t)·u_{top} + g(t)·u_{bot}

  For a police siren, we want a Strobe Pattern:
  f(t): 3 quick pulses, then silence.
  g(t): Silence, then 3 quick pulses.

GEOMETRY: 
  64x64 Grid.
  Top Half (Blue Zone): Rows 0-31.
  Bottom Half (Red Zone): Rows 32-63.
"""
import numpy as np

N = 64

def build_basis():
    """
    Construct the two orthogonal spatial basis vectors.
    
    Returns:
        u_top (4096, 1): Mask for upper half.
        u_bot (4096, 1): Mask for lower half.
    """
    grid_top = np.zeros((N, N))
    grid_bot = np.zeros((N, N))

    # Partition the space linearly
    grid_top[0:32, :] = 1.0  # Upper Half
    grid_bot[32:64, :] = 1.0  # Lower Half

    # Flatten to column vectors
    u_top = grid_top.flatten().reshape(-1, 1)
    u_bot = grid_bot.flatten().reshape(-1, 1)
    
    return u_top, u_bot

def x_to_rgb(x_state):
    """
    Map the scalar state vector back to the Representation Layer (RGB).
    
    COLOR MAPPING:
    - We use the SPATIAL POSITION to determine color.
    - Top Half (Rows 0-31) -> BLUE channel.
    - Bottom Half (Rows 32-63) -> RED channel.
    """
    # 1. Reshape from Vector World (4096x1) to Grid World (64x64)
    grid = x_state.reshape(N, N)
    
    # 2. Clip intensities to valid 0-1 range
    intensity = np.clip(grid, 0, 1)
    
    # 3. Create RGB buffer
    rgb = np.zeros((N, N, 3), dtype=np.uint8)
    
    # Apply Colors based on regions
    # Top Half -> Blue (Channel 2)
    # Using 'Deep Blue': 255 is standard
    rgb[0:32, :, 2] = (intensity[0:32, :] * 255).astype(np.uint8)
    
    # Bottom Half -> Red (Channel 0)
    rgb[32:64, :, 0] = (intensity[32:64, :] * 255).astype(np.uint8)
    
    return rgb

def frames(speed=1.0):
    """
    Generator yielding frames.
    
    We implement a 'Wig-Wag' style strobe pattern.
    Cycle Length: ~30 frames
    0-15: Top flashes 3 times
    15-30: Bottom flashes 3 times
    """
    u_top, u_bot = build_basis()
    t = 0
    
    while True:
        # Define the strobe logic based on integer frame counter
        # Cycle is 30 frames long
        cycle_t = t % 30
        
        i_top = 0.0
        i_bot = 0.0
        
        # Logic: 3 Flashes per half-cycle.
        # Each flash is approx 5 frames: 3 ON, 2 OFF.
        if cycle_t < 15:
            # Blue Phase (Top)
            # Flash at t=0, t=5, t=10
            if (cycle_t % 5) < 3:
                i_top = 1.0
        else:
            # Red Phase (Bottom)
            phase_t = cycle_t - 15
            # Flash at t=0, t=5, t=10 (relative to phase)
            if (phase_t % 5) < 3:
                i_bot = 1.0
                
        # Linear Combination
        x_state = i_top * u_top + i_bot * u_bot
        
        yield x_to_rgb(x_state)
        
        t += 1
