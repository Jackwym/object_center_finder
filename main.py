import numpy as np
from scipy import ndimage
import cv2
import time
import threading
import math
START_TIME = time.time()

WHITE_CENTER = True
width = 128
height = 128

class VideoStream:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()

        # Start the frame grabbing thread
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                self.stop()
                return

            with self.lock:
                self.ret, self.frame = ret, frame

    def read(self):
        with self.lock:
            return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()


def get_frame_redness_data(array):
    # Iterate over the pixels and get the redness value of each pixel
    redness_vals = [
        # redness values will be from 0 to 510, with 510 being the most red
        ((array[h, w][0] * 2) - array[h, w][1]) - array[h, w][2]
        for h in range(height)
        for w in range(width)
    ]
    return redness_vals


def make_redness_frame(red_vals, target_pixel):
        # Normalize the redness values to a range of [0, 255]
    least_red = min(red_vals)
    most_red = max(red_vals)

    # Avoid division by zero if all values are the same
    if most_red - least_red == 0:
        normalized_pixels = np.full_like(red_vals, 255, dtype=np.uint8)  # All values will map to 255 if there's no range
    else:
        normalized_pixels = np.clip(((np.array(red_vals) - least_red) / (most_red - least_red) * 255), 0, 255).astype(np.uint8)

    # Reshape normalized pixels to match the image shape (height, width)
    normalized_pixels = normalized_pixels.reshape((height, width))

    # Create a blank image (height, width, 3) to hold RGB values
    img_data = np.zeros((height, width, 3), dtype=np.uint8)

    # Apply the gradient: [value, 0, 255 - value]
    img_data[:, :, 0] = normalized_pixels  # Red channel
    img_data[:, :, 1] = 0  # Green channel (always 0)
    img_data[:, :, 2] = 255 - normalized_pixels  # Blue channel

    # Set the center pixel to white if required
    if WHITE_CENTER:
        img_data[target_pixel[1], target_pixel[0]] = [255, 255, 255]

    return img_data


def find_redness_center(red_vals) -> tuple[int, ...]:
    redness_array = np.array(red_vals).reshape(width, height).T
    redness_grid = redness_array.tolist()

    BOUNDS = (100, 510) # Acceptable bounds for the redness values, i.e. if something doesn't have at least 100 redness score then it doesn't make the cut

    img = np.array(redness_grid)  # Convert redness grid to numpy array
    lowerb = np.array(BOUNDS[0])  # lowest allowed red pixel value
    upperb = np.array(BOUNDS[1])  # highest allowed red pixel value

    mask = cv2.inRange(img, lowerb, upperb)  # Create mask of pixels within the pixel threshold

    if np.all(mask == 0):  # If no pixels are within the pixel threshold, exit
        return (int(width / 2 + (20 * math.cos(time.time()))), int(height / 2))

    blobs = mask > 100  # Identify blobs in the mask & label the
    labels, nlabels = ndimage.label(blobs) # type: ignore

    centers_of_mass = ndimage.center_of_mass(mask, labels, np.arange(nlabels) + 1)  # Find centers of mass
    blob_sizes = ndimage.sum(blobs, labels, np.arange(nlabels) + 1)  # Calculate size of each blob
    redness_center = tuple(int(coord) for coord in centers_of_mass[blob_sizes.argmax()][::-1])  # Find largest blob's center (x,y)

    print(f"Redness center: {redness_center}")
    return redness_center


if __name__ == "__main__":
    # Initialize video stream
    video_stream = VideoStream(0)

    while True:
        ret, frame = video_stream.read()

        if not ret:
            print("Error: Could not read frame.")
            continue

        frame = frame.astype("float32")

        frame = cv2.resize(frame, (128, 128))

        redness_vals = get_frame_redness_data(frame)
        redness_center = find_redness_center(redness_vals)
        new_frame = make_redness_frame(redness_vals, redness_center)

        new_frame = cv2.resize(new_frame, (512, 512))
        new_frame = new_frame.astype("uint8")
        cv2.imshow("Live Video - Most Recent Modified Frame", new_frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_stream.stop()
    cv2.destroyAllWindows()

    print(f"Execution time: {time.time() - START_TIME:.2f} seconds")