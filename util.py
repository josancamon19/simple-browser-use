import os
import glob

from PIL import Image


def create_gif(run_id: str):
    frame_dir = f"frames/{run_id}"
    frame_files = sorted(glob.glob(os.path.join(frame_dir, "*.png")))
    if frame_files and Image is not None:
        images = [Image.open(f) for f in frame_files]
        gif_path = os.path.join(frame_dir, "animation.gif")
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=700,
            loop=0,
        )
        print(f"Saved animation gif to {gif_path}")
    elif not frame_files:
        print("No frames found to create gif.")
    elif Image is None:
        print("Pillow (PIL) is not installed, cannot create gif.")
