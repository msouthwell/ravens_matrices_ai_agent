# DO NOT MODIFY THIS FILE.
#
# Any modifications to this file will not be used when grading your project.
# If you have any questions, please email the TAs.

# A single figure in a Raven's Progressive Matrix problem, comprised of a name
# and a list of RavensObjects.

import os

class RavensFigure:
    # Creates a new figure for a Raven's Progressive Matrix given a name.
    #
    # Your agent does not need to use this method.
    #
    # @param name the name of the figure
    def __init__(self, name, problemName, setName):
        # The name of the figure. The name of the figure will always match
        # the HashMap key for this figure.
        #
        # The figures in the problem will be named A, B, and C for 2x1 and 2x2
        # problems. The figures in the problem will be named A, B, C, D, E, F, G,
        # and H in 3x3 problems. The first row is A, B, and C; the second row is
        # D, E, and F; and the third row is G and H.
        #
        # Answer options will always be named 1 through 6.
        #
        # The numbers for the answer options will be randomly generated on each run
        # of the problem. The correct answer will remain the same, but its number
        # will change.
        self.name=name

        # A dictionary of RavensObjects from the figure. RavensObjects within a figure
        # are given random names that are used in spatial relationships among figures.
        # For example, objects["a"] would return the object named 'a'.
        self.objects={}

        # The filename where your agent can find the imagistic representation of this
        # figure as a .PNG file.
        self.visualFilename="Problems" + os.sep + setName + os.sep + problemName + os.sep + name + ".png"