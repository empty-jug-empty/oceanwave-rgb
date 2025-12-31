import numpy as np

# 1. Setup the Grid
size = 64
pixels = size * size  # 4096
x_coord = np.linspace(0, 1, size)
y_coord = np.linspace(0, 1, size)
X, Y = np.meshgrid(x_coord, y_coord)

# 2. Define 4 Basis Vectors (The Columns of our Matrix A)
# We flatten them to 4096-element columns
v1 = np.sin(2 * np.pi * X).flatten()   # Horiz Low-Freq
v2 = np.sin(10 * np.pi * X).flatten()  # Horiz High-Freq
v3 = np.sin(2 * np.pi * Y).flatten()   # Vert Low-Freq
v4 = np.sin(10 * np.pi * Y).flatten()  # Vert High-Freq

# 3. Assemble Matrix A (4096 rows x 4 columns)
# This matrix is your "Ocean Palette"
A = np.column_stack((v1, v2, v3, v4))

def generate_ocean(weights):
    """
    weights: a vector x with 4 elements [c1, c2, c3, c4]
    returns: the screen image b
    """
    # The Heart of Linear Algebra: Ax = b
    # This dots the weights into our basis patterns
    b = A @ weights 
    
    # Reshape back to 64x64 for the hardware
    return b.reshape((size, size))

# --- TEST DRIVE ---
# Recipe: Heavy on low-freq horizontal, light on high-freq vertical
x = np.array([1.5, 0.2, 0.0, 0.5]) 
screen = generate_ocean(x)

# Note: In a real ocean, these weights (x) will 
# change over time according to physics!