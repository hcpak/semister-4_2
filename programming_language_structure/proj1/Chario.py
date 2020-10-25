from Token import Token

class Chario(object):
    EL = '\n'
    EF = chr(26)
    TAB = '\t'
    sourceProgram = ""
    line = ""
    totalErrors: int
    column: int
    lineNumber: int


    def __init__(self, file):

        self.sourceProgram = ""
        self.readFile(file)
        self.reset()

    def reset(self):
        self.totalErrors = 0
        self.lineNumber = 0
        self.column = 0
        self.line = ""

    def println(self, s):
        print(s)

    def makeSpaces(self, number):
        string = ""
        for i in range(number):
            string += " "
        return string

    def putError(self, message):
        self.totalErrors += 1
        spaces = self.makeSpaces(self.column)
        print(spaces + "ERROR > " + message)

    def reprotErrors(self):
        print("\nCompilation complete.")
        if self.totalErrors == 0:
            print("No errors reported")
        elif self.totalErrors == 1:
            print("1 error reported")
        else:
            print(self.totalErrors + " errors reported")

    def getChar(self):
        if(self.column >= len(self.line)):
            self.nextLine()

        ch = self.line[self.column]

        self.column += 1
        return ch

    def nextLine(self):

        self.column = 0
        self.line = self.getLine()
        if self.line[0] != self.EF:
            self.lineNumber += 1
            print(str(self.lineNumber) + " > " + self.line)


    def getLine(self):
        ln = ""
        if self.sourceProgram.__eq__(""):
            ln = "" + self.EF
        else:
            first = self.sourceProgram.find(self.EL)
            last = len(self.sourceProgram)
            if first == -1:
                ln = self.sourceProgram + self.EL
                self.sourceProgram = ""
            else:
                ln = self.sourceProgram[:first + 1]
                self.sourceProgram = self.sourceProgram[first + 1 : last]

        return ln

    def readFile(self, file):
        try:
            data = file.readline()
            while(1):
                data = file.readline()
                if not data:
                    break
                self.sourceProgram += data
            file.close()


        except IOError as e:
            print("Error in file input" + e)


# #
# while 1:
#     s = file.readline()
#     if not s:
#         break
#     print(s, end="")