from Token import Token
from Chario import Chario 
MAX_KEY_SPELLING = 9


class Scanner:
    keywords = dict()
    single_ops = dict()
    double_ops = dict()
    token = Token
    token_buffer = ""

    def __init__(self, c):
        self.Chario = c
        self.keywords = self.init_keywords()
        self.single_ops = self.init_single_ops()
        self.double_ops = self.init_double_ops()
        self.ch = self.Chario.getChar()
        # self.ch = "a"

    def reset(self):
        self.Chario.reset()
        ch = self.Chario.getChar()
        pass

    def init_keywords(self):
        self.keywords = dict()
        self.keywords["AND"] = Token(Token.AND)
        self.keywords["ARRAY"] = Token(Token.ARRAY)
        self.keywords["BEGIN"] = Token(Token.BEGIN)
        self.keywords["CONSTANT"] = Token(Token.CONST)
        self.keywords["ELSE"] = Token(Token.ELSE)
        self.keywords["ELSIF"] = Token(Token.ELSIF)
        self.keywords["END"] = Token(Token.END)
        self.keywords["EXIT"] = Token(Token.EXIT)
        self.keywords["IF"] = Token(Token.IF)
        self.keywords["IN"] = Token(Token.IN)
        self.keywords["IS"] = Token(Token.IS)
        self.keywords["LOOP"] = Token(Token.LOOP)
        self.keywords["MOD"] = Token(Token.MOD)
        self.keywords["NOT"] = Token(Token.NOT)
        self.keywords["NULL"] = Token(Token.NULL)
        self.keywords["OF"] = Token(Token.OF)
        self.keywords["OR"] = Token(Token.OR)
        self.keywords["OUT"] = Token(Token.OUT)
        self.keywords["PROCEDURE"] = Token(Token.PROC)
        self.keywords["RANGE"] = Token(Token.RANGE)
        self.keywords["THEN"] = Token(Token.THEN)
        self.keywords["TYPE"] = Token(Token.TYPE)
        self.keywords["WHEN"] = Token(Token.WHEN)
        self.keywords["WHILE"] = Token(Token.WHILE)
        return self.keywords

    def init_single_ops(self):
        self.single_ops = dict()
        self.single_ops[":"] = Token(Token.COLON)
        self.single_ops[","] = Token(Token.COMMA)
        self.single_ops["="] = Token(Token.EQ)
        self.single_ops[">"] = Token(Token.GT)
        self.single_ops["<"] = Token(Token.LT)
        self.single_ops["("] = Token(Token.L_PAR)
        self.single_ops["-"] = Token(Token.MINUS)
        self.single_ops["*"] = Token(Token.MUL)
        self.single_ops["/"] = Token(Token.DIV)
        self.single_ops["+"] = Token(Token.PLUS)
        self.single_ops[")"] = Token(Token.R_PAR)
        self.single_ops[";"] = Token(Token.SEMI)
        return self.single_ops

    def init_double_ops(self):
        self.double_ops = dict()
        self.double_ops["**"] = Token(Token.EXPO)
        self.double_ops[">="] = Token(Token.GE)
        self.double_ops[":="] = Token(Token.GETS)
        self.double_ops["<="] = Token(Token.LE)
        self.double_ops["/="] = Token(Token.NE)
        self.double_ops[".."] = Token(Token.THRU)
        return self.double_ops

    def find_token(self, table, target):
        return table[target] if target in table else Token(Token.ERROR)

    def skip_blanks(self):
        while self.ch == ' ' or self.ch == self.Chario.EL or self.ch == self.Chario.TAB:
            self.ch = self.Chario.getChar()

    def get_identifier_or_keyword(self):
        i = bar_count = 0
        id = token_buffer = ""
        token = Token(Token.ID)
        if self.ch == '_':
            self.Chario.put_error("illegal leading '_'")
        while True:
            self.ch = self.ch.upper()
            i += 1
            token_buffer += self.ch
            if i <= MAX_KEY_SPELLING:
                id += self.ch
            if self.ch == '_':
                self.ch = self.Chario.getChar()
                if self.ch == '_':
                    bar_count += 1
                if not self.ch.isalnum() and self.ch != '_':
                    self.Chario.put_error("letter or digit expected after '_'")
            else:
                self.ch = self.Chario.getChar()
            if not self.ch.isalnum() and self.ch != '_':
                break
        if bar_count > 0:
            self.Chario.put_error("letter or digit expected after '_'")
        if i <= MAX_KEY_SPELLING:
            token = self.find_token(self.keywords, id)
            if token.code == Token.ERROR:
                token.code = Token.ID
        if token.code == Token.ID:
            token.string = str(token_buffer)

    def get_integer(self):
        base = 16
        self.token = Token(Token.INT)
        self.get_based_integer(10)
        if self.ch == '#':
            base = self.token.integer
            if base < 2 or base > 16:
                self.Chario.put_error("base must be between 2 and 16")
                base = 16
            self.ch = self.Chario.getChar()
            if not self.ch.isalnum():
                self.Chario.put_error("letter or digit expected after '#'")
            self.get_based_integer()
            if self.ch == '#':
                self.ch = self.Chario.getChar()
            else:
                self.Chario.put_error("'#' expected")

    def get_based_integer(self, base):
        bar_count = 0
        self.token.integer = 0
        while self.ch.isalnum() or self.ch == '_':
            if self.ch == '_':
                self.ch = self.Chario.getChar()
                if self.ch == '_':
                    bar_count += 1
                if not self.ch.isalnum() and self. ch != '_':
                    self.Chario.put_error("letter or digit expected after '_'")
            else:
                self.token.integer = base * self.token.integer + charToInt(self.ch, base)
                self.ch = self.Chario.getChar()
        if bar_count > 0:
            self.Chario.put_error("letter or digit expected after '_'")

    def char_to_int(self, ch, base):
        digit = int(ch, base)
        if digit == -1:
            self.Chario.put_error("digit not in range of base")
            digit = 0
        return digit

    def char_to_digit(self, ch, base):
        try:
            temp = int(ch, base)
            return temp
        except:
            return -1

    def get_character(self):
        self.token = Token(Token.CHAR)
        self.ch = self.Chario.getChar()
        if self.ch == self.Chario.EL:
            self.Chario.put_error("''' expected")
            self.token_buffer += ' '
            self.ch = self.Chario.getChar
        else:
            self.token.string = str(self.ch)
            self.ch = self.Chario.getChar()
            if self.ch == "\'":
                self.ch = self.Chario.getChar
            else:
                self.Chario.put_error("''' expected")

    def get_double_op(self):
        self.token_buffer = ""
        self.token_buffer += self.ch
        self.ch = self.Chario.getChar()
        self.token_buffer += self.ch
        self.token = self.find_token(self.double_ops, self.token_buffer)
        if self.token.code != Token.ERROR:
            self.ch = self.Chario.getChar

    def get_single_op(self):
        self.token = self.find_token(self.single_ops, self.token_buffer[0])

    def nextToken(self):
        while True:
            self.skip_blanks()
            if self.ch.isalnum() or self.ch == '_':
                self.get_identifier_or_keyword()
            elif self.ch.isdigit():
                self.get_integer()
            elif self.ch == '\'':
                self.get_character()
            elif self.ch == self.Chario.EF:
                print(self.Chario.EF)
                self.token = Token(Token.EOF)
            else:
                self.get_double_op()
                if self.token.code == Token.ERROR:
                    self.get_single_op()
                    if self.token.code == Token.ERROR:
                        self.Chario.put_error("unrecognized symbol")
            if self.token.code == Token.ERROR:
                break
        return self.token

