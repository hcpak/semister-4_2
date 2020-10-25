################################################################################
#Parser가 동작하기 위해서 Token, Chario, Scanner 모듈이 필요
#추가로 sys.exit() 사용하기 위해 sys를 import 했다.
################################################################################
from Token import Token
from Chario import Chario
from Scanner import Scanner
import sys

################################################################################
#Parser 모듈
################################################################################

NONE = 0
SCOPE = 0
ROLE = 0


class Parser(object):
    ##########################################################################################
    #Parser 초기화 관련 함수들
    ##########################################################################################
    def __init__(self, chario: Chario, scanner: Scanner, mode):
        self.__chario = chario
        self.__scanner = scanner

        self.__initHandles()
        self.__initTables()
        self.__token = self.__scanner.nextToken()
        self.__mode = mode

    def reset(self):
        self.__scanner.reset()
        self.__token = self.__scanner.nextToken()

    def __initHandles(self):
        self.__addingOperator = set()
        self.__addingOperator.add(Token.PLUS)
        self.__addingOperator.add(Token.MINUS)
        self.__multiplyingOperator = set()
        self.__multiplyingOperator.add(Token.MUL)
        self.__multiplyingOperator.add(Token.DIV)
        self.__multiplyingOperator.add(Token.MOD)
        self.__relationalOperator = set()
        self.__relationalOperator.add(Token.EQ)
        self.__relationalOperator.add(Token.NE)
        self.__relationalOperator.add(Token.LE)
        self.__relationalOperator.add(Token.GE)
        self.__relationalOperator.add(Token.LT)
        self.__relationalOperator.add(Token.GT)
        self.__basicDeclarationHandles = set()
        self.__basicDeclarationHandles.add(Token.TYPE)
        self.__basicDeclarationHandles.add(Token.ID)
        self.__basicDeclarationHandles.add(Token.PROC)
        self.__statementHandles = set()
        self.__statementHandles.add(Token.EXIT)
        self.__statementHandles.add(Token.ID)
        self.__statementHandles.add(Token.IF)
        self.__statementHandles.add(Token.LOOP)
        self.__statementHandles.add(Token.NULL)
        self.__statementHandles.add(Token.WHILE)
        self.__leftNames = set()
        self.__leftNames.add(SymbolEntry.PARAM)
        self.__leftNames.add(SymbolEntry.VAR)
        self.__rightNames = set(self.__leftNames)
        self.__rightNames.add(SymbolEntry.CONST)


    def __acceptRole(self, symbolEntry, expected, errorMessage):
        if self.__mode == Parser.ROLE:
            if symbolEntry == None or (symbolEntry.NONE and symbolEntry != expected ):
                self.__putError(errorMessage)


    def __acceptRole(self, symbolEntry, expected, errormessage):
        if self.__mode == Parser.ROLE:
            if symbolEntry == None or (symbolEntry.role != symbolEntry.NONE and not(expected.__contains__(symbolEntry.role))):
                self.__chario.putError(errormessage)

    def __setRole(self, symbolEntry, role):
        if(self.__mode == Parser.ROLE and symbolEntry != None):
            symbolEntry.setRole(role)

    def __appendEntry(self, head, tail):
        if(self.__mode == Parser.SCOPE or self.__mode == Parser.ROLE):
            if(head != None):
                head.append(tail)


    ################################################################################
    #Parser ERROR 처리 관련 함수들
    ################################################################################
    def __accept(self, expected: int, errorMessage: str):
        if self.__token.code != expected:
            self.__fatalError(errorMessage)
        self.__token = self.__scanner.nextToken()

    def __fatalError(self, errorMessage: str):
        self.__chario.putError("PARSER ERROR >> "+errorMessage)
        self.__chario.reportErrors()
        sys.exit()
        # raise RuntimeError("Fatal Error")

    def __initTable(self):
        if(self.__mode == Parser.ROLE or self.__mode == Parser.SCOPE):
            self.__table = SymbolTable(self.__chario)
            self.__enterScope()
            entry = table.enterSymbol("BOOLEAN")
            self.__setRole(entry, SymbolEntry.TYPE)
            entry = table.enterSymbol("CHAR")
            self.__setRole(entry, SymbolEntry.TYPE)
            entry = table.enterSymbol("INTEGER")
            self.__setRole(entry, SymbolEntry.TYPE)
            entry = table.enterSymbol("TRUE")
            self.__setRole(entry, SymbolEntry.CONST)
            entry = table.enterSymbol("FALSE")
            self.__setRole(entry, SymbolEntry.CONST)

    def __enterScope(self):
        if(self.__mode == Parser.ROLE or self.__mode == Parser.SCOPE):
            self.__table.enterScope()

    def __exitSccope(self):
        if(self.__mode == Parser.ROLE or self.__mode == Parser.SCOPE):
            self.__table.exitScope(self.__mode)

    def __enterID(self):
        entry = None
        if self.__token.code == Token.ID:
            if self.__mode == Parser.SCOPE or self.__mode == Parser.ROLE :
                entry = self.__table.enterSymbol(self.__token.string)
        else:
            self.__fatalError("Identifier expected")

        self.__token = self.__scanner.nextToken()
        return entry

    def __findID(self):
        entry = None
        if self.__token.code == Token.ID:
            if self.__mode == Parser.SCOPE or self.__mode == Parser.ROLE:
                entry = self.__table.findSymbol(self.__token.string)
        else:
            self.__fatalError("Identifier expected")

        self.__token = self.__scanner.nextToken()
        return entry


    ################################################################################
    #Parsing 관련 함수들
    ################################################################################
    def parse(self):
        self.__subprogramBody()
        self.__accept(Token.EOF, "Extra symbols after logical end of program")

    ################################################################################
    #   subprogramBody =
    #               subprogramSpecification "is"
    #               declarativePart
    #               "begin" sequenceOfStatements
    #               "end"[ < procedure > identifier] ";"
    ################################################################################
    def __subprogramBody(self):
        self.__subprogramSpecification()
        self.__accept(Token.IS, "'is' expected")
        self.__declarativePart()
        self.__accept(Token.BEGIN, "'begin' expected")
        self.__sequenceOfStatements()
        self.__accept(Token.END, "'end' expected")
        if self.__token.code == Token.ID:
            self.__token = self.__scanner.nextToken()
        self.__accept(Token.SEMI, "semicolon expected")

    ################################################################################
    #   subprogramSpecification = "procedure" identifier [ formalPart ]
    ################################################################################
    def __subprogramSpecification(self):
        self.__accept(Token.PROC, "'procedure' expected")
        self.__accept(Token.ID, "'identifier' expected")
        if self.__token.code == Token.L_PAR:
            self.__formalPart()

    def __formalPart(self):
        self.__accept(Token.L_PAR, "'(' expected")
        self.__parameterSpecification()
        while self.__token.code == Token.SEMI:
            self.__token = self.__scanner.nextToken()
            self.__parameterSpecification()
        self.__accept(Token.R_PAR, "')' expected")

    ################################################################################
    #   parameterSpecification = identifierList ":" mode <type>name
    ################################################################################
    def __parameterSpecification(self):
        self.__identifierList()
        self.__accept(Token.COLON, "':' expected")
        self.__mode()
        self.__name()

    ################################################################################
    #   mode = [ "in" ] | "in" "out" | "out"
    ################################################################################
    def __mode(self):
        if self.__token.code == Token.IN:
            self.__accept(Token.IN, "'in' expected")
        if self.__token.code == Token.OUT:
            self.__accept(Token.OUT, "'out' expected")

    ################################################################################
    #   declarativePart = { basicDeclaration }
    ################################################################################
    def __declarativePart(self):
        while self.__basicDeclarationHandles.__contains__(self.__token.code):
            self.__basicDeclaration()

    ################################################################################
    #   basicDeclaration = objectDeclaration | numberDeclaration
    #                     | typeDeclaration | subprogramBody
    ################################################################################
    def __basicDeclaration(self):
        if self.__token.code == Token.ID:
            self.__numberOrObjectDeclaration()
        elif self.__token.code == Token.TYPE:
            self.__typeDeclaration()
        elif self.__token.code == Token.PROC:
            self.__subprogramBody()
        else:
            self.__fatalError("Error in declaration part")

    ################################################################################
    #   objectDeclaration =
    #       identifierList ":" typeDefinition ";"
    #
    #   numberDeclaration =
    #       identifierList ":" "constant" ":=" <static>expression ";"
    ################################################################################
    def __numberOrObjectDeclaration(self):
        self.__identifierList()
        self.__accept(Token.COLON, "':' expected")
        if self.__token.code == Token.CONST:
            self.__token = self.__scanner.nextToken()
            self.__accept(Token.GETS, "':=' expected")
            self.__expression()
        else:
            self.__typeDefinition()
        self.__accept(Token.SEMI, "';' expected")

    ################################################################################
    #   typeDeclaration = "type" identifier "is" typeDefinition ";"
    ################################################################################
    def __typeDeclaration(self):
        self.__accept(Token.TYPE, "'type' expected")
        self.__accept(Token.ID, "'identifier' expected")
        self.__accept(Token.IS, "'is' expected")
        self.__typeDefinition()
        self.__accept(Token.SEMI, "';' expected")

    ################################################################################
    #   typeDefinition = enumerationTypeDefinition | arrayTypeDefinition
    #                       | range | <type>name
    ################################################################################
    def __typeDefinition(self):
        if self.__token.code == Token.L_PAR:
            self.__enumerationTypeDefinition()
        elif self.__token.code == Token.R_PAR:
            self.__arrayTypeDefinition()
        elif self.__token.code == Token.RANGE:
            self.__range()
        elif self.__token.code == Token.ID:
            self.__name()
        elif self.__token.code == Token.ARRAY:
            self.__arrayTypeDefinition()
        else:
            self.__fatalError("Error in definition part")

    ################################################################################
    #   enumerationTypeDefinition = "(" identifierList ")"
    ################################################################################
    def __enumerationTypeDefinition(self):
        self.__accept(Token.L_PAR, "'(' expected")
        self.__identifierList()
        self.__accept(Token.R_PAR, "')' expected")

    ################################################################################
    #   arrayTypeDefinition = "array" "(" index { "," index } ")" "of" <type>name
    ################################################################################
    def __arrayTypeDefinition(self):
        self.__accept(Token.ARRAY, "'array' expected")
        self.__accept(Token.L_PAR, "'(' expected")
        self.__index()

        while self.__token.code == Token.COMMA:
            self.__token = self.__scanner.nextToken()
            self.__index()

        self.__accept(Token.R_PAR, "')' expected")
        self.__accept(Token.OF, "'of' expected")
        self.__name()

    ################################################################################
    #   index = range | <type>name
    ################################################################################
    def __index(self):
        if self.__token.code == Token.RANGE:
            self.__range()
        elif self.__token.code == Token.ID:
            self.__name()
        else:
            self.__fatalError("Error in index type")

    ################################################################################
    #   range = "range " simpleExpression ".." simpleExpression
    ################################################################################
    def __range(self):
        self.__accept(Token.RANGE, "'array' expected")
        self.__simpleExpression()
        self.__accept(Token.THRU, "'..' expected")
        self.__simpleExpression()

    ################################################################################
    #   identifier { "," identifier }
    ################################################################################
    def __identifierList(self):
        self.__token = self.__scanner.nextToken()
        while self.__token.code == Token.COMMA:
            self.__token = self.__scanner.nextToken()
            self.__accept(Token.ID, "'identifier' expected")

    ################################################################################
    #   sequenceOfStatements = statement { statement }
    ################################################################################
    def __sequenceOfStatements(self):
        self.__statement()
        while self.__statementHandles.__contains__(self.__token.code):
            self.__statement()

    ################################################################################
    #   statement = simpleStatement | compoundStatement
    #
    #   simpleStatement = nullStatement | assignmentStatement
    #                    | procedureCallStatement | exitStatement
    #
    #   compoundStatement = ifStatement | loopStatement
    ################################################################################
    def __statement(self):
        if self.__token.code == Token.ID:
            self.__assignmentOrCallStatement()
        elif self.__token.code == Token.EXIT:
            self.__exitStatement()
        elif self.__token.code == Token.IF:
            self.__ifStatement()
        elif self.__token.code == Token.NULL:
            self.__nullStatement()
        elif self.__token.code == Token.WHILE or self.__token.code == Token.LOOP:
            self.__loopStatement()
        else:
            self.__fatalError("Error in statement")

    ################################################################################
    #    nullStatement = "null" ";"
    ################################################################################
    def __nullStatement(self):
        self.__accept(Token.NULL, "'null' expected")
        self.__accept(Token.SEMI, "';' expected")

    ################################################################################
    #   loopStatement =
    #            [ iterationScheme ] "loop" sequenceOfStatements "end" "loop" ";"
    ################################################################################
    def __loopStatement(self):
        if self.__token.code == Token.WHILE:
            self.__iterationScheme()
        self.__accept(Token.LOOP, "'loop' expected")
        self.__sequenceOfStatements()
        self.__accept(Token.END, "'end' expected")
        self.__accept(Token.LOOP, "'loop' expected")
        self.__accept(Token.SEMI, "semicolon expected")

    ################################################################################
    #   iterationScheme = "while" condition
    ################################################################################
    def __iterationScheme(self):
        self.__accept(Token.WHILE, "'while' expected")
        self.__condition()

    ################################################################################
    #   ifStatement =
    #          "if" condition "then" sequenceOfStatements
    #          { "elsif" condition "then" sequenceOfStatements }
    #          [ "else" sequenceOfStatements ]
    #          "end" "if" ";"
    ################################################################################
    def __ifStatement(self):
        self.__accept(Token.IF, "'if' expected")
        self.__condition()
        self.__accept(Token.THEN, "'then' expected")
        self.__sequenceOfStatements()
        while self.__token.code == Token.ELSIF:
            self.__token = self.__scanner.nextToken()
            self.__condition()
            self.__accept(Token.THEN, "'then' expected")
            self.__sequenceOfStatements()

        if self.__token.code == Token.ELSE:
            self.__token = self.__scanner.nextToken()
            self.__sequenceOfStatements()

        self.__accept(Token.END, "'end' expected")
        self.__accept(Token.IF, "'if' expected")
        self.__accept(Token.SEMI, "semicolon expected")

    ################################################################################
    #   exitStatement = "exit" [ "when" condition ] ";"
    ################################################################################
    def __exitStatement(self):
        self.__accept(Token.EXIT, "'exit' expected")
        if self.__token.code == Token.WHEN:
            self.__token = self.__scanner.nextToken()
            self.__condition()

        self.__accept(Token.SEMI, "semicolon expected")

    ################################################################################
    #   assignmentStatement = <variable>name ":=" expression ";"
    #   procedureCallStatement = <procedure>name [ actualParameterPart ] ";"
    ################################################################################
    def __assignmentOrCallStatement(self):
        self.__name()
        if self.__token.code == Token.GETS:
            self.__token = self.__scanner.nextToken()
            self.__expression()

        self.__accept(Token.SEMI, "semicolon expected")

    ################################################################################
    #   condition = <boolean>expression
    ################################################################################
    def __condition(self):
        self.__expression()

    ################################################################################
    #   expression = relation { "and" relation } | { "or" relation }
    ################################################################################
    def __expression(self):
        self.__relation()
        if self.__token.code == Token.AND:
            while self.__token.code == Token.AND:
                self.__token = self.__scanner.nextToken()
                self.__relation()
        elif self.__token.code == Token.OR:
            while self.__token.code == Token.OR:
                self.__token = self.__scanner.nextToken()
                self.__relation()

    ################################################################################
    #    relation = simpleExpression [ relationalOperator simpleExpression ]
    ################################################################################
    def __relation(self):
        self.__simpleExpression()
        if self.__relationalOperator.__contains__(self.__token.code):
            self.__token = self.__scanner.nextToken()
            self.__simpleExpression()

    ################################################################################
    #        simpleExpression =
    #           [ unaryAddingOperator ] term { binaryAddingOperator term }
    ################################################################################
    def __simpleExpression(self):
        if self.__addingOperator.__contains__(self.__token.code):
            self.__token = self.__scanner.nextToken()

        self.__term()

        while self.__addingOperator.__contains__(self.__token.code):
            self.__token = self.__scanner.nextToken()
            self.__term()

    ################################################################################
    #   term = factor { multiplyingOperator factor }
    ################################################################################
    def __term(self):
        self.__factor()
        while self.__multiplyingOperator.__contains__(self.__token.code):
            self.__token = self.__scanner.nextToken()
            self.__factor()

    ################################################################################
    #   factor = primary [ "**" primary ] | "not" primary
    ################################################################################
    def __factor(self):
        if self.__token.code == Token.NOT:
            self.__token = self.__scanner.nextToken()
            self.__primary()
        else:
            self.__primary()
            if(self.token.code == Token.EXPO):
                self.__token = self.__scanner.nextToken()
                self.__primary()

    ################################################################################
    #   primary = numericLiteral | name | "(" expression ")"
    ################################################################################
    def __primary(self):
        if self.__token.code == Token.INT:
            self.__token = self.__scanner.nextToken()
        elif self.__token.code == Token.CHAR:
            self.__token = self.__scanner.nextToken()
        elif self.__token.code == Token.ID:
            entry = self.__name()
            self.__acceptRole(entry, self.__rightNames, "must be a paramet, variable ro constant name")
        elif self.__token.code == Token.L_PAR:
            self.__token = self.__scanner.nextToken()
            self.__expression()
            self.__accept(Token.R_PAR, "')' expected")
        else:
            self.__fatalError("Error in primary")

    ################################################################################
    #   name = identifier [ indexedComponent ]
    ################################################################################
    def __name(self):
        entry = self.__findID()
        if self.__token.code == Token.L_PAR:
            self.__indexedComponent()
        return entry

    ################################################################################
    #    indexedComponent = "(" expression  { "," expression } ")"
    ################################################################################
    def __indexedComponent(self):
        self.__accept(Token.L_PAR, "'(' expected")
        self.__expression()
        while self.__token.code == Token.COMMA:
            self.__token = self.__scanner.nextToken()
            self.__expression()

        self.__accept(Token.R_PAR, "')' expected")