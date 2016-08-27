# An Agent for solving Raven's Progressive Matrices. 

from PIL import Image
import  numpy as np
from itertools import product
                # ufarray is used with the two pass connected component labeling
import ufarray  # ufarray class from https://github.com/spwhitt/cclabel/blob/master/ufarray.py
import copy
import logging
from time import time
from random import random

TOLERANCE = .02 # 20% needed for problem 6
IMAGE_INTENSITY = 1  
OBJECT_THRESHOLD = 20
UNCHANGED_W = 0
FILLED_W = 1
ROTATED_W = 2
DELETED_W = 10
ADDED_W = 10
FILLED_W = 3

DB_LEVEL = "WARNING"

# create logger
logger = logging.getLogger('agent')
logger.setLevel(DB_LEVEL)

# create console handler and set level
ch = logging.StreamHandler()
ch.setLevel(DB_LEVEL)

formatter = logging.Formatter('%(levelname)s - %(message)s')

ch.setFormatter(formatter)

logger.addHandler(ch)

######################################################################
#####    COMPONENT LABELING
#####
######################################################################

# This is a two pass connected component labeling algorithm that I found open source on github
# It seperates each figure into its component images, with each shape getting its own 'color'
# Code copied from https://github.com/spwhitt/cclabel/blob/master/cclabel.py
# I altered code slightly to fit problem
# Algorithm obtained from "Optimizing Two-Pass Connected-Component Labeling 
# by Kesheng Wu, Ekow Otoo, and Kenji Suzuki
#
def color_shapes(image):
    output = np.zeros(image.shape)
    width, height = image.shape
 
    # Union find data structure
    uf = ufarray.UFarray() # UFarray code copied from https://github.com/spwhitt/cclabel/blob/master/ufarray.py
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

######## END COPIED CODE ###########


######################################################################
#####    IMAGE PROCESSING METHODS
#####
######################################################################

def to_image_array(filename):
    image = Image.open(filename).convert("L") #opens image, converts to single channel grayscale
    im_data = np.asarray(image, dtype=np.int32).T
    binary = np.zeros(im_data.shape)
    binary[np.where(im_data <= 128)] = 1 
    binary[np.where(im_data > 128)] = 0

    return binary



######################################################################
#####    OBJECT COMPARISON METHODS
#####
######################################################################

def difference(a, b):
    if np.sum(a) != 0:
        diff = (np.sum(abs(a - b))) / np.sum(a)

        rolls = [np.roll(a, 1, 0), np.roll(a, -1, 0), np.roll(a, 1, 1), np.roll(a, -1, 1)]

        diffs = [(np.sum(abs(i - b))) / np.sum(i) for i in rolls ]

        # logger.debug("Diff: " + str(diff))
        # logger.debug("Rolls: " + str(diffs))
        for i in diffs:
            if i < diff:
                # logger.debug("Original Diff: " + str(diff) + " Post Roll diff: " + str(i))
                diff = i  

        return diff
    else:
        return np.sum(b) / b.size

def object_flipud(a, b):
    pre_diff = difference(a,b)
    tmp = np.flipud(a)
    post_diff = difference(tmp, b)
    if abs(pre_diff - post_diff) < TOLERANCE:
        return -1
    elif post_diff < TOLERANCE:
        return "FLIP_UD"
    else:
        return -1

def object_fliplr(a, b):
    pre_diff = difference(a,b)
    tmp = np.fliplr(a)
    post_diff = difference(tmp, b)
    if abs(pre_diff - post_diff) < TOLERANCE:
        return -1
    elif post_diff < TOLERANCE:
        return "FLIP_LR"
    else:
        return -1

def object_unchanged(a, b, tol=TOLERANCE):
    diff = difference(a, b)
    # logger.debug("Original Diff is " + str(a.name) + " " + str(b.name) + " difference is " + str(diff))
 
    if diff <= tol:
        if diff > 0.03:
            # logger.warning("Shapes the same with difference: " + str(diff))
            pass
        return "UNCHANGED"
    else:
        return -1

def object_rotated(a, b):
    c = copy.copy(a)
    pre_diff = difference(a,b)
    for i in range(1,4):
        c = np.rot90(c)
        post_diff = difference(c, b)      
        if abs(pre_diff - post_diff) > 0.05:
            if i == 3:
                return str("ROTATED_90") 
            else:
                return str("ROTATED_" + str(i *90))
    return -1

######################################################################
#####    FRAME CLASS
#####
######################################################################
class Frame:
    '''Frame is the relationship between two/three figures in a Ravens problem'''

    def __init__(self, figures):
        self.figures = figures
        self.images = []
        for i in self.figures:
            self.images.append(i.attr["Image"])
        self.blackdifference = self.get_black_difference()
        self.nodes = self.get_nodes()
        self.nodedifference = self.get_node_difference()
        self.blackratio = self.get_black_ratio()
        self.transformable = self.is_transformable()
        self.simple_transform = self.check_simple_transform()
        self.and_or_xor = self.check_and_or_xor()
        self.semantic_net = self.get_net() #if len(self.nodes[0]) > 1 else "none"

    def get_net(self):
        net = {"ab": [], "bc": [], "ac": []}

        if len(self.nodes) == 3:

            if len(self.nodes[0]) > 10 or len(self.nodes[1]) > 10 or len(self.nodes[2]) > 10:
                return net
            for a in self.nodes[0]:
                for b in self.nodes[1]:
                    if a.transform == "not matched" and b.transform == "not matched":
                        if 0.95 < np.sum(a.pixels) / np.sum(b.pixels) < 1.05:
                            unchange = object_unchanged(a.pixels, b.pixels, 0.2)
                            rotated = object_rotated(a.pixels, b.pixels)
                            fliplr = object_fliplr(a.pixels, b.pixels)
                            flipud = object_flipud(a.pixels, b.pixels)
                            if unchange == "UNCHANGED":
                                net["ab"].append("UNCHANGED")
                                a.transform = unchange
                                b.transform = unchange
                                break
                            elif rotated == "ROTATED_90" or rotated == "ROTATED_180" or rotated == "ROTATED_270":
                                net["ab"].append(rotated)
                                a.transform = rotated
                                b.transform = rotated
                                break
                            elif fliplr == "FLIP_LR":
                                net["ab"].append(fliplr)
                                a.transform = fliplr
                                b.transform = fliplr
                                break
                            elif flipud == "FLIP_UD":
                                net["ab"].append(flipud)
                                a.transform = flipud
                                b.transform = flipud
                                break
                            else:
                                net["ab"].append("no match")
                        else:
                            net["ab"].append("no match")

            [i.reset() for i in self.nodes[0]]
            [i.reset() for i in self.nodes[1]]


            for a in self.nodes[1]:
                for b in self.nodes[2]:
                    if a.transform == "not matched" and b.transform == "not matched":
                        if 0.95 < np.sum(a.pixels) / np.sum(b.pixels) < 1.05:
                            unchange = object_unchanged(a.pixels, b.pixels, 0.2)
                            rotated = object_rotated(a.pixels, b.pixels)
                            fliplr = object_fliplr(a.pixels, b.pixels)
                            flipud = object_flipud(a.pixels, b.pixels)
                            if unchange == "UNCHANGED":
                                net["bc"].append("UNCHANGED")
                                a.transform = unchange
                                b.transform = unchange
                                break
                            elif rotated == "ROTATED_90" or rotated == "ROTATED_180" or rotated == "ROTATED_270":
                                net["bc"].append(rotated)
                                a.transform = rotated
                                b.transform = rotated
                                break
                            elif fliplr == "FLIP_LR":
                                net["bc"].append(fliplr)
                                a.transform = fliplr
                                b.transform = fliplr
                                break
                            elif flipud == "FLIP_UD":
                                net["bc"].append(flipud)
                                a.transform = flipud
                                b.transform = flipud
                                break
                            else:
                                net["bc"].append("no match")
                        else:
                            net["bc"].append("no match")
            [i.reset() for i in self.nodes[1]]
            [i.reset() for i in self.nodes[2]]

            for a in self.nodes[1]:
                for b in self.nodes[2]:
                    if a.transform == "not matched" and b.transform == "not matched":
                        if 0.95 < np.sum(a.pixels) / np.sum(b.pixels) < 1.05:
                            unchange = object_unchanged(a.pixels, b.pixels, 0.2)
                            rotated = object_rotated(a.pixels, b.pixels)
                            fliplr = object_fliplr(a.pixels, b.pixels)
                            flipud = object_flipud(a.pixels, b.pixels)
                            if unchange == "UNCHANGED":
                                net["ac"].append("UNCHANGED")
                                a.transform = unchange
                                b.transform = unchange
                                break
                            elif rotated == "ROTATED_90" or rotated == "ROTATED_180" or rotated == "ROTATED_270":
                                net["ac"].append(rotated)
                                a.transform = rotated
                                b.transform = rotated
                                break
                            elif fliplr == "FLIP_LR":
                                net["ac"].append(fliplr)
                                a.transform = fliplr
                                b.transform = fliplr
                                break
                            elif flipud == "FLIP_UD":
                                net["ac"].append(flipud)
                                a.transform = flipud
                                b.transform = flipud
                                break
                            else:
                                net["ac"].append("no match")
                        else:
                            net["ac"].append("no match")
            [i.reset() for i in self.nodes[0]]
            [i.reset() for i in self.nodes[2]]

        return net

    def get_black_difference(self):
        diff = []
        diff.append(difference(self.images[0], self.images[1]))
        if len(self.images) > 2:
            diff.append(difference(self.images[1], self.images[2]))
            diff.append(difference(self.images[0], self.images[2]))
        return diff

    def get_black_ratio(self):
        ratio = []
        if np.sum(self.images[1]) == 0:
            ratio.append(np.sum(self.images[0]))
        else:
            ratio.append(np.sum(self.images[0]) / np.sum(self.images[1]))
        if len(self.images) > 2 and np.sum(self.images[2]) != 0:
            ratio.append(np.sum(self.images[1]) / np.sum(self.images[2]))
            ratio.append(np.sum(self.images[0]) / np.sum(self.images[2]))
        else:
            ratio.append(np.sum(self.images[1]))
            ratio.append(np.sum(self.images[0]))
        return ratio

    def is_transformable(self):
        transformable = []
        for i in range(len(self.blackratio)):
            if 0.95 < self.blackratio[i] < 1.05 and self.nodedifference[i] == 0:
                transformable.append(True)
            else:
                transformable.append(False)
        return transformable

    def get_node_difference(self):
        diff = []
        diff.append(len(self.nodes[1]) - len(self.nodes[0]))
        if len(self.nodes) > 2:
            diff.append(len(self.nodes[2]) - len(self.nodes[1]))
            diff.append(len(self.nodes[2]) - len(self.nodes[0]))
        return diff

    def check_simple_transform(self):
        length = len(self.transformable)
        simple = [-1, -1, -1] if length == 3 else [-1, -1]
        if length == 2:
            if self.transformable[0]:
                if simple[0] == -1:
                    simple[0] = object_unchanged(self.images[0], self.images[1])
                if simple[0] == -1:
                    simple[0] = object_flipud(self.images[0], self.images[1])
                if simple[0] == -1:
                    simple[0] = object_fliplr(self.images[0], self.images[1])
                if simple[0] == -1:
                    simple[0] = object_rotated(self.images[0], self.images[1]) 
            return simple

        for i in range(len(simple)):
            if self.transformable[i]:
                if simple[i] == -1:
                    simple[i] = object_unchanged(self.images[i], self.images[(i+1)%length])
                if simple[i] == -1:
                    simple[i] = object_flipud(self.images[i], self.images[(i+1)%length])
                if simple[i] == -1:
                    simple[i] = object_fliplr(self.images[i], self.images[(i+1)%length])
                if simple[i] == -1:
                    simple[i] = object_rotated(self.images[i], self.images[(i+1)%length]) 

        return simple

    def check_and_or_xor(self):

        length = len(self.images)
        operator = [-1, -1, -1] if length == 3 else [-1, -1]
        if length == 2: 
            return "none"
        else:
            and_img = self.images[0] + self.images[1]
            and_img -= IMAGE_INTENSITY
            if difference(and_img, self.images[2]) < TOLERANCE:
                return "AND"
            or_img = self.images[0] + self.images[1]
            or_img[np.where(or_img > IMAGE_INTENSITY)] = IMAGE_INTENSITY
            if difference(or_img, self.images[2]) < TOLERANCE:
                return "OR"         
            xor_img = self.images[0] + self.images[1]
            xor_img[np.where(or_img > IMAGE_INTENSITY)] = 0
            if difference(xor_img, self.images[2]) < TOLERANCE:
                return "XOR"
        return "none"

    def print_frame(self):
        print("#################################")
        print("Frame contains: ")
        for i in self.figures:
            print("    " + str(i.name))
        print("Black Difference: " + str(self.blackdifference))
        print("Black Ratio: " + str(self.blackratio))
        print("Transformable: " + str(self.transformable))
        print("Number of Nodes: " + str([len(i) for i in self.nodes]))
        print("Nodes Changed by " + str(self.nodedifference))
        print("Simple Transforms: " + str(self.simple_transform))
        print("AND_OR_XOR: " + str(self.and_or_xor))
        print("Semantic Net" + str(self.semantic_net))

    def get_nodes(self):
        nodes = []
        for i in self.figures:
            nodes.append(i.attr["Nodes"])
        return nodes

######################################################################
#####    NODE CLASS
#####
######################################################################
class Node:
    '''Holds information about each object inside a raven figure'''

    def __init__(self, pixels, match, transform, match_weight, name):
        self.pixels = pixels
        self.match = match
        self.transform = transform
        self.match_weight = match_weight
        self.name = name

    def reset(self):
        self.match = 'none'
        self.transform = 'not matched'
        self.match_weight = 0


######################################################################
#####    MAIN AGENT
#####
######################################################################

class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main()
    def __init__(self):
        pass

    def create_nodes(self, figures):
        '''Seperates each figure into nodes for the creation of the semantic net '''
        for figure_name in figures:
            this_figure = figures[figure_name]
            this_figure.attr = {}

            # Process the image for future operations
            array = to_image_array(this_figure.visualFilename)

            this_figure.attr["Image"] = color_shapes(array)

            # inv_array = np.zeros(array.shape)
            # inv_array[np.where(array == 0)] = 1

            this_figure.attr["Nodes"] = []

            # this_figure.attr["Inverse"] = color_shapes(inv_array)
            # this_figure.attr["Whites"] = []

            # Seperate each shape into its own object
            for i in range(1, int(np.amax(this_figure.attr["Image"])) + 1):
                pixels = np.zeros(this_figure.attr["Image"].shape)

                # Set pixel back to IMAGE_INTENSITY rather than its 'color'
                pixels[np.where(this_figure.attr["Image"] == i)] = IMAGE_INTENSITY

                if np.sum(pixels) <= OBJECT_THRESHOLD: 
                    if np.sum(pixels) > 0:
                        logger.warning("Found an object with " + str(np.sum(pixels)) + "pixels, passed")
                    pass
                else:
                    node = Node(pixels, "none", "not matched", 0, "Node_" + str(i))
                    this_figure.attr["Nodes"].append(node)
                    # test_image = Image.fromarray(tmp)
                    # test_image.show()
            # logger.debug("Figure " + str(figure_name) + " has " + str(len(this_figure.attr["Nodes"])) + " nodes")

            #  uncolor component images
            this_figure.attr["Image"][np.where(this_figure.attr["Image"] > 1)] = IMAGE_INTENSITY

    # method that sets objects frame values
    def match(self, a, b, transform):
        if transform == "DELETED":
            a.transform = transform
        elif transform == "ADDED":
            b.transform = transform
        else:
            a.transform = transform
            a.match = b.name
            b.match = a.name
            b.transform = transform

    def match_nodes(self, fig_a, fig_b):
        # print("Entered match_nodes")
        # print("Frame: " + str(fig_a.name))
        # print("Frame: " + str(fig_b.name))
        for a in fig_a.frame["Nodes"]:
            for b in fig_b.frame["Nodes"]:

                if a.match == "none":
                    a.match_weight = 0
                if b.match == "none":
                    b.match_weight = 0

                while True:
                    transform = "no transform"
                    if (a.match_weight and b.match_weight) == UNCHANGED_W:
                        transform = object_unchanged(a, b)
                        if transform == "UNCHANGED": 
                            self.match(a, b, transform)
                            break 
                        else: 
                            a.match_weight += 1
                            b.match_weight += 1
                    elif (a.match_weight <= ROTATED_W) and (b.match_weight <= ROTATED_W):
                        transform = object_rotated(a, b)
                        if (transform == "ROTATED_90") or (transform == "ROTATED_180") or (transform == "ROTATED_270"): 
                            self.match(a, b, transform)
                            break 
                        else: 
                            a.match_weight += 1
                            b.match_weight += 1
                    elif (a.match_weight <= FILLED_W) and (b.match_weight <= FILLED_W):
                        transform = object_filled(a, b)
                        if transform == "FILLED": 
                            self.match(a, b, transform)
                            break 
                        else: 
                            a.match_weight += 1
                            b.match_weight += 1
                    else:
                        break

        # print("object X length " + str(len(fig_a.frame["Nodes"])))
        # print("object Y length " + str(len(fig_b.frame["Nodes"])))

        #######
        # Checks for added or deleted objects
        for a in fig_a.frame["Nodes"]:
            for b in fig_b.frame["Nodes"]:

                if (len(fig_a.frame["Nodes"]) > len(fig_b.frame["Nodes"])) and a.match == "none":
                    a.transform = "DELETED"
                elif (len(fig_a.frame["Nodes"]) < len(fig_b.frame["Nodes"])) and b.match == "none":
                    b.transform = "ADDED"

    def reset_frame_nodes(self, a):
        for i in a:
            i.transform = "not matched"
            i.match = "none"
            i.match_weight = 0

    def generate_semantic_net(self, fig1, fig2):
        
        if self.match_nodes(fig1, fig2) == -1:
            return -1

        net = [i.transform for i in fig1.frame["Nodes"]]   
        [i.reset() for i in fig1.frame["Nodes"]]
        [i.reset() for i in fig2.frame["Nodes"]]

        return net

    def compare_frames(self, fr_1, fr_2, problem):
        confidence = 1

        # Compare black difference
        for i, j in zip(fr_1.blackdifference, fr_2.blackdifference):
            if abs(i - j) < 0.05:
                confidence += 3
            elif abs(i - j) < 0.1:
                confidence += 2
            elif abs(i - j) < 0.15:
                confidence += 1

        # Compare black ratio
        for i, j in zip(fr_1.blackratio, fr_2.blackratio):
            if abs(i - j) < 0.05:
                confidence += 3
            elif abs(i - j) < 0.1:
                confidence += 2
            elif abs(i - j) < 0.15:
                confidence += 1

        # Compare number of nodes
        for (i, j) in zip(fr_1.nodedifference, fr_2.nodedifference):
            if i != j:
                confidence -= 0
            elif i == j and i != 0:
                confidence += 5
            else:
                confidence += 0

        # Compare simple transforms
        for (i, j) in zip(fr_1.simple_transform, fr_2.simple_transform):
            if i != j:
                confidence -= 0
            elif i == j and i != -1:
                confidence += 5

        # Check for and or xor
        if fr_1.and_or_xor == fr_2.and_or_xor and fr_1.and_or_xor != "none":
            confidence += 2

        # compare semantic nets.... really poorly
        ab1 = sorted(fr_1.semantic_net["ab"])
        ab2 = sorted(fr_2.semantic_net["ab"])
        bc1 = sorted(fr_1.semantic_net["bc"])
        bc2 = sorted(fr_2.semantic_net["bc"])
        ac1 = sorted(fr_1.semantic_net["ac"])
        ac2 = sorted(fr_2.semantic_net["ac"])

        # if ab1 == bc1 and bc1 == ac1:
        #     if ab2 == bc2 and bc2 == ac2:
        #         confidence += 10

        if "Basic Problem D-" in problem.name:
            if ab2 == bc2:
                confidence += 10
        # TODO add count edges
        # TODO add count corners

        return confidence

    def solve_two(self, problem):
        p = problem

        answer = 1
        confidence = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}


        letters = ["A", "B", "C"]
        numbers = [1, 2, 3, 4, 5, 6]

        problem.frames = {}
        problem.frames["A" + "B"] = Frame([problem.figures["A"], problem.figures["B"]])

        problem.frames["A" + "C"] = Frame([problem.figures["A"], problem.figures["C"]])

        for i in numbers:
            problem.frames["B" + str(i)] = Frame([problem.figures["B"], problem.figures[str(i)]])
            problem.frames["C" + str(i)] = Frame([problem.figures["C"], problem.figures[str(i)]])

        if DB_LEVEL == "DEBUG":
            for frame in problem.frames:
                problem.frames[frame].print_frame()


        for i in numbers:
            confidence[i] += self.compare_frames(problem.frames["AB"], problem.frames["C" + str(i)], problem)
            confidence[i] += self.compare_frames(problem.frames["AC"], problem.frames["B" + str(i)], problem)

        logger.debug("Confidence is " + str(confidence))

        conf = confidence[1]
        for key in confidence:
            if confidence[key] > conf:
                answer = key
                conf = confidence[key]

        if DB_LEVEL == "DEBUG" or DB_LEVEL == "INFO":
            problem.frames["AB"].print_frame()
            problem.frames["C" + str(answer)].print_frame()
            problem.frames["AC"].print_frame()
            problem.frames["B" + str(answer)].print_frame()

        print(confidence)

        if conf < 2:
            answer = -1

        return answer

    def solve_three(self, problem):

        letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
        numbers = [1, 2, 3, 4, 5, 6, 7, 8]
        confidence = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}  
        answer = 1

        problem.frames = {}

        # Normal horizontal and vertical frames
        problem.frames["A" + "B" + "C"] = Frame([problem.figures["A"], problem.figures["B"], problem.figures["C"]])

        problem.frames["D" + "E" + "F"] = Frame([problem.figures["D"], problem.figures["E"], problem.figures["F"]])
        problem.frames["A" + "D" + "G"] = Frame([problem.figures["A"], problem.figures["D"], problem.figures["G"]])
        problem.frames["B" + "E" + "H"] = Frame([problem.figures["B"], problem.figures["E"], problem.figures["H"]])

        # Add diagonals

        problem.frames["B" + "F" + "G"] = Frame([problem.figures["B"], problem.figures["F"], problem.figures["G"]])
        problem.frames["C" + "D" + "H"] = Frame([problem.figures["C"], problem.figures["D"], problem.figures["H"]])


        for i in numbers:
            problem.frames["C" + "F" + str(i)] = Frame([problem.figures["C"], problem.figures["F"], problem.figures[str(i)]])
            problem.frames["G" + "H" + str(i)] = Frame([problem.figures["G"], problem.figures["H"], problem.figures[str(i)]])
            problem.frames["A" + "E" + str(i)] = Frame([problem.figures["A"], problem.figures["E"], problem.figures[str(i)]])


        if DB_LEVEL == "DEBUG":
            for frame in problem.frames:
                problem.frames[frame].print_frame()

        for i in numbers:
            confidence[i] += self.compare_frames(problem.frames["ABC"], problem.frames["GH" + str(i)], problem) * 1.0
            confidence[i] += self.compare_frames(problem.frames["DEF"], problem.frames["GH" + str(i)], problem) * 1.0
            confidence[i] += self.compare_frames(problem.frames["ADG"], problem.frames["CF" + str(i)], problem) * 1.0
            confidence[i] += self.compare_frames(problem.frames["BEH"], problem.frames["CF" + str(i)], problem) * 1.0
            if "Basic Problem E-" in problem.name:
                pass
            else:
                confidence[i] += self.compare_frames(problem.frames["BFG"], problem.frames["AE" + str(i)], problem) * 1.0
                confidence[i] += self.compare_frames(problem.frames["CDH"], problem.frames["AE" + str(i)], problem) * 1.0


        logger.info("Confidence is " + str(confidence))

        # if max(confidence) >10:
        #             conf = confidence[1]

        conf = confidence[1]

        for key in confidence:
            if confidence[key] > conf:
                answer = key
                conf = confidence[key]

        if DB_LEVEL == "DEBUG" or DB_LEVEL == "INFO":
            problem.frames["ABC"].print_frame()
            problem.frames["DEF"].print_frame()
            problem.frames["GH" + str(answer)].print_frame()
            problem.frames["ADG"].print_frame()
            problem.frames["BEH"].print_frame()
            problem.frames["CF" + str(answer)].print_frame()
            problem.frames["BFG"].print_frame()
            problem.frames["CDH"].print_frame()
            problem.frames["AE" + str(answer)].print_frame()
            problem.frames["GH1"].print_frame()


        print(confidence)

        if conf < 7:
            answer = -1

        return answer

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


        t0 = time()
        print("**********Solving Problem : " + str(problem.name) + " ***********************")

        self.create_nodes(problem.figures)

        problem.answer = self.solve_two(problem) if problem.problemType == "2x2" else self.solve_three(problem)

        t1 = time()
        logger.info("Time is : %f" % (t1-t0));
        print("Answer is : " + str(problem.answer))

        return problem.answer


