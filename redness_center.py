from PIL import Image
import numpy as np
from scipy import ndimage
import os
import cv2
import time


START_TIME = time.time()
# Open the image, downsizing it to improve speed and grabbing the image parameters (not hardcoded for ez flexibility)
# Image must be a square for a redness map to be generated
INPUT_DIR = "test_images"
OUTPUT_DIR = "results"

# INPUT_NAME = "DEXI_test_1.jpg"
INPUT_NAME = "DEXI_test_2.jpg"
# INPUT_NAME = "christmas.jpg"
# INPUT_NAME = "crossout.jpg"

image = Image.open(os.path.join(INPUT_DIR, INPUT_NAME))
image.thumbnail((128, 128), Image.Resampling.NEAREST)
width, height = image.size

WHITE_CENTER = True

def get_redness_data(image: Image.Image) -> list[int]:
    # Get the pixel data
    pixels = image.load()
    if pixels is None:
        raise TypeError("Could not load the image")

    # Iterate over the pixels and get the redness value of each pixel
    redness_vals = [
        # ((red * 2) - green) - blue
        # redness values will be from 0 to 510, with 510 being the most red
        ((pixels[w, h][0] * 2) - pixels[w, h][1]) - pixels[w, h][2]
        for w in range(width)
        for h in range(height)
    ]

    return redness_vals

def find_redness_center(red_vals) -> tuple[int, ...]:
    redness_array = np.array(red_vals).reshape(width, height).T
    redness_grid = redness_array.tolist()

    BOUNDS = (100, 510) # Acceptable bounds for the redness values, i.e. if something doesn't have at least 100 redness score then it doesn't make the cut

    img = np.array(redness_grid)  # Convert redness grid to numpy array
    lowerb = np.array(BOUNDS[0])  # lowest allowed red pixel value
    upperb = np.array(BOUNDS[1])  # highest allowed red pixel value
    mask = cv2.inRange(img, lowerb, upperb)  # Create mask of pixels within the pixel threshold

    if np.all(mask == 0):  # If no pixels are within the pixel threshold, exit
        exit(1)

    blobs = mask > 100  # Identify blobs in the mask & label them
    labels, nlabels = ndimage.label(blobs) # type: ignore

    centers_of_mass = ndimage.center_of_mass(mask, labels, np.arange(nlabels) + 1)  # Find centers of mass
    blob_sizes = ndimage.sum(blobs, labels, np.arange(nlabels) + 1)  # Calculate size of each blob
    redness_center = tuple(int(coord) for coord in centers_of_mass[blob_sizes.argmax()][::-1])  # Find largest blob's center (x,y)

    print(f"Redness center: {redness_center}")
    return redness_center

def make_redness_map(redness_vals, center) -> None:
    if width != height:
        print("Image is not a square - redness map cannot be generated")
        return
    
    least_red = min(redness_vals)
    most_red = max(redness_vals)
    normalized_pixels = [(int((val - least_red) / (most_red - least_red) * 255)) for val in redness_vals]

    # Map normalized values to colored pixels
    img = Image.new("RGB", (width, height))
    for w in range(width):
        for h in range(height):
            if (w, h) == center and WHITE_CENTER:
                img.putpixel((w, h), (255, 255, 255))
                continue
            value = normalized_pixels[w * width + h]
            # Create a gradient from blue (not red) to red (red)
            color = (value, 0, 255 - value)
            img.putpixel((w, h), color)

    # Resize the image to 512x512
    img = img.resize((512, 512), Image.Resampling.NEAREST)

    # Create the directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    result_filename = f"{INPUT_NAME.split(".")[0]}_redness_map.jpg"

    # Save the image as the specified file
    img.save(os.path.join(OUTPUT_DIR, result_filename))
    print(f"Redness map saved as {result_filename}")

if __name__ == "__main__":
    redness_vals = get_redness_data(image)
    redness_center = find_redness_center(redness_vals)
    make_redness_map(redness_vals, redness_center)

    print(f"Execution time: {time.time() - START_TIME:.2f} seconds")
