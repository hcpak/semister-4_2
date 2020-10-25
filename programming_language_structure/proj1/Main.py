from Chario import Chario
from Scanner import Scanner
from Parser import Parser

# fileName = input("Enter the file name: ")
file = open("prog1.ada",'r')
# try:
#     file = open(fileName, 'r')
# except IOError as e:
#     print(e)

chario = Chario(file)
scanner = Scanner(chario)
# Parser = Parser(chario, scanner)

ch = chario.getChar()
index = 0
while ch != chr(26):

#     ch = chario.getChar()
# chario.reprotErrors()
