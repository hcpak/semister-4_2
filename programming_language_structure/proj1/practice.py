file = open("prog1.ada", 'r')

while 1:
    s = file.readline()
    if not s:
        break
    print(s, end="")
    