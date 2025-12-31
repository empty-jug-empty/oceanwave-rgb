import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 1. Setup the Grid
size = 64
pixels = size * size  # 4096
x_coord = np.linspace(0, 1, size)
y_coord = np.linspace(0, 1, size)
X, Y = np.meshgrid(x_coord, y_coord)

# 2. Define 4 Basis Vectors (The Columns of our Matrix A)
v1 = np.sin(2 * np.pi * X).flatten()   # Horiz Low-Freq
v2 = np.sin(10 * np.pi * X).flatten()  # Horiz High-Freq
v3 = np.sin(2 * np.pi * Y).flatten()   # Vert Low-Freq
v4 = np.sin(10 * np.pi * Y).flatten()  # Vert High-Freq

# 3. Assemble Matrix A (4096 rows x 4 columns)
A = np.column_stack((v1, v2, v3, v4))

def generate_ocean(weights):
    # The Heart of Linear Algebra: Ax = b
    b = A @ weights 
    return b.reshape((size, size))

# --- MACBOOK VISUALIZATION (Matplotlib) ---

# Setup the Plot
fig, ax = plt.subplots(figsize=(6, 6))
# Initialize with zeros
initial_screen = np.zeros((size, size))
# Use a blue colormap to simulate ocean depth
im = ax.imshow(initial_screen, cmap='ocean', vmin=-2, vmax=2, interpolation='bilinear')
ax.set_title("Ocean Wave Simulation (Basis Projection)")
plt.axis('off') # Hide axes for better look

def update(frame):
    # Time variable t
    t = frame * 0.1
    
    # Dynamic weights: x(t)
    # We are changing the linear combination of our basis vectors over time
    current_weights = np.array([
        1.5 * np.cos(t),       # Basis 1 oscillates
        0.5 * np.sin(t * 2),   # Basis 2 oscillates faster
        0.3 * np.cos(t * 0.5), # Basis 3 slow swell
        0.2                    # Basis 4 constant
    ])
    
    # Compute new state b
    screen = generate_ocean(current_weights)
    
    # Update the image data
    im.set_data(screen)
    return [im]

# Run Animation at ~30 FPS (interval=33ms)
ani = FuncAnimation(fig, update, frames=range(200), interval=33, blit=True)

plt.show()