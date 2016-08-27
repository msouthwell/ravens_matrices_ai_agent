# Raven's Progressive Matrices (RPM) AI Agent

This project was developed for the Knowledge-Based Artificial Intelligence course as Georgia Tech.  The purpose was to design an artificial intelligence agent that was capable of solving the RPM intelligence test.  The RPM intelligence test is a test comprised of a 3 x 3 matrix of images.  Based on the relationship between the figures, a person (or agent) needs to determine which image best completes the matrix.

![RPM Example] (Problems/Challenge Problems E/Challenge Problem E-07/Challenge Problem E-07.PNG)

For this project I was restricted from using any third-party image processing libraries (ie. no OpenCV), thus my agent relied on basic image transformations and pixel analysis.

The problems solved by the agent get progressively harder, starting with simple problems in the `Basic Problems B` set up to the `Challenge Problems E` set. 

## Agent problem solving process

The agent functions by separating each raven figure in a problem into its component shape objects using a connected-component labeling algorithm.  These objects become the nodes in each figure.  It then creates frames for each relationship between Raven's figures (ie. Frame ABC, Frame DEF, Frame GH6…).  Each frame compared its corresponding figures for simple transforms, the percentage of black difference in each image, and the number of nodes in each image. Next each horizontal and vertical relationship frames are compared against each possible answer frame.  Each answer has a confidence number starting at zero.  As each answer relationship is matched against each horizontal and vertical relationship its confidence goes up or down.  The answer with the highest confidence is the correct answer.


## Running the Agent

The main agent code is located in `Agent.py`.  The rest of the files were provided as part of the assignment.

To run the project:

`python RavensProject.py`

Results will be stored in: `SetResults.csv` and `ProblemResults.csv`

To edit which problems are solved edit the `Problems/problemSetList.txt` file

