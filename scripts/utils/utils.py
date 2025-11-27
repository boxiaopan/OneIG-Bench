import os
import stat
import megfile
import argparse
import pandas as pd
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

def parse_args():
    parser = argparse.ArgumentParser(description="Run alignment score evaluation.")
    parser.add_argument("--mode", type=str, default="EN", help="Choose language mode (EN/ZH).")
    parser.add_argument("--image_dirname", type=str, default="organized_images", help="Base directory containing organized images.")
    parser.add_argument("--model_names", type=str, nargs="+", default=["gpt-4o"], help="List of model names.")
    parser.add_argument("--image_grid", type=int, nargs="+", default=[2], help="List of image grids.")
    parser.add_argument("--image_type", type=str, default="non-grids", help="Image type: 'grids' or 'non-grids'.")
    parser.add_argument("--checkpoint", type=str, default="15000", help="Checkpoint number (e.g., '15000').")
    parser.add_argument("--class_items", type=str, nargs="+", default=["anime", "human", "object"], help="List of class items.")
    return parser.parse_args()


def get_image_path(base_dir: str, model_name: str, image_type: str, checkpoint: str, mode: str, category: str = None) -> str:
    """
    Construct the image path based on the new directory structure.
    
    Structure: base_dir/model_name/image_type/checkpoint/language/[category/]
    
    Args:
        base_dir: Base directory (e.g., 'organized_images')
        model_name: Model name (e.g., 'omni', 'omni-ep')
        image_type: 'grids' or 'non-grids'
        checkpoint: Checkpoint number (e.g., '15000')
        mode: Language mode ('EN' or 'ZH')
        category: Optional category (e.g., 'anime', 'human')
    
    Returns:
        Full path to the image directory
    """
    language = "en" if mode == "EN" else "zh"
    if category:
        return os.path.join(base_dir, model_name, image_type, checkpoint, language, category)
    else:
        return os.path.join(base_dir, model_name, image_type, checkpoint, language)

def is_black_image(image):
    pixels = image.load()  
    for i in range(image.width):
        for j in range(image.height):
            if pixels[i, j] != (0, 0, 0):
                return False
    return True

def split_2x2_grid(image_path, grid_size, cache_dir):
    with megfile.smart_open(image_path, 'rb') as f:
        grid_image = Image.open(f)

        width, height = grid_image.size

        individual_width = width // grid_size[0]
        individual_height = height // grid_size[1]

        image_list = []

        for i in range(grid_size[1]):
            for j in range(grid_size[0]):
                box = (
                    j * individual_width,      
                    i * individual_height,     
                    (j + 1) * individual_width,  
                    (i + 1) * individual_height  
                )

                individual_image = grid_image.crop(box)

                if is_black_image(individual_image):
                    print(f"Detected a black image at position ({i},{j}) in {image_path}")
                else:
                    image_list.append(individual_image)

    image_path_list = []
    for i, image in enumerate(image_list):
        image_path = os.path.join(cache_dir, f"{i}.jpg")
        image.save(image_path)
        image_path_list.append(image_path)

    return image_path_list

def save2csv(df, csv_path):
    df.to_csv(csv_path)
    print(f"Results saved to {csv_path}")

def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)
