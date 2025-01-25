from PIL import Image
import math
import numpy as np

#bias of 1 has no distortion, and 0 of maximum distortion
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
    #print(find_target_pixel(image))
    pixels = image.load()
    print(pixels[0, 0])
    print(pixels[15, 15])
    print(pixels[599, 599])
    # exit()
    #print(calculate_pixel_error(pixels, 0, 0, 2, bias_array, image.width, image.height))
    #make_bias_map(image, DISTANCE_BIAS)
    make_error_map(image, DISTANCE, bias_array)
    #find_target_pixel(image, pixels, image.width, image.height, 0, 0, bias_array)
    print("Done")


def calculate_pixel_error(p, px, py, dist, bias_array, width, height):
    sum_error = 0
    individual_error = 0

    # for x in range(max(int(-1 * width / 2), px - dist), min(int(width / 2) -1, px + dist)):
    #     for y in range (max(int(-1 * height / 2), py - dist), min(int(height / 2) - 1, py + dist)):
    for x in range(max(0, px - dist), min(int(width), px + dist)):
        for y in range (max(0, py - dist), min(int(height), py + dist)):
            if (math.sqrt((x - px) ** 2 + (y - py) ** 2) > dist): continue
            if (px == x and py == y):
                individual_error = abs((abs(p[x, y][0] - TARGET[0]) +
                                            abs(p[x, y][0] - TARGET[1]) +
                                            abs(p[x, y][0] - TARGET[2])))
            else:
                # individual_error = abs(bias_array[int(x + width / 2)][int(y + width / 2)] *
                #                                 (abs(p[x, y][0] - TARGET[0]) +
                #                                 abs(p[x, y][0] - TARGET[1]) +
                #                                 abs(p[x, y][0] - TARGET[2])) *
                #                                 DISTANCE_BIAS * ((x - px) ** 2 + (y - py) ** 2) / dist)
                individual_error = abs(bias_array[x][y] *
                                                (abs(p[x, y][0] - TARGET[0]) +
                                                abs(p[x, y][0] - TARGET[1]) +
                                                abs(p[x, y][0] - TARGET[2])) *
                                                DISTANCE_BIAS * ((x - px) ** 2 + (y - py) ** 2) / dist)
            sum_error += individual_error

            if (x  + dist > width or x - dist < 0):
                # print(x)
                sum_error += individual_error
            if (y + dist > height or y - dist < 0):
                # print(y)
                sum_error += individual_error
    return sum_error


def find_target_pixel(image, pixels, width, height, least_x, least_y, bias_array):
    if (width == 1 and height == 1): return (least_x, least_y)
    left_x = least_x + int(-1 * width / 4)
    right_x = least_x + int( width / 4)
    top_y = least_y + int(-1 * height / 4)
    bottom_y = least_y + int(height / 4)
    least_error_location = (0, 0)
    top_left_error = calculate_pixel_error(pixels, left_x, top_y, math.sqrt(width ** 2 + height **  2) / 4, bias_array, image.width, image.height)
    top_right_error = calculate_pixel_error(pixels, right_x, top_y, math.sqrt(width ** 2 + height **  2) / 4, bias_array, image.width, image.height)
    bottom_left_error = calculate_pixel_error(pixels, left_x, bottom_y, math.sqrt(width ** 2 + height **  2) / 4, bias_array, image.width, image.height)
    #bottom_right_error = calculate_pixel_error(pixels, right_x, bottom_y, math.sqrt(width ** 2 + height **  2) / 4, bias_array, image.width, image.height)
    if (top_left_error > top_right_error):
        least_error_location[0] = 1
    if (top_left_error > bottom_left_error):
        least_error_location[1] = 1
    find_target_pixel(image, pixels, width / 4, height / 4, least_x + width / 2 * least_error_location[0], least_y + height / 2 * least_error_location[1], bias_array)
    return (0, 0)


def make_error_map(image, dist, bias_array):
    pixels = image.load()
    max_error = 0 #includes center
    pixel_error_array = [[0 for _ in range(image.width)] for _ in range(image.height)]

    #find max error
    # for x in range(max(int(-1 * image.width / 2), -dist), min(int(image.width / 2) - 1, dist)):
    #     for y in range (max(int(-1 * image.height / 2), -dist), min(int(image.height / 2) - 1, dist)):
    # for x in range(max(0, int(image.width / 2) - dist), min(int(image.width), int(image.width / 2) + dist + 1)):
    #     for y in range (max(0, int(image.height / 2) - dist), min(int(image.height), int(image.height / 2) + dist + 1)):
    #         if (math.sqrt((x - image.width / 2) ** 2 + (y - image.height / 2) ** 2) > dist):
    #             print("skipped " + str(x) + ", " + str(y))
    #             continue
    #         max_error += 765 * DISTANCE_BIAS * ((x - int(image.width / 2)) ** 2 + (y - int(image.height / 2)) ** 2) / dist
    #         if ((image.width / 2) + x > image.width or -1 * (image.width / 2) - x < 0):
    #             max_error += 765 * DISTANCE_BIAS * ((x - int(image.width / 2)) ** 2 + (y - int(image.height / 2)) ** 2) / dist
    #         if ((image.height / 2) + y > image.height or -1 * (image.height / 2) - y < 0):
    #             max_error += 765 * DISTANCE_BIAS * ((x - int(image.width / 2)) ** 2 + (y - int(image.height / 2)) ** 2) / dist
    # print(max_error)

    pixel_error = 0
    #find error / divide by max
    # for x in range(int(-1 * image.width / 2), int(image.width / 2)):
    #     print("current row: " + str(x))
    #     for y in range (int(-1 * image.height / 2), int(image.height / 2)):
    for x in range(0, image.width):
        print("current row: " + str(x))
        for y in range (0, image.height):
            #print("current column: " + str(y))
            if (x < 10 and y < 10): print(calculate_pixel_error(pixels, x, y, dist, bias_array, image.width, image.height))
            # pixel_error = int(calculate_pixel_error(pixels, x, y, dist, bias_array, image.width, image.height) / max_error * 255)
            pixel_error = int(calculate_pixel_error(pixels, x, y, dist, bias_array, image.width, image.height))
            pixel_error_array[x].insert(y, pixel_error)

    print(pixel_error_array[0][0])
    max_error = pixel_error_array[0][0]
    for x in range(0, image.width):
        for y in range (0, image.height):
            if (pixel_error_array[x][y] > max_error):
                max_error = pixel_error_array[x][y]

    print(max_error)

    for x in range(0, int(image.width)):
        for y in range (0, int(image.height)):
            pixels[x, y] = (int(pixel_error_array[x][y] / max_error * 255),
                            int(pixel_error_array[x][y] / max_error * 255),
                            int(pixel_error_array[x][y] / max_error * 255))

    image.save("results/error_map.jpg")
    image.show()


def make_bias_map(image, bias):
    pixels = image.load()

    for x in range(image.width):
        for y in range (image.height):
            pixels[x, y] = ((int(255 * (-math.sin(abs(x - (image.width / 2)) / image.width * math.pi / 2 * bias + math.pi / 2 - math.pi / 2 * bias)) + 1)),
                            (int(64 * (-math.sin(abs(x - (image.width / 2)) / image.width * math.pi / 2 * bias + math.pi / 2 - math.pi / 2 * bias)) + 1)) +
                            (int(64 * (-math.sin(abs(y - (image.height / 2)) / image.height * math.pi / 2 * bias + math.pi / 2 - math.pi / 2 * bias)) + 1)),
                            (int(255 * (-math.sin(abs(y - (image.height / 2)) / image.height * math.pi / 2 * bias + math.pi / 2 - math.pi / 2 * bias)) + 1)))
    image.save("results/bias_map.jpg")
    image.show()


def make_bias_array(image, bias):
    bias_array = [[]]
    for x in range(image.width):
        for y in range (image.height):
            bias_array[x].append((0, 0))
        bias_array.append([])

    for x in range(image.width):
        for y in range (image.height):
            bias_array[x].insert(y, 0.5 * (((-math.sin(abs(x - (image.width / 2)) / image.height * math.pi / 2 * bias + math.pi / 2 - math.pi / 2 * bias)) + 1) +
                                            ((-math.sin(abs(y - (image.height / 2)) / image.height * math.pi / 2 * bias + math.pi / 2 - math.pi / 2 * bias)) + 1)))

    return bias_array


if __name__ == "__main__":
    main()

"""
Bugs:
max error is incorrectly calculated
border error incorrectly (more noticable in image 1)
error divided into 4 distinct preferences (?)
check for when a loop should be incremented by 1 at the end

to find max error perform the same claculation as the center pixel, but pretend it is as far from the target as possible

alright pal ingnore the idiot above me, we arent goign to not calculate max error and insted, after finding each
pixels error, sort through and find the one with the most, and divide the rest by that

code to test error calculating without looping through entire image:
for x in range(px - dist, px + dist):
        for y in range (py - dist, py + dist):
            if (math.sqrt((x - px) ** 2 + (y - py) ** 2) > dist): continue
            try:
                individual_error = abs(bias_array[x][y] * (abs(p[x, y][0] - TARGET[0]) +
                                                abs(p[x, y][0] - TARGET[1]) +
                                                abs(p[x, y][0] - TARGET[2])) *
                                                DISTANCE_BIAS * ((x - px) ** 2 + (y - py) ** 2) / dist)
                sum_error += individual_error
            except:
                print("edge")
"""