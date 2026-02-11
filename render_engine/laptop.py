"""
REPRESENTATION LAYER: Laptop Driver (matplotlib)

Generic display driver. It does NOT know what simulation is running.
It receives (64, 64, 3) uint8 RGB frames and shows them.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

N = 64


def run(frame_generator, fps=30, title="Ocean Wave Simulation"):
    """
    Consume a generator of (64, 64, 3) uint8 frames and display via matplotlib.

    Args:
        frame_generator: Generator yielding np.ndarray (64, 64, 3) uint8
        fps: Target frames per second
        title: Window title
    """
    gen = frame_generator

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title(title)
    ax.axis("off")
    img = ax.imshow(np.zeros((N, N, 3), dtype=np.uint8))

    def update(_frame):
        rgb = next(gen)
        img.set_array(rgb)
        return [img]

    _ani = FuncAnimation(fig, update, interval=1000 // fps, blit=True,
                         cache_frame_data=False)
    plt.show()
