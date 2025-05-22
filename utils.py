import os
import glob

from PIL import Image, ImageDraw, ImageFont


def _extract_action_from_filename(filename):
    """
    Extracts the action and extra info from the filename, and includes the step id in the prefix.
    Examples:
        '001_go_to_www.google.com.png' -> '001: go_to (www.google.com)'
        '006_submit_input[name=\'query\'].png' -> '006: submit (input[name=\'query\'])'
        '003_go_back.png' -> '003: go_back'
    """
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)
    # Split off the step id (should be 3 digits)
    parts = name.split("_", 1)
    if len(parts) == 2:
        step_id = parts[0]
        rest = parts[1]
        # Split at the first underscore to separate action and extra info
        if "_" in rest:
            action, extra = rest.split("_", 1)
            return f"{step_id}: {action} ({extra})"
        else:
            return f"{step_id}: {rest}"
    else:
        return name


def _get_font(size=24):
    # Try to get a reasonable font, fallback to default if not found
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()


def _add_text_overlay(image, text):
    # Draws semi-transparent rectangle and overlays text at the top
    draw = ImageDraw.Draw(image, "RGBA")
    font = _get_font()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1] + 5
    padding = 10
    rect_height = text_height + 2 * padding
    rect_width = image.width
    # Draw semi-transparent rectangle
    overlay_color = (0, 0, 0, 128)  # black, half-transparent
    draw.rectangle([(0, 0), (rect_width, rect_height)], fill=overlay_color)
    # Draw text
    text_x = (rect_width - text_width) // 2
    text_y = padding
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
    return image


def create_gif(run_id: str):
    frame_dir = f"frames/{run_id}"
    frame_files = sorted(glob.glob(os.path.join(frame_dir, "*.png")))
    if frame_files and Image is not None:
        images = []
        for f in frame_files:
            img = Image.open(f).convert("RGBA")
            action_text = _extract_action_from_filename(f)
            img_with_text = _add_text_overlay(img, action_text)
            # Convert back to RGB for GIF compatibility
            images.append(img_with_text.convert("RGB"))
        gif_path = os.path.join(frame_dir, "animation.gif")
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=2000,
            loop=0,
        )
        print(f"Saved animation gif to {gif_path}")
    elif not frame_files:
        print("No frames found to create gif.")
    elif Image is None:
        print("Pillow (PIL) is not installed, cannot create gif.")
