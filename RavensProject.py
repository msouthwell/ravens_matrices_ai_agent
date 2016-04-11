# DO NOT MODIFY THIS FILE.
#
# Any modifications to this file will not be used when grading your project.
# If you have any questions, please email the TAs.
#
#

import os
import sys
import csv
from Agent import Agent
from ProblemSet import ProblemSet

def outcome(truth, answer):
    if truth==answer:
        return "Correct"
    elif answer < 0:
        return "Skipped"
    else:
        return "Incorrect" 

def getNextLine(r):
    return r.readline().rstrip()

# Reads answers from answers_file and outputs outcomes for individual
# problems in ProblemResults.csv and set summaries in SetResults.csv
def grade(answersFile):
    answers = {}

    with open(answersFile) as fd:
        reader = csv.DictReader(fd)
        for row in reader:
            if row['ProblemSet'] in answers:
                answers[row['ProblemSet']][row['RavensProblem']] = int(row["Agent's Answer"])
            else:
                answers[row['ProblemSet']] = {row['RavensProblem']: int(row["Agent's Answer"])}


    results=open("ProblemResults.csv","w")
    results.write("Problem,Agent's Answer,Correct?,Correct Answer\n")

    setResults=open("SetResults.csv","w")      
    setResults.write("Set,Correct,Incorrect,Skipped\n")

    with open(os.path.join("Problems", "ProblemSetList.txt")) as fd0:
        for line0 in fd0:
            line0 = line0.rstrip()
            totals = {"Correct": 0, "Skipped": 0, "Incorrect": 0}
            with open(os.path.join("Problems", line0, "ProblemList.txt")) as fd1:
                for line1 in fd1:
                    line1 = line1.rstrip()
                    with open(os.path.join("Problems", line0, line1, "ProblemAnswer.txt")) as fd2:
                        truth = int(fd2.read())
                        ans = answers[line0][line1]
                        results.write("%s,%d,%s,%d\n" % (line1, ans, outcome(truth, ans), truth))
                        totals[outcome(truth, ans)] += 1
            setResults.write("%s,%d,%d,%d\n" % (line0, totals["Correct"], totals["Incorrect"], totals["Skipped"]))

    results.close()
    setResults.close()


def solve(problemSetList):
    sets=[] # The variable 'sets' stores multiple problem sets.
            # Each problem set comes from a different folder in /Problems/
            # Additional sets of problems will be used when grading projects.
            # You may also write your own problems.

    r = open("Problems" + os.sep + "ProblemSetList.txt")    # ProblemSetList.txt lists the sets to solve.
    line = getNextLine(r)                                   # Sets will be solved in the order they appear in the file.
    while not line=="":                                     # You may modify ProblemSetList.txt for design and debugging.
        sets.append(ProblemSet(line))                       # We will use a fresh copy of all problem sets when grading.
        line=getNextLine(r)                                 # We will also use some problem sets not given in advance.

    # Initializing problem-solving agent from Agent.java
    agent=Agent()   # Your agent will be initialized with its default constructor.
                    # You may modify the default constructor in Agent.java

    # Running agent against each problem set
    with open("StudentAnswers.csv","w") as results:     # Results will be written to ProblemResults.csv.
                                                        # Note that each run of the program will overwrite the previous results.
                                                        # Do not write anything else to ProblemResults.txt during execution of the program.
        results.write("ProblemSet,RavensProblem,Agent's Answer\n")
        for set in sets:
            for problem in set.problems:   # Your agent will solve one problem at a time.
                #try:
                answer = agent.Solve(problem)  # The problem will be passed to your agent as a RavensProblem object as a parameter to the Solve method
                                                # Your agent should return its answer at the conclusion of the execution of Solve.

                results.write("%s,%s,%d\n" % (set.name, problem.name, answer))


# The main driver file for Project2. You may edit this file to change which
# problems your Agent addresses while debugging and designing, but you should
# not depend on changes to this file for final execution of your project. Your
# project will be graded using our own version of this file.
def main():

    solve("Problems" + os.sep + "ProblemSetList.txt")
    grade("StudentAnswers.csv")

if __name__ == "__main__":
    main()