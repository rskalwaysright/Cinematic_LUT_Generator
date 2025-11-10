import os
import time
from utils.frame_extractor import extract_frame
from color_analysis import extract_palette, visualize_palette
from lut_generator import generate_cube_lut


def run_image_demo(image_path):
    # Check if the image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}\nPlace an image in 'samples/' (jpg or png).")

    # Output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Dynamic naming based on image name and timestamp
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    lut_path = os.path.join(output_dir, f"{base_name}_{timestamp}.cube")
    preview_path = os.path.join(output_dir, f"{base_name}_{timestamp}_palette.png")

    # Extract colors from the image
    print(f"Analyzing colors from image: {image_path}")
    colors = extract_palette(image_path, n_colors=8)

    # Save palette visualization
    visualize_palette(colors, save_path=preview_path)

    # Generate LUT
    generate_cube_lut(colors, size=17, output_path=lut_path)

    # Final status
    print("\n✅ Done! Check the 'output/' folder for:")
    print(f"🎨 Palette Preview: {preview_path}")
    print(f"🎬 LUT File: {lut_path}")


if __name__ == "__main__":
    # Change this to your desired image file
    image_path = "samples/mylook.jpg"  # or samples/yourimage.jpg
    run_image_demo(image_path)
