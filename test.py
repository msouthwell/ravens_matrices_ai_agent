from itertools import product
import numpy as np
from ufarray import *

image = np.array([[1, 0, 0, 0, 0, 0, 0, 0],
				  [0, 0, 1, 1, 1, 0, 0, 0],
				  [1, 0, 1, 0, 1, 0, 1, 0],
				  [0, 0, 1, 1, 1, 0, 1, 1],
				  [0, 1, 0, 0, 0, 0, 0, 0]])

def object_rotated(a, b):
    print("Testing for object rotated")
    c = a
    for i in range(1,4):
        print(i)
        c = np.rot90(c)
        print(c)
        if object_unchanged(c, b):
            return str("ROTATED_" + str(i*90))
    return -1

# The dilate function below was altered from the blog listed below
# # http://blog.ostermiller.org/dilate-and-erode
# # Changed bits are left as 2 to aid in erode the image
# # dilate and erode are probably not really needed, but it prevents an isolated pixel from becoming its own object
# def dilate(image):
#     for (i, j) in product(range(image.shape[0]), range(image.shape[1])):
#         if (image[i, j] == 1):
#             if (image[i-1, j] == 0):
#                 image[i-1, j] = 2
#             if (image[i, j-1] == 0):
#                 image[i, j-1] = 2
#             if (i+1 < image.shape[0] and image[i+1, j] == 0):
#                 image[i+1, j] = 2
#             if (j+1 < image.shape[1] and image[i, j+1] == 0):
#                 image[i, j+1] = 2
#     return image

# def erode(image):
#     tmp = np.zeros(image.shape)
#     for (i, j) in product(range(image.shape[0]), range(image.shape[1])):
#         if (image[i, j] == 2):
#             if (image[i-1, j] == 2):
#                 tmp[i-1, j] = 2
#             if (image[i, j-1] == 2):
#                 tmp[i, j-1] = 2
#             if (i+1 < image.shape[0] and image[i+1, j] == 2):
#                 tmp[i+1, j] = 2
#             if (j+1 < image.shape[1] and image[i, j+1] == 2):
#                 tmp[i, j+1] = 2
#     output = image - tmp
#     output[np.where(output == 2)] = 1
#     return output
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
    uf = UFarray()
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
 
        # If pixel b is in the image and 1:
        #    a, d, and c are its neighbors, so they are all part of the same component
        #    Therefore, there is no reason to check their labels
        #    so simply assign b's label to e
        elif y > 0 and image[x, y-1] == 1:
            labels[x, y] = labels[(x, y-1)]
 
        # If pixel c is in the image and 1:
        #    b is its neighbor, but a and d are not
        #    Therefore, we must check a and d's labels
        elif x+1 < width and y > 0 and image[x+1, y-1] == 1:
 
            c = labels[(x+1, y-1)]
            labels[x, y] = c
 
            # If pixel a is in the image and 1:
            #    Then a and c are connected through e
            #    Therefore, we must union their sets
            if x > 0 and image[x-1, y-1] == 1:
                a = labels[(x-1, y-1)]
                uf.union(c, a)
 
            # If pixel d is in the image and 1:
            #    Then d and c are connected through e
            #    Therefore we must union their sets
            elif x > 0 and image[x-1, y] == 1:
                d = labels[(x-1, y)]
                uf.union(c, d)
 
        # If pixel a is in the image and 1:
        #    We already know b and c are white
        #    d is a's neighbor, so they already have the same label
        #    So simply assign a's label to e
        elif x > 0 and y > 0 and image[x-1, y-1] == 1:
            labels[x, y] = labels[(x-1, y-1)]
 
        # If pixel d is in the image and 1
        #    We already know a, b, and c are white
        #    so simpy assign d's label to e
        elif x > 0 and image[x-1, y] == 1:
            labels[x, y] = labels[(x-1, y)]
 
        # All the neighboring pixels are white,
        # Therefore the current pixel is a new component
        else: 
            labels[x, y] = uf.makeLabel()

    uf.flatten()

    for (i, j) in labels:

        # Name of the label the current point belongs to
        label = uf.find(labels[(i, j)])

        # # Update the labels with correct information
        # labels[(i, j)] = label

        output[i, j] = label

    return output

# def color_shapes(image):
# 	current_label = 1
# 	labels = {}
# 	output = np.zeros(image.shape)

# 	uf = UFarray()

# 	for (i, j) in product(range(image.shape[0]), range(image.shape[1])):
# 		if (image[i, j] == 1):
# 			if j > 0 and image[(i, j-1)] > 0:
# 				labels[i, j] = labels[(i, j-1)]
# 			elif i + 1 < image.shape[0] and j > 0 and image[(i + 1, j - 1)] > 0:
# 				c = labels[(i + 1, j - 1)]
# 				labels[i, j] = c
# 				if i > 0 and image[(i-1, j-1)] > 0:
# 					uf.union(c, labels[(i-1, j-1)])
# 				elif i > 0 and image[(i - 1, j)] > 0:
# 					uf.union(c, labels[(i - 1, j)])
# 			elif i > 0 and j > 0 and image[(i-1, j-1)] > 0:
# 				labels[i, j] = labels[(i-1, j-1)]	
# 			elif i > 0 and j < image.shape[1] and image[(i -1, j)] > 0:
# 				labels[i, j] = labels[(i -1, j)]
# 			else:
# 				labels[i, j] = current_label
# 				current_label += 1

# 	uf.flatten()

# 	for (i, j) in labels:

# 		# Name of the label the current point belongs to
# 		label = uf.find(labels[(i, j)])

# 		# # Update the labels with correct information
# 		# labels[(i, j)] = label

# 		output[i, j] = labels

# 	return output

# The dilate function below was altered from the blog listed below
# http://blog.ostermiller.org/dilate-and-erode

def dilate(image):
    for (i, j) in product(range(image.shape[0]), range(image.shape[1])):
        if (image[i, j] == 1):
            if (image[i-1,j]==0):
            	image[i-1,j] = 2
            if (image[i,j-1]==0):
            	image[i,j-1] = 2
            if (i+1<image.shape[0] and image[i+1,j]==0):
            	image[i+1,j] = 2
            if (j+1<image.shape[1] and image[i,j+1]==0):
            	image[i,j+1] = 2        
    return image

# def erode(image):
# 	tmp = np.zeros(image.shape)
#     for (i, j) in product(range(image.shape[0]), range(image.shape[1])):
# 		if (image[i, j] == 2):
# 			if (image[i-1,j]==2):
# 				tmp[i-1,j] = 2
# 			if (image[i,j-1]==2):
# 				tmp[i,j-1] = 2
# 			if (i+1<image.shape[0] and image[i+1,j]==2):
# 				tmp[i+1,j] = 2
# 			if (j+1<image.shape[1] and image[i,j+1]==2):
# 				tmp[i,j+1] = 2
# 	output = image - tmp
# 	output[np.where(output == 2)] = 1
# 	return output
print(np.rot90(image))
# print(color_shapes(image))