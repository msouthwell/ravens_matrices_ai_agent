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

# create console handler and set level to WARNING
ch = logging.StreamHandler()
ch.setLevel(DB_LEVEL)

# create formatter
formatter = logging.Formatter('%(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

######################################################################
#####    COMPONENT LABELING
#####
######################################################################

# This is a two pass connected component labeling algorithm that I found open source on github
# It seperates each figure into its component images, with each shape getting its own 'color'
# Code copied from https://github.com/spwhitt/cclabel/blob/master/cclabel.py
# I altered code slightly to fit problem
# I attempted creating my own component labeling, but it was taking significant amounts of time
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
            logger.warning("Shapes the same with difference: " + str(diff))
        return "UNCHANGED"
    else:
        return -1

#### Old object_unchanged
# def object_unchanged(a, b, tol=TOLERANCE):
#     diff = difference(a.pixels, b.pixels)
#     # logger.debug("Original Diff is " + str(a.name) + " " + str(b.name) + " difference is " + str(diff))
#     rolls = [np.roll(a.pixels, 1, 0), np.roll(a.pixels, -1, 0), np.roll(a.pixels, 1, 1), np.roll(a.pixels, -1, 1)]

#     diffs = [difference(i, b.pixels) for i in rolls ]

#     for i in diffs:
#         if i < diff and i < tol:
#             logger.debug("Original Diff: " + str(diff) + " Post Roll diff: " + str(i))
#             diff = i  
#     if diff <= tol:
#         if diff > 0.10:
#             logger.warning("Shapes the same with difference: " + str(diff))
#         return "UNCHANGED"
#     else:
#         return -1

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

###### Semantic net old object rotated code
# def object_rotated(a, b):
#     c = copy.copy(a)
#     for i in range(1,4):
#         c.pixels = np.rot90(c.pixels)
#         unchanged = object_unchanged(c, b)      
#         if unchanged == "UNCHANGED":
#             if i == 3:
#                 return str("ROTATED_90") 
#             else:
#                 return str("ROTATED_" + str(i *90))
#     return -1


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
            self.images.append(i.frame["Image"])
        self.blackdifference = self.get_black_difference()
        self.simple_transform = self.check_simple_transform()
        self.nodes = self.get_nodes()
        self.nodedifference = self.get_node_difference()

    def get_black_difference(self):
        diff = []
        diff.append(difference(self.images[0], self.images[1]))
        if len(self.images) > 2:
            diff.append(difference(self.images[1], self.images[2]))
            diff.append(difference(self.images[0], self.images[2]))
        return diff

    def get_node_difference(self):
        diff = []
        diff.append(len(self.nodes[1]) - len(self.nodes[0]))
        if len(self.nodes) > 2:
            diff.append(len(self.nodes[2]) - len(self.nodes[1]))
            diff.append(len(self.nodes[2]) - len(self.nodes[0]))
        return diff

    def check_simple_transform(self):
        simple = []
        if len(self.figures) == 3:
            simple = [-1, -1, -1]
            for i in range(3):
                if simple[i] == -1:
                    simple[i] = object_unchanged(self.images[i], self.images[(i+1)%3])
                if simple[i] == -1:
                    simple[i] = object_flipud(self.images[i], self.images[(i+1)%3])
                if simple[i] == -1:
                    simple[i] = object_fliplr(self.images[i], self.images[(i+1)%3])
                if simple[i] == -1:
                    simple[i] = object_rotated(self.images[i], self.images[(i+1)%3])

        return simple

    def print_frame(self):
        print("#################################")
        print("Frame contains: ")
        for i in self.figures:
            print("    " + str(i.name))
        print("Black Difference: " + str(self.blackdifference))
        print("Number of Nodes: " + str([len(i) for i in self.nodes]))
        print("Nodes Changed by " + str(self.nodedifference))
        print("Simple Transforms: " + str(self.simple_transform))

    def get_nodes(self):
        nodes = []
        for i in self.figures:
            nodes.append(i.frame["Nodes"])
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
    # main().
    def __init__(self):
        pass

    def create_nodes(self, figures):
        '''Seperates each figure into nodes for the creation of the semantic net '''
        for figure_name in figures:
            this_figure = figures[figure_name]
            this_figure.frame = {}

            # Process the image for future operations
            array = to_image_array(this_figure.visualFilename)

            this_figure.frame["Image"] = color_shapes(array)
            this_figure.frame["Nodes"] = []

            # Seperate each shape into its own object
            for i in range(1, int(np.amax(this_figure.frame["Image"])) + 1):
                pixels = np.zeros(this_figure.frame["Image"].shape)

                # Set pixel back to IMAGE_INTENSITY rather than its 'color'
                pixels[np.where(this_figure.frame["Image"] == i)] = IMAGE_INTENSITY

                if np.sum(pixels) <= OBJECT_THRESHOLD: 
                    if np.sum(pixels) > 0:
                        logger.warning("Found an object with " + str(np.sum(pixels)) + "pixels, passed")
                    pass
                else:
                    node = Node(pixels, "none", "not matched", 0, "Node_" + str(i))
                    this_figure.frame["Nodes"].append(node)
                    # test_image = Image.fromarray(tmp)
                    # test_image.show()
            # logger.debug("Figure " + str(figure_name) + " has " + str(len(this_figure.frame["Nodes"])) + " nodes")

            # Set uncolor component images
            this_figure.frame["Image"][np.where(this_figure.frame["Image"] > 1)] = IMAGE_INTENSITY

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

    def solve_two(self, problem):
        p = problem
        logger.info("####### Solving 2x2: " + str(p.name))

        answer = -1
        confidence = [0, 0, 0, 0, 0, 0]


        letters = ["A", "B", "C"]
        numbers = [1, 2, 3, 4, 5, 6]

        problem.frames = {}
        problem.frames["A" + "B"] = Frame([problem.figures["A"], problem.figures["B"]])

        problem.frames["A" + "C"] = Frame([problem.figures["A"], problem.figures["C"]])

        for i in numbers:
            problem.frames["B" + str(i)] = Frame([problem.figures["B"], problem.figures[str(i)]])
            problem.frames["C" + str(i)] = Frame([problem.figures["C"], problem.figures[str(i)]])

        # for frame in problem.frames:
        #     problem.frames[frame].print_frame()


        for i in numbers:
            confidence[i-1] += self.compare_frames(problem.frames["AB"], problem.frames["C" + str(i)])
            confidence[i-1] += self.compare_frames(problem.frames["AC"], problem.frames["B" + str(i)])

        logger.debug("Confidence is " + str(confidence))
        s_conf = copy.copy(confidence)
        s_conf.sort()
        if abs(s_conf[5] - s_conf[4]) > 0:
            answer = confidence.index(max(confidence)) + 1
        else:
            answer = -1
            logger.warning("Skipping Question, unconfident")
        return answer

        # # Get transformation from A to B

        # p.horz_relation = self.generate_semantic_net(p.figures["A"], p.figures["B"])
        # p.horz_relation_size_diff = len(p.figures["A"].frame["Nodes"]) - len(p.figures["B"].frame["Nodes"])

        # p.vert_relation = self.generate_semantic_net(p.figures["A"], p.figures["C"])
        # p.vert_relation_size_diff = len(p.figures["A"].frame["Nodes"]) - len(p.figures["C"].frame["Nodes"])

        # p.horz_relation.sort()
        # p.vert_relation.sort()

        # if p.horz_relation == -1 and p.vert_relation == -1:
        #     logger.warning("Semantic Net Failed")

        # logger.info("Horizontal: " + str(p.horz_relation))
        # logger.info("Vertical:   " + str(p.vert_relation))

        # for i in range(1,7):
        #     if self.match_nodes(p.figures["C"], p.figures[str(i)]) != -1:
        #         p.semantic_net["C", str(i)] = [i.transform for i in p.figures["C"].frame["Nodes"]]
        #     if  self.match_nodes(p.figures["B"], p.figures[str(i)]) != -1:
        #         p.semantic_net["B", str(i)] = [i.transform for i in p.figures["B"].frame["Nodes"]]
        #     self.reset_frame_nodes(p.figures["B"].frame["Nodes"])
        #     self.reset_frame_nodes(p.figures["C"].frame["Nodes"])
        #     self.reset_frame_nodes(p.figures[str(i)].frame["Nodes"])

        # # for net in p.semantic_net:
        # #     p.semantic_net[net].sort()
        # #     print(str(net) + "  : " + str(p.semantic_net[net]))

        # for i in range(1,7):

        #     if p.semantic_net["C", str(i)] == p.horz_relation and p.vert_relation == p.semantic_net["B", str(i)]:
        #         answer = i
        #         p.confidence = 0

        #     elif p.semantic_net["C", str(i)] == p.horz_relation:
        #         if p.confidence > 10:
        #             answer = i
        #             p.confidence = 10

        #     elif p.semantic_net["B", str(i)] == p.vert_relation:
        #         if p.confidence > 20:
        #             answer = i
        #             p.confidence = 10
        #     elif (len(p.figures["C"].frame["Nodes"]) - len(p.figures[str(i)].frame["Nodes"])) == p.horz_relation_size_diff:
        #         if p.confidence > 30:
        #             answer = i
        #     elif (len(p.figures["B"].frame["Nodes"]) - len(p.figures[str(i)].frame["Nodes"])) == p.vert_relation_size_diff:
        #         if p.confidence > 30:
        #             answer = i

        return int(answer)

    def compare_frames(self, fr_1, fr_2):
        confidence = 1

        # Compare black difference
        for i, j in zip(fr_1.blackdifference, fr_2.blackdifference):
            if i == j:
                confidence += 10
            elif abs(i - j) < 0.1:
                confidence += 5
            elif abs(i - j) < 0.25:
                confidence += 2

        # Compare number of nodes
        for (i, j) in zip(fr_1.nodedifference, fr_2.nodedifference):
            if i != j:
                confidence -= 5
            elif i == j and i != 0:
                confidence += 10
            else:
                confidence += 5

        # Compare simple transforms
        for (i, j) in zip(fr_1.simple_transform, fr_2.simple_transform):
            if i != j:
                confidence -= 5
            elif i == j and i != -1:
                confidence += 10

        return confidence

    def solve_three(self, problem):

        logger.info("######### Solving 3x3: " + str(problem.name))

        letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
        numbers = [1, 2, 3, 4, 5, 6, 7, 8]
        confidence = [0, 0, 0, 0, 0, 0, 0, 0]

        problem.frames = {}

        # Normal horizontal and vertical frames
        problem.frames["A" + "B" + "C"] = Frame([problem.figures["A"], problem.figures["B"], problem.figures["C"]])

        problem.frames["D" + "E" + "F"] = Frame([problem.figures["D"], problem.figures["E"], problem.figures["F"]])
        problem.frames["A" + "D" + "G"] = Frame([problem.figures["A"], problem.figures["D"], problem.figures["G"]])
        problem.frames["B" + "E" + "H"] = Frame([problem.figures["B"], problem.figures["E"], problem.figures["H"]])


        for i in numbers:
            problem.frames["C" + "F" + str(i)] = Frame([problem.figures["C"], problem.figures["F"], problem.figures[str(i)]])
            problem.frames["G" + "H" + str(i)] = Frame([problem.figures["G"], problem.figures["H"], problem.figures[str(i)]])

        if DB_LEVEL == "DEBUG":
            for frame in problem.frames:
                problem.frames[frame].print_frame()

        for i in numbers:
            confidence[i-1] += self.compare_frames(problem.frames["ABC"], problem.frames["GH" + str(i)])
            confidence[i-1] += self.compare_frames(problem.frames["DEF"], problem.frames["GH" + str(i)])
            confidence[i-1] += self.compare_frames(problem.frames["ADG"], problem.frames["CF" + str(i)])
            confidence[i-1] += self.compare_frames(problem.frames["BEH"], problem.frames["CF" + str(i)])


        logger.info("Confidence is " + str(confidence))

        if max(confidence) >10:
            answer = confidence.index(max(confidence)) + 1
        else:
            logger.info("Trying new confidence")
            confidence2 = [0, 0, 0, 0, 0, 0, 0, 0]
            # Diagonal frames
            problem.frames["B" + "F" + "G"] = Frame([problem.figures["B"], problem.figures["F"], problem.figures["G"]])
            problem.frames["C" + "D" + "H"] = Frame([problem.figures["C"], problem.figures["D"], problem.figures["H"]])

            for i in numbers:
                problem.frames["A" + "E" + str(i)] = Frame([problem.figures["A"], problem.figures["D"], problem.figures[str(i)]])

            for i in numbers:
                confidence2[i-1] += self.compare_frames(problem.frames["BFG"], problem.frames["AE" + str(i)])
                confidence2[i-1] += self.compare_frames(problem.frames["CDH"], problem.frames["AE" + str(i)])

            answer = confidence2.index(max(confidence2)) + 1
            logger.info("Confidence2 is " + str(confidence2))




        # s_conf = copy.copy(confidence)
        # m1 = max(confidence)
        # i1 = confidence.index(m1)
        # s_conf.remove(m1) 
        # m2 = max(s_conf)
        # i2 = confidence.index(m2)
        # if abs(m1 - m2) > 0:
        #     answer = confidence.index(max(confidence)) + 1
        # else:
        #     if random() > 0.5:
        #         answer = i2 + 1
        #     else:
        #         answer = i1 + 1
        #     logger.warning("Guessing Question, unconfident")
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
        # # add properties to the problem object

        # problem.horz_relation = []  # TODO: is an array the best way to represent this
        # problem.vert_relation = []
        # problem.semantic_net = {}
        # problem.confidence = 999 # TODO: Implement a confidence level if needed?
        problem.answer = -1

        self.create_nodes(problem.figures)

        problem.answer = self.solve_two(problem) if problem.problemType == "2x2" else self.solve_three(problem)

        t1 = time()
        logger.debug("Time is : %f" % (t1-t0));
        logger.info("Answer is : " + str(problem.answer))

        return problem.answer


