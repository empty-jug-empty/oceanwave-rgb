"""
REPRESENTATION LAYER: Pi 5 Driver (piomatter)

Generic display driver. It does NOT know what simulation is running.
It receives (64, 64, 3) uint8 RGB frames and pushes them to the LED matrix.

Requires: adafruit_blinka_raspberry_pi5_piomatter
"""
import sys
import time
import numpy as np

N = 64


def run(frame_generator, fps=30, title="Ocean Wave Simulation"):
    """
    Consume a generator of (64, 64, 3) uint8 frames and display on
    a 64×64 RGB LED Matrix via piomatter.

    Args:
        frame_generator: Generator yielding np.ndarray (64, 64, 3) uint8
        fps: Target frames per second
        title: (unused on hardware, kept for interface parity with laptop)
    """
    try:
        import adafruit_blinka_raspberry_pi5_piomatter as piomatter
    except ImportError:
        print("Error: adafruit_blinka_raspberry_pi5_piomatter library is required.")
        print("Install: pip install adafruit-blinka-raspberry-pi5-piomatter")
        sys.exit(1)

    print(f"Initializing 64×64 RGB Matrix — {title}")

    geometry = piomatter.Geometry(
        width=N, height=N, n_addr_lines=5,
        rotation=piomatter.Orientation.Normal,
    )
    framebuffer = np.zeros((N, N, 3), dtype=np.uint8)
    matrix = piomatter.PioMatter(
        geometry=geometry,
        pinout=piomatter.Pinout.AdafruitMatrixBonnet,
        colorspace=piomatter.Colorspace.RGB888Packed,
        framebuffer=framebuffer,
    )

    gen = frame_generator
    print("Running... Press Ctrl+C to stop.")

    try:
        while True:
            t0 = time.time()

            framebuffer[:] = next(gen)
            matrix.show()

            dt = time.time() - t0
            time.sleep(max(0, 1.0 / fps - dt))
    except KeyboardInterrupt:
        print("\nStopping...")
        framebuffer.fill(0)
        matrix.show()
