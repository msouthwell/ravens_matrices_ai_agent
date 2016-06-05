# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
from PIL import Image
import  numpy as np
from itertools import product
import ufarray
# import logging, sys

# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# Code copied from https://github.com/spwhitt/cclabel/blob/master/cclabel.py
# I altered slightly to fit problem
# I attemted creating my own component labeling, but it was taking significant amounts of time
# Algorithm obtained from "Optimizing Two-Pass Connected-Component Labeling 
# by Kesheng Wu, Ekow Otoo, and Kenji Suzuki
#
def color_shapes(image):
    output = np.zeros(image.shape)
    width, height = image.shape
 
    # Union find data structure
    uf = ufarray.UFarray()
    uf.makeLabel()
    #
    # First pass
    #
 
    # Dictionary of point:label pairs
    labels = {}
 
    for y, x in product(range(height), range(width)):
 
        # If the current pixel is 0, it's obviously not a component...
        if image[x, y] == 0:
            pass
 
        elif y > 0 and image[x, y-1] == 1:
            labels[x, y] = labels[(x, y-1)]

        elif x+1 < width and y > 0 and image[x+1, y-1] == 1:
 
            c = labels[(x+1, y-1)]
            labels[x, y] = c

            if x > 0 and image[x-1, y-1] == 1:
                a = labels[(x-1, y-1)]
                uf.union(c, a)
 
            elif x > 0 and image[x-1, y] == 1:
                d = labels[(x-1, y)]
                uf.union(c, d)

        elif x > 0 and y > 0 and image[x-1, y-1] == 1:
            labels[x, y] = labels[(x-1, y-1)]

        elif x > 0 and image[x-1, y] == 1:
            labels[x, y] = labels[(x-1, y)]
 
        else: 
            labels[x, y] = uf.makeLabel()

    uf.flatten()

    for (i, j) in labels:

        # Name of the label the current point belongs to
        label = uf.find(labels[(i, j)])

        output[i, j] = label

    return output

def to_image_array(filename):
    image = Image.open(filename).convert("L") #opens image, converts to single channel grayscale
    im_data = np.asarray(image, dtype=np.uint8).T
    binary = np.zeros(im_data.shape)
    binary[np.where(im_data <= 128)] = 1 
    binary[np.where(im_data > 128)] = 0

    return binary

# The dilate function below was altered from the blog listed below
# http://blog.ostermiller.org/dilate-and-erode
# Changed bits are left as 2 to aid in erode the image
# dilate and erode are probably not really needed, but I did not want a possible isolated pixel to become its own object
def dilate(image):
    for (i, j) in product(range(image.shape[0]), range(image.shape[1])):
        if (image[i, j] == 1):
            if (image[i-1, j] == 0):
                image[i-1, j] = 2
            if (image[i, j-1] == 0):
                image[i, j-1] = 2
            if (i+1 < image.shape[0] and image[i+1, j] == 0):
                image[i+1, j] = 2
            if (j+1 < image.shape[1] and image[i, j+1] == 0):
                image[i, j+1] = 2
    return image

def erode(image):
    tmp = np.zeros(image.shape)
    for (i, j) in product(range(image.shape[0]), range(image.shape[1])):
        if (image[i, j] == 2):
            if (image[i-1, j] == 2):
                tmp[i-1, j] = 2
            if (image[i, j-1] == 2):
                tmp[i, j-1] = 2
            if (i+1 < image.shape[0] and image[i+1, j] == 2):
                tmp[i+1, j] = 2
            if (j+1 < image.shape[1] and image[i, j+1] == 2):
                tmp[i, j+1] = 2
    output = image - tmp
    output[np.where(output == 2)] = 1
    return output

class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    def create_nodes(self, figures):
        for figure_name in figures:
            this_figure = figures[figure_name]
            this_figure.frame = {}

            # Process the image for future operations
            array = to_image_array(this_figure.visualFilename)
            array = erode(dilate(array))  # morphological open to remove possible isolated pixels
            this_figure.frame["Image"] = color_shapes(array)
            this_figure.frame["Objects"] = {}

            # Seperate each shape into its own object
            for i in range(1, int(np.amax(this_figure.frame["Image"])) + 1):
                tmp = np.zeros(this_figure.frame["Image"].shape)
                # Set pixel back to 1 for future comparisons
                tmp[np.where(this_figure.frame["Image"] == i)] = 1
                if np.sum(tmp) == 0:
                    pass
                else:
                    obj = {}
                    obj["Shape Pixels"] = tmp
                    this_figure.frame["Objects"]["Object " + str(i)] = obj

            # Set pixel back to 1 for future comparisons
            this_figure.frame["Image"][np.where(this_figure.frame["Image"] > 1)] = 1

    def solve_two(self, problem):

        for figure_name in problem.figures:
            this_figure = problem.figures[figure_name]

            print("Figure " + figure_name)
            print("    Figure Pixel Total: " + str(np.sum(this_figure.frame["Image"])))
            if len(this_figure.frame["Objects"]) < 15:
                for shapes in this_figure.frame["Objects"]:
                    print("    " + str(shapes))
                    this_shape = this_figure.frame["Objects"][shapes]
                    print("           " + str(np.sum(this_shape["Shape Pixels"])))
            else:
                print("Too many shapes found, skip question")
                answer = -1



        # diff = np.sum(problem.figures["A"].frame["Image"]) / np.sum(problem.figures["B"].frame["Image"])

        # print("Difference between A and B is: " + str(diff))

        # answer = -1
        # temp = 100000000
        # for figure_name in problem.figures:
        #     if figure_name != "A" and figure_name != "B" and figure_name != "C":
        #         second_diff = np.sum(problem.figures["C"].frame["Image"]) / np.sum(problem.figures[figure_name].frame["Image"])
        #         print("Difference between C and " + figure_name + " is: " + str(second_diff))

        #         if abs(diff - second_diff) < temp:
        #             temp = abs(diff-second_diff)
        #             answer = figure_name

        # print(answer)

        return -1

    def solve_three(self, problem):

        return -1

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints 
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self, problem):

        print(problem.name)

        self.create_nodes(problem.figures)

        if problem.problemType == "2x2":
            answer = self.solve_two(problem)
        else:
            answer = self.solve_three(problem)

        return answer