from PIL import Image
import math
import numpy as np

#bias of 0 has no distortion, and 1 of maximum distortion
DISTORTION_BIAS = 0.1
#desired target RGB
TARGET = (255, 0, 0)
#importance of surrounding searched pixels when calculating error
DISTANCE_BIAS = 0.1
#radius searched around each pixel adding to its potential error
DISTANCE = 3


def main():
    print("Running . . .")
    image = Image.open("test_images/DEXI_test_2.jpg")

    bias_array = make_bias_array(image, DISTORTION_BIAS)
    pixels = image.load()
    make_error_map(image, DISTANCE, bias_array)
    #find_target_pixel(image, pixels, image.width, image.height, 0, 0, bias_array)
    print("Done")


def calculate_pixel_error(p, px, py, dist, bias_array, width, height):
    """
    calculate_pixel_error finds how far from the target RGB a given pixel is,
    accounting for the error of the surrounding pixels and distortion of the lens

    :param p: Pixels object with all pixels in the image
    :param px: x coordinate of the pixel
    :param py: y coordinate of the pixel
    :param dist: radius around each pixel that will be searched to add to that pixels error
    :param bias_array: list of the bias values of the image due to lens distortion
    :param width: width of the image
    :param height: height of the imaeg
    :return: returns an arbitrary value (error) that, when compared to other pixels,
    demonstrates how "red" a pixel is. a higher number indicates that it has high
    error, and is far from the target RGB values
    """
    sum_error = 0
    individual_error = 0

    for x in range(max(0, px - dist), min(int(width), px + dist)):
        for y in range (max(0, py - dist), min(int(height), py + dist)):
            if (math.sqrt((x - px) ** 2 + (y - py) ** 2) > dist): continue
            if (px == x and py == y):
                individual_error = abs((abs(p[x, y][0] - TARGET[0]) +
                                            abs(p[x, y][0] - TARGET[1]) +
                                            abs(p[x, y][0] - TARGET[2])))
            else:
                individual_error = abs(bias_array[x][y] *
                                                (abs(p[x, y][0] - TARGET[0]) +
                                                abs(p[x, y][0] - TARGET[1]) +
                                                abs(p[x, y][0] - TARGET[2])) *
                                                DISTANCE_BIAS * ((x - px) ** 2 + (y - py) ** 2) / dist)
            sum_error += individual_error

            #if the pixel is around the edge, add more error
            if (x  + dist > width or x - dist < 0):
                sum_error += individual_error
                #sum_error += 100000
            if (y + dist > height or y - dist < 0):
                sum_error += individual_error
                #sum_error += 100000
    return sum_error


def find_target_pixel(image, pixels, width, height, least_x, least_y, bias_array):
    """
    find_target_pixel finds the pixel most denseley populated with the target RGB
    through an algorithm closely related to a binary search

    :param image: image that is to be inspected, used for a consisted width and height
    for the calculate_pixel_error function
    :param pixels: Pixels object with all pixels in the image
    :param width: width of the area of the image to be inspected
    :param height: height of the area of the image to be inspected
    :param least_x: the lowest value x can be, or leftmost area to be searched
    :param least_y: the lowest value y can be, or topmost area to be searched
    :param bias_array: list of the bias values of the image due to lens distortion
    :return: returns the pixel coordinate most densely populated with the target RGB
    """
    if (width == 1 and height == 1): return (least_x, least_y)
    left_x = least_x + int(-1 * width / 4)
    right_x = least_x + int( width / 4)
    top_y = least_y + int(-1 * height / 4)
    bottom_y = least_y + int(height / 4)
    least_error_location = (0, 0)
    top_left_error = calculate_pixel_error(pixels, left_x, top_y, math.sqrt(width ** 2 + height **  2) / 4, bias_array, image.width, image.height)
    top_right_error = calculate_pixel_error(pixels, right_x, top_y, math.sqrt(width ** 2 + height **  2) / 4, bias_array, image.width, image.height)
    bottom_left_error = calculate_pixel_error(pixels, left_x, bottom_y, math.sqrt(width ** 2 + height **  2) / 4, bias_array, image.width, image.height)
    if (top_left_error > top_right_error):
        least_error_location[0] = 1
    if (top_left_error > bottom_left_error):
        least_error_location[1] = 1
    find_target_pixel(image, pixels, width / 4, height / 4, least_x + width / 2 * least_error_location[0], least_y + height / 2 * least_error_location[1], bias_array)
    return (0, 0)


def make_error_map(image, dist, bias_array):
    """
    make_error_map creates an image with every pixels error represented
    on a grey scale and saves it to the results folder

    :param image: image that is to be inspected
    :param dist: radius around each pixel that will be searched to add to that pixels error
    :param bias_array: list of the bias values of the image due to lens distortion
    """
    pixels = image.load()
    max_error = 0
    pixel_error_array = [[0 for _ in range(image.width)] for _ in range(image.height)]

    #find error of each pixel individually
    pixel_error = 0
    for x in range(0, image.width):
        print("current row: " + str(x))
        for y in range (0, image.height):
            pixel_error = int(calculate_pixel_error(pixels, x, y, dist, bias_array, image.width, image.height))
            pixel_error_array[x].insert(y, pixel_error)

    #find the pixel with the most error and set it as the max
    max_error = pixel_error_array[0][0]
    for x in range(0, image.width):
        for y in range (0, image.height):
            if (pixel_error_array[x][y] > max_error):
                max_error = pixel_error_array[x][y]

    #divide each error by the max and multiply by 255 in order to display the error as an image
    for x in range(0, int(image.width)):
        for y in range (0, int(image.height)):
            pixels[x, y] = (int(pixel_error_array[x][y] / max_error * 255),
                            int(pixel_error_array[x][y] / max_error * 255),
                            int(pixel_error_array[x][y] / max_error * 255))

    image.save("results/error_map3.jpg")
    image.show()


def make_bias_array(image, bias):
    """
    make_bias_array creates an array representing the distortion of an image due
    to the lens

    :param image: image that is to be inspected
    :param bias: how distorted the lens is on a scale of 0-1
    :return: returns an array with each value on a scale of 0-1, representing
    how distorted those pixels would be (0 being regular and 1 being distorted)
    """
    bias_array = [[0 for _ in range(image.width)] for _ in range(image.height)]

    for x in range(image.width):
        for y in range (image.height):
            bias_array[x].insert(y, 0.5 * (((-math.sin(abs(x - (image.width / 2)) / image.height * math.pi / 2 * bias + math.pi / 2 - math.pi / 2 * bias)) + 1) +
                                            ((-math.sin(abs(y - (image.height / 2)) / image.height * math.pi / 2 * bias + math.pi / 2 - math.pi / 2 * bias)) + 1)))

    return bias_array


if __name__ == "__main__":
    main()

"""
Bugs:
whenever pixels near the edge are evaluated, the distortion effect reflects over the axis
    (edged are over-accounted for)
check for when a loop should be incremented by 1 at the end
find_target_pixel does not currently work

Optimization:
utilize numpy matrices rather than for loops
"""