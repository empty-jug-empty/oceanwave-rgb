import time
import sys
import numpy as np

try:
    import adafruit_blinka_raspberry_pi5_piomatter as piomatter
except ImportError:
    print("Error: adafruit_blinka_raspberry_pi5_piomatter library is required.")
    sys.exit(1)

# Configuration
# Single 64x64 panel
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 64

def get_color_buffer(color_hex):
    """
    Create a numpy buffer filled with a specific color.
    color_hex: 0x00RRGGBB format
    """
    # Create a buffer of uint32
    buffer = np.full((DISPLAY_HEIGHT, DISPLAY_WIDTH), color_hex, dtype=np.uint32)
    return buffer

def main():
    print("Initializing 64x64 RGB Matrix Color Test...")
    
    # Initialize the geometry
    # n_addr_lines=5 is required for 64x64 panels (1/32 scan)
    geometry = piomatter.Geometry(
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        n_addr_lines=5, 
        rotation=piomatter.Orientation.Normal
    )

    # Create a framebuffer
    # The library expects (H, W, 3) uint8 array for RGB888Packed
    framebuffer = np.zeros((DISPLAY_HEIGHT, DISPLAY_WIDTH, 3), dtype=np.uint8)

    # Initialize the matrix
    matrix = piomatter.PioMatter(
        geometry=geometry,
        pinout=piomatter.Pinout.AdafruitMatrixBonnet,
        colorspace=piomatter.Colorspace.RGB888Packed,
        framebuffer=framebuffer
    )

    colors = [
        ("Red", (255, 0, 0)),
        ("Green", (0, 255, 0)),
        ("Blue", (0, 0, 255)),
        ("White", (255, 255, 255))
    ]

    print("Starting color cycle test (Ctrl+C to stop)...")

    try:
        while True:
            for name, color_value in colors:
                print(f"Displaying {name}...")
                # Fill the framebuffer with the color tuple (broadcasts to all pixels)
                framebuffer[:] = color_value
                matrix.show()
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        # Clear the display on exit
        framebuffer.fill(0)
        matrix.show()
        print("Display cleared.")

if __name__ == "__main__":
    main()
