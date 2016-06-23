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

TOLERANCE = .20 # 20% needed for problem 6
IMAGE_INTENSITY = 1  
OBJECT_THRESHOLD = 150
UNCHANGED_W = 0
FILLED_W = 1
ROTATED_W = 2
DELETED_W = 10
ADDED_W = 10
FILLED_W = 3




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

def object_unchanged(a, b, tol=TOLERANCE):
    diff = (np.sum(abs(a["Shape Pixels"] - b["Shape Pixels"]))) / np.sum(a["Shape Pixels"])
    if diff <= TOLERANCE:
        print("Shapes the same with difference: " + str(diff))
        return "UNCHANGED"
    else:
        return -1

def object_rotated(a, b):
    c = copy.copy(a)
    for i in range(1,4):
        c["Shape Pixels"] = np.rot90(c["Shape Pixels"])
        unchanged = object_unchanged(c, b)      
        if unchanged == "UNCHANGED":
            if i == 3:
                return str("ROTATED_90") 
            else:
                return str("ROTATED_" + str(i *90))
    return -1

def object_filled(a, b):
    # print("Entered object_filled")
    # tmp = {}
    # tmp["Shape Pixels"] = fill(b["Shape Pixels"])

    # transform = object_unchanged(a, tmp, tol=TOLERANCE_FILL)
    # if  transform == "UNCHANGED":
    #     return "FILLED"
    # else:
    #     tmp["Shape Pixels"] = fill(a["Shape Pixels"])
    #     transform = object_unchanged(b, tmp, tol=TOLERANCE_FILL)
    #     if transform == "UNCHANGED":
    #         return "FILLED"
    #     else:
    #         return -1
    return -1

class Node:
    '''Holds information about each object inside a raven figure'''

    def __init__(self):
        pass

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
            this_figure.frame["Objects"] = Node()

            # Seperate each shape into its own object
            for i in range(1, int(np.amax(this_figure.frame["Image"])) + 1):
                tmp = np.zeros(this_figure.frame["Image"].shape)

                # Set pixel back to IMAGE_INTENSITY rather than its 'color'
                tmp[np.where(this_figure.frame["Image"] == i)] = IMAGE_INTENSITY

                if np.sum(tmp) <= OBJECT_THRESHOLD: 
                    logging.warning("Found an object with " + str(np.sum(tmp)) + "pixels, passed")
                    pass
                else:
                    obj = {}
                    obj["Shape Pixels"] = tmp
                    obj["Matched to"] = "none"
                    obj["Transform"] = "not matched"
                    obj["Matched Weight"] = 0
                    this_figure.frame["Objects"]["Object " + str(i)] = obj
                    # test_image = Image.fromarray(tmp)
                    # test_image.show()

            # Set uncolor component images
            this_figure.frame["Image"][np.where(this_figure.frame["Image"] > 1)] = IMAGE_INTENSITY

    # method that sets objects frame values
    def match(self, a, b, transform):
        if transform == "DELETED":
            a["Transform"] = transform
        elif transform == "ADDED":
            b["Transform"] = transform
        else:
            a["Transform"] = transform
            a["Matched to"] = str(b)
            b["Matched to"] = str(a)
            b["Transform"] = transform

    def match_objects(self, fig_a, fig_b):
        # print("Entered match_objects")
        # print("Frame: " + str(fig_a.name))
        # print("Frame: " + str(fig_b.name))
        for a in fig_a.frame["Objects"]:
            for b in fig_b.frame["Objects"]:
                a_object = fig_a.frame["Objects"][a]
                b_object = fig_b.frame["Objects"][b]

                if a_object["Matched to"] == "none":
                    a_object["Matched Weight"] = 0
                if b_object["Matched to"] == "none":
                    b_object["Matched Weight"] = 0

                while True:
                    transform = "no transform"
                    if (a_object["Matched Weight"] and b_object["Matched Weight"]) == UNCHANGED_W:
                        transform = object_unchanged(a_object, b_object)
                        if transform == "UNCHANGED": 
                            self.match(a_object, b_object, transform)
                            break 
                        else: 
                            a_object["Matched Weight"] += 1
                            b_object["Matched Weight"] += 1
                    elif (a_object["Matched Weight"] <= ROTATED_W) and (b_object["Matched Weight"] <= ROTATED_W):
                        transform = object_rotated(a_object, b_object)
                        if (transform == "ROTATED_90") or (transform == "ROTATED_180") or (transform == "ROTATED_270"): 
                            self.match(a_object, b_object, transform)
                            break 
                        else: 
                            a_object["Matched Weight"] += 1
                            b_object["Matched Weight"] += 1
                    elif (a_object["Matched Weight"] <= FILLED_W) and (b_object["Matched Weight"] <= FILLED_W):
                        transform = object_filled(a_object, b_object)
                        if transform == "FILLED": 
                            self.match(a_object, b_object, transform)
                            break 
                        else: 
                            a_object["Matched Weight"] += 1
                            b_object["Matched Weight"] += 1
                    else:
                        break

        # print("object X length " + str(len(fig_a.frame["Objects"])))
        # print("object Y length " + str(len(fig_b.frame["Objects"])))

        #######
        # Checks for added or deleted objects
        for a in fig_a.frame["Objects"]:
            for b in fig_b.frame["Objects"]:
                a_object = fig_a.frame["Objects"][a]
                b_object = fig_b.frame["Objects"][b]
                if (len(fig_a.frame["Objects"]) > len(fig_b.frame["Objects"])) and a_object["Matched to"] == "none":
                    a_object["Transform"] = "DELETED"
                elif (len(fig_a.frame["Objects"]) < len(fig_b.frame["Objects"])) and b_object["Matched to"] == "none":
                    b_object["Transform"] = "ADDED"

    def array_transforms(self, a, b):
        transforms = []
        for i in a:
            a_object = a[i]
            transforms.append(a_object["Transform"])

        for i in b:
            b_object = b[i]
            transforms.append(b_object["Transform"])

        return transforms

    def reset_frame_objects(self, a):
        for i in a:
            obj = a[i]
            obj["Transform"] = "not matched"
            obj["Matched to"] = "none"
            obj["Matched Weight"] = 0

    def solve_two(self, problem):

        answer = -1
        confidence = 999
        semantic_net = {}

        # Get transformation from A to B

        if self.match_objects(problem.figures["A"], problem.figures["B"]) == -1:
            print("Skipping question")
            return -1

        problem.horz_relation = self.array_transforms(problem.figures["A"].frame["Objects"], problem.figures["B"].frame["Objects"])
        problem.horz_relation_size_diff = len(problem.figures["A"].frame["Objects"]) - len(problem.figures["B"].frame["Objects"])
        self.reset_frame_objects(problem.figures["A"].frame["Objects"])
        self.reset_frame_objects(problem.figures["B"].frame["Objects"])

        # Get transformation from A to C
        if self.match_objects(problem.figures["A"], problem.figures["C"]) == -1:
            print("Skipping questions")
            return -1

        problem.vert_relation = self.array_transforms(problem.figures["A"].frame["Objects"], problem.figures["C"].frame["Objects"])
        problem.vert_relation_size_diff = len(problem.figures["A"].frame["Objects"]) - len(problem.figures["C"].frame["Objects"])
        self.reset_frame_objects(problem.figures["A"].frame["Objects"])
        self.reset_frame_objects(problem.figures["C"].frame["Objects"])

        problem.horz_relation.sort()
        problem.vert_relation.sort()
        if problem.horz_relation[0] == "not matched" and problem.vert_relation[0] == "not matched":
            print("Skipping questions")
            return -1
        # print(problem.horz_relation)
        # print(problem.vert_relation)

        for i in range(1,7):
            if self.match_objects(problem.figures["C"], problem.figures[str(i)]) != -1:
                semantic_net["C", str(i)] = self.array_transforms(problem.figures["C"].frame["Objects"], problem.figures[str(i)].frame["Objects"])
            if  self.match_objects(problem.figures["B"], problem.figures[str(i)]) != -1:
                semantic_net["B", str(i)] = self.array_transforms(problem.figures["B"].frame["Objects"], problem.figures[str(i)].frame["Objects"])
            self.reset_frame_objects(problem.figures["B"].frame["Objects"])
            self.reset_frame_objects(problem.figures["C"].frame["Objects"])
            self.reset_frame_objects(problem.figures[str(i)].frame["Objects"])

        # for net in semantic_net:
        #     semantic_net[net].sort()
        #     print(str(net) + "  : " + str(semantic_net[net]))

        for fig_i, fig_j in semantic_net:
            obj_number_diff = len(problem.figures[fig_i].frame["Objects"]) - len(problem.figures[fig_j].frame["Objects"])
            if semantic_net[("C", fig_j)] == problem.horz_relation and problem.vert_relation == semantic_net["B", fig_j]:
                answer = fig_j
                confidence = 0

            elif semantic_net[("C", fig_j)] == problem.horz_relation:
                if confidence > 10:
                    answer = fig_j
                    confidence = 10

            elif semantic_net[("B", fig_j)] == problem.vert_relation:
                if confidence > 20:
                    answer = fig_j
                    confidence = 10
            elif (len(problem.figures["C"].frame["Objects"]) - len(problem.figures[fig_j].frame["Objects"])) == problem.horz_relation_size_diff:
                if confidence > 30:
                    answer = fig_j
            elif (len(problem.figures["B"].frame["Objects"]) - len(problem.figures[fig_j].frame["Objects"])) == problem.vert_relation_size_diff:
                if confidence > 30:
                    answer = fig_j



        print ("Answer is : " + str(answer))
        return int(answer)

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

        logging.info(problem.name)

        # add properties to the problem

        problem.horz_relation = []  # TODO: is an array the best way to represent this
        problem.vert_relation = []


        self.create_nodes(problem.figures)



        if problem.problemType == "2x2":
            answer = self.solve_two(problem)
        else:
            answer = self.solve_three(problem)

        return answer


