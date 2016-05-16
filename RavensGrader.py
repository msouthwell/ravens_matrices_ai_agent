# DO NOT MODIFY THIS FILE.
#
# Any modifications to this file will not be used when grading your project.
# If you have any questions, please email the TAs.
#
# This file grades the answers your agent submits.

import os
import csv

def outcome(truth, answer):
    if truth==answer:
        return "Correct"
    elif answer < 0:
        return "Skipped"
    else:
        return "Incorrect" 

# Reads answers from answers_file and outputs outcomes for individual
# problems in ProblemResults.csv and set summaries in SetResults.csv
def grade():
    answers = {}

    with open("AgentAnswers.csv") as fd:
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