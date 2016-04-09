# DO NOT MODIFY THIS FILE.
#
# Any modifications to this file will not be used when grading your project.
# If you have any questions, please email the TAs.

# A single Raven's Progressive Matrix problem, represented by a type (2x2
# or 3x3), a String name, and a dictionary of figures.
class RavensProblem:
    # Initializes a new Raven's Progressive Matrix problem given a name, a
    # type, and a correct answer to the problem. Also initializes a blank
    # dictionary representing the figures in the problem.
    #
    # Your agent does not need to use this method.
    def __init__(self, name, problemType, correctAnswer, hasVisual, hasVerbal):
        # The name of the problem, typically the set followed by an identifier,
        # such as "Basic Problem B-02".
        self.name=name

        # The type of problem, either 2x2 or 3x3.
        self.problemType=problemType

        # The correct answer to the problem, accessible only after supplying an
        # answer to the problem. Do NOT access this variable directly. Its name
        # will be changed during grading, and if you access it directly, your
        # code will crash. Only access the correct answer via the checkAnswer
        # method, supplied below.
        self.correctAnswer=correctAnswer

        # Whether or not the problem has visual representations available.
        self.hasVisual=hasVisual

        # Whether or not the problem has verbal representations available.
        self.hasVerbal=hasVerbal

        # The dictionary representing the RavensFigures of the problem. The
        # key for each figure is the name of the figure. For example:
        #
        # figures["A"] would return the first frame in a problem.
        # figures["3"] would return the third answer choice in a problem.
        # figures["G"] would return the third row, first column of a 3x3 problem.
        #
        # The value for each key is the RavensFigure corresponding to that figure
        # of the problem.
        #
        # In 2x2, the figures are named A, B, and C. A is to B as C is to one of
        # the answer choices. Similarly, A is to C as B is to one of the answer
        # choices. In 2x2 problems, relationships are present both across the rows
        # and down the columns. The answer choices are named 1 through 6.
        #
        # In 3x3, the figures in the first row are named from left to right A, B,
        # and C. The figures in the second row are named from left to right D, E,
        # and F. The figures in the third row are named from left to right G and H.
        # Relationships are present across rows and down columns: A is to B is to
        # C as D is to E is to F as G is to H is to one of the answer choices. A is
        # to D is G as B is to E is to H as C is to F is to one of the answer
        # choices. The answer choices are named 1 through 6.
        self.figures={}

        # Whether or not an answer has been received. As soon as your agent has
        # given an answer to this problem, answerReceived will be set to true.
        # Do NOT access answerReceived directly; its name will be changed during
        # grading and if you access it directly, your code will crash.
        self.answerReceived=False

        # Your agent's answer to this problem. Do NOT access this variable
        # directly. Its name will be changed during grading, and if you access it
        # directly, your code will crash. Only access the correct answer via the
        # checkAnswer method, supplied below, or by returning a number at the end
        # of your agent's Solve method.
        self.givenAnswer=-1

    # Returns the correct answer to the problem.
    #
    # In order to receive the correct answer to the problem, your Agent must
    # supply a guess (givenAnswer). Once it has supplied its guess, it will NOT
    # be able to change its answer to the problem; the answer passed as
    # givenAnswer will be stored as the answer to this problem.
    #
    # This method is provided to enable your Agent to participate in learning
    # and meta-reasoning by reflecting on its past incorrect answers. Using
    # this method is completely optional.
    def checkAnswer(self, givenAnswer):
        self.setAnswerReceived(givenAnswer)
        return self.correctAnswer

    # Sets your Agent's answer to this problem. This method can only be used
    # once; the first answer that is received will be stored. This method is
    # called by either checkAnswer or by the main() method.
    #
    # Your agent does not need to use this method.
    def setAnswerReceived(self, givenAnswer):
        if not self.answerReceived:
            self.answerReceived=True
            self.givenAnswer=int(givenAnswer)

    # Returns whether your Agent's answer is the correct answer. Your agent
    # does not need to use this method; it is used to identify whether each
    # problem is correct in main().
    #
    # Your agent does not need to use this method.
    def getCorrect(self):
        if self.givenAnswer==self.correctAnswer:
            return "Correct"
        elif self.givenAnswer<0:
            return "Skipped";
        else:
            return "Incorrect"

