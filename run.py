"""
Ocean Wave RGB — Orchestrator

Usage:
    python run.py <animation> <display>

Arguments:
    animation : Name of a simulation module in pixel_engine/
                e.g. nullspace_eddies
    display   : "laptop" (matplotlib) or "pi" (LED matrix)

Examples:
    python run.py nullspace_eddies laptop
    python run.py nullspace_eddies pi
"""
import sys
import importlib


def main():
    if len(sys.argv) != 3:
        print("Usage: python run.py <animation> <display>")
        print()
        print("  animation : nullspace_eddies")
        print("  display   : laptop | pi")
        sys.exit(1)

    animation_name = sys.argv[1]
    display_name = sys.argv[2].lower()

    # ── Load the Calculation Layer ──────────────────────────────────
    try:
        sim = importlib.import_module(f"pixel_engine.{animation_name}")
    except ModuleNotFoundError:
        print(f"Error: animation '{animation_name}' not found in pixel_engine/")
        print(f"       Expected file: pixel_engine/{animation_name}.py")
        sys.exit(1)

    # ── Load the Representation Layer ───────────────────────────────
    if display_name not in ("laptop", "pi"):
        print(f"Error: display must be 'laptop' or 'pi', got '{display_name}'")
        sys.exit(1)

    driver = importlib.import_module(f"render_engine.{display_name}")

    # ── Wire them together ──────────────────────────────────────────
    # pixel_engine produces frames → rgb consumes and displays them
    title = sim.__doc__.strip().split("\n")[0] if sim.__doc__ else animation_name
    driver.run(sim.frames(), title=title)


if __name__ == "__main__":
    main()
