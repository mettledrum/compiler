# Andrew Hoyle
# Assignment 3: Micro Scanner/Parser/Generator (ad-hoc)
# 810-32-3651
# 9/12/13

# scanner and semantic_scanner first run on the code from infile
# token list and semantic list are generated from the scanners
# parser then references these lists indexed at T_IDX when needed
# SEM_LIST is used for putting the values into the "structs"
# TOK_LIST is used for parsing and matching
# generator code puts values into machine output file

# This code is uuuuugly, but I need to do some more testing of the
#  way python allows imports.

import string                    # string. objects for GLOBAL defs
from debug import *             # for VIEWER GLOBAL
from structs import *           # for micro generator to use

"""--------------------------GLOBALS-----------------------------------------"""

EOF = '$'                        # make sure EOF symbol is not an operator!
LETTERS = string.letters
DIGITS = string.digits
VAR_CHARS = string.letters + string.digits + '_'
SKIP_US = ' ' + '\n' + '\t'
RES_WORDS = dict( WRITE="WriteSym", READ="ReadSym", BEGIN="BeginSym", 
                  END="EndSym" )
LEGAL_TOKENS = [ "BeginSym", "EndSym", "ReadSym", "WriteSym",
                 "Id", "IntLiteral", "LParen", "RParen", "SemiColon",
                 "Comma", "AssignOp", "PlusOp", "MinusOp", "EofSym" ]

IDX = 0                          # where the string is being read
CODE_STR = ""                    # the code string to be compiled 
TOK_LIST = []                    # list of tokens from Scanner's first run
T_IDX = 0                        # which token is current

VIEWER = StackViewer("    ")     # for debugging
#VIEWER.turn_on()                # turns the view switch on

OUT_FILE_NAME = "output.txt"     # main could assign this value
SYMBOL_TABLE = []                # holds names of variables
TEMP_COUNTER = 0                 # increments for temp variables' names

SEM_LIST  = []                   # Sem_Scanner's strings for semantics records

"""--------------------AUXILLARY-GENERATOR-----------------------------------"""

# writes machine code to external file, GLOBAL OUT_FILE_NAME
def Generate4(s1, s2, s3, s4):
    global OUT_FILE_NAME
    f = open(OUT_FILE_NAME, 'a')
    f.write(s1 + " " + s2 + ", " + s3 + ", " + s4 + '\n')

def Generate3(s1, s2, s3):
    global OUT_FILE_NAME
    f = open(OUT_FILE_NAME, 'a')
    f.write(s1 + " " + s2 + ", " + s3 + '\n')

def Generate1(s1):
    global OUT_FILE_NAME
    f = open(OUT_FILE_NAME, 'a')
    f.write(s1 + '\n')

# should be a class method, why can't I just call ex.name?
def Extract(expr_rec): 
    return expr_rec.name

# machine code for add or "subtract", only add works
# GLOBAL LEGAL_TOKENS' element names are used
def ExtractOp(o):
    if o.op == "MinusOp":
        return "Sub"
    elif o.op == "PlusOp":
        return "Add"
    # add error checking
    else:
        return "shouldn't come here"

# just sees if var name is in the GLOBAL SYMBOL_TABLE
def LookUp(s):
    global SYMBOL_TABLE
    if s in SYMBOL_TABLE:
        return True
    else:
        return False

# just puts it in! uses GLOBAL SYMBOL_TABLE
def Enter(s):
    global SYMBOL_TABLE
    SYMBOL_TABLE.append(s)

# put in table and declare in machine code output IF hasn't been made yet
def CheckId(s):
    if not LookUp(s):
        Enter(s)
        Generate3("Declare", s, "Integer")

# names temp vars put in SYMBOL_TABLE using GLOBAL TEMP_COUNTER
def GetTemp():
    global TEMP_COUNTER
    TEMP_COUNTER = TEMP_COUNTER + 1
    temp_name = "Temp&" + str(TEMP_COUNTER)
    CheckId(temp_name)
    return temp_name

"""--------------------------------SEMANTIC ROUTINES-------------------------"""

# WOULD initialize some list counter variables, not needed in Python
def Start():
    return

# machine code calls 
def Assign(target, source):
    Generate3("Store ", Extract(source), target.name)

def ReadId(inVar):
    Generate3("Read", inVar.name, "Integer")

def WriteExpr(outExpr):
    Generate3("Write", Extract(outExpr), "Integer")

# assign values to ExprRec "struct" generate + code
def GenInfix(e1, op, e2):
    # call ExprRec constructor
    tempRec = ExprRec(GetTemp(), "TempExpr")
    Generate4(ExtractOp(op), Extract(e1), Extract(e2), tempRec.name)
    return tempRec

# changes the value of the exprRec and puts it in table
# changes to class data members are by ref
# uses GLOBAL TOKEN LIST and IDX
def ProcessId(e):
    global SEM_LIST, T_IDX
    CheckId(SEM_LIST[T_IDX])
    e.kind = "IdExpr"
    e.name = SEM_LIST[T_IDX]

# changes the value of the exprRec
# changes to class data members are by ref
# uses GLOBAL TOKEN LIST and IDX
def ProcessLiteral(e):
    global SEM_LIST, T_IDX
    e.kind = "LiteralExpr"
    e.name = SEM_LIST[T_IDX]

# assigns token to o.op "struct"
# changes to class data members are by ref
# uses GLOBAL TOKEN LIST and IDX
def ProcessOp(o):
    global TOK_LIST, T_IDX
    o.op = TOK_LIST[T_IDX]

def Finish():
    Generate1("Halt")

"""-----------------------------ERROR CORRECTION-----------------------------"""

# uses sets 
def CheckInput(vs, fs, hs):
    global TOK_LIST, T_IDX
    nt = TOK_LIST[T_IDX]
    uni = vs | fs | hs

    print "CHECK INPUT:\t", nt
    print "ValidSet:\t", vs
    print "UnionSet:\t", uni, "\n"

    if nt in vs:
        return
    else:
        print "CheckInput SyntaxError(", nt, ")"
        while nt not in uni:
            print "CheckIn skipping:", nt
            Increm()
            nt = TOK_LIST[T_IDX]
        print ''

# prevents index error
def Increm():
    global T_IDX
    if T_IDX >= len(TOK_LIST)-1:
        return
    else:
        T_IDX += 1

"""------------------------------PARSER-WITH-GENERATOR-----------------------"""

# syntactic error checker for the parser
def Match(leg_tok):
    global T_IDX
    # view recursion
    VIEWER.into("Match")

    print "Match:\t", leg_tok, "=?", SEM_LIST[T_IDX], "\n"

    # get token from scanner and declare GLOBAL token index
    global T_IDX
    
    next_tok = TOK_LIST[T_IDX]

    if next_tok == leg_tok:
        cur_tok = TOK_LIST[T_IDX]
        Increm()

    else:
        cur_tok = leg_tok
        print "Match SyntaxError(", next_tok, "!=", leg_tok, ")"

        end_set = set(['EofSym', 'SemiColon'])

        if leg_tok in end_set:
            Increm()
            cur_tok = TOK_LIST[T_IDX]

            while cur_tok != leg_tok:
                #print "legal_token:\t", leg_tok
                print "Match skipping:", cur_tok
                Increm()
                cur_tok = TOK_LIST[T_IDX]

            #T_IDX -= 1
            print "parsing resuming at:", TOK_LIST[T_IDX], '\n' 
           
    # print token Match worked
    VIEWER.match_show(leg_tok)

    # view recursion
    VIEWER.outa("Match")

# now accepts opRec
def AddOp(op):
    VIEWER.into("AddOp")
    
    next_tok = TOK_LIST[T_IDX]
    if next_tok == "PlusOp":
        ProcessOp(op)
        Match("PlusOp")
    elif next_tok == "MinusOp":
        ProcessOp(op)
        Match("MinusOp")          
    else:
        print "SyntaxError(", TOK_LIST[T_IDX], ")"

    VIEWER.outa("AddOp")

# processes ID, now accepts exprRecs
def Ident(expr):
    VIEWER.into("Ident")

    ProcessId(expr)                         # gen code for struct
    Match("Id")

    VIEWER.outa("Ident")

# takes ExprRec now
def Primary(result):
    VIEWER.into("Primary")

    next_tok = TOK_LIST[T_IDX]
    if next_tok == "LParen":
        Match("LParen")
        result = Expression(result)         # now takes exprRec
        Match("RParen")
    elif next_tok == "Id":
        Ident(result)                       # now it takes exprRec
    elif next_tok == "IntLiteral":
        ProcessLiteral(result)              # added for generator
        Match("IntLiteral")
    else:
        print "SyntaxError(", TOK_LIST[T_IDX], ")"

    VIEWER.outa("Primary")

# recursive part JUST WORKS FOR ADDITION!
def Expression(Result):                               # now it takes ExprRec
    VIEWER.into("Expression")

    CheckInput(set(['Id', 'IntLiteral', 'LParen']), set(['Comma', 'SemiColon', 'RParen']), set(['EndSym']))

    leftOperand = ExprRec("ERROR", "ERROR")           # make empty structs
    rightOperand = ExprRec("ERROR", "ERROR")
    op = OpRec("ERROR")

    Primary(leftOperand)                              # now takes ExprRec

    next_tok = TOK_LIST[T_IDX]
    if next_tok == "PlusOp" or next_tok == "MinusOp":
        AddOp(op)                                     # takes ExprRec now
        rightOperand = Expression(rightOperand)       # takes ExprRec now

        Result = GenInfix(leftOperand, op, rightOperand)
    else:
        Result = leftOperand
    return Result

    VIEWER.outa("Expression")

def ExprList():
    VIEWER.into("ExprList")

    expr = Expr("ERROR", "ERROR")               # gen code struct
    expr = Expression(expr)                     # pass struct
    WriteExpr(expr)                             # pass struct

    next_tok = TOK_LIST[T_IDX]
    if next_tok == "Comma":
        Match("Comma")
        ExprList()

    VIEWER.outa("ExprList")

def IdList():
    VIEWER.into("IdList")

    identifier = ExprRec("ERROR", "ERROR")      # gen code struct
    Ident(identifier)                           # pass struct
    ReadId(identifier)                          # pass struct

    next_tok = TOK_LIST[T_IDX]
    if next_tok == "Comma":
        Match("Comma")
        IdList()

    VIEWER.outa("IdList")

def Statement():
    VIEWER.into("Statement")

    identifier = ExprRec("ERROR", "ERROR")       # gen code struct
    expr = ExprRec("ERROR", "")                  # gen code struct

    CheckInput(set(['Id', 'ReadSym', 'WriteSym']), set(['EndSym']), set(['EofSym']))

    next_tok = TOK_LIST[T_IDX]
    # populates expression_records structs
    # they are are stuffed with token values
    if next_tok == "Id":            
        Ident(identifier)
        Match("AssignOp")
        expr = Expression(expr)
        Assign(identifier, expr)
        Match("SemiColon")
    elif next_tok == "ReadSym":
        Match("ReadSym")
        Match("LParen")
        IdList()
        Match("RParen")
        Match("SemiColon")
    elif next_tok == "WriteSym":
        Match("WriteSym")
        Match("LParen")
        ExprList()
        Match("RParen")
        Match("SemiColon")
    else:
        print "SyntaxError(", TOK_LIST[T_IDX], ")"

    VIEWER.outa("Statement")

def StatementList():
    VIEWER.into("StatementList")

    CheckInput(set(['Id', 'ReadSym', 'WriteSym']), set(['EndSym']), set(['EofSym']))
    Statement()

    next_tok = TOK_LIST[T_IDX]
    if next_tok == "Id" or next_tok == "ReadSym" or next_tok == "WriteSym":
        StatementList()

    VIEWER.outa("StatementList")

def Program():
    VIEWER.into("Program")

    Start()
    CheckInput(set(['BeginSym']), set(['EofSym']), set(['EofSym']))
    Match("BeginSym")
    StatementList()
    Match("EndSym")

    VIEWER.outa("Program")

def SystemGoal():
    VIEWER.into("SystemGoal")

    Program()
    Match("EofSym")
    Finish()

    VIEWER.outa("SystemGoal")

"""------------------------------SCANNER-------------------------------------"""

# add a way to check the specific reserved word it is
def CheckReserved(_buff):
    if _buff in RES_WORDS:
        return RES_WORDS[_buff]
    else:
        return "Id"

# looks at string and gives the next token, also updates the GLOBAL
#  index position for viewing the code string
def Scanner():
    global CODE_STR, IDX
    while EOF != CODE_STR[IDX]:
        # do nothing
        if CODE_STR[IDX] in SKIP_US:
            IDX = IDX + 1

        # ID or reserved symbol
        elif CODE_STR[IDX] in LETTERS:
            # reset _buffer and store char
            _buf = "" + CODE_STR[IDX]
            # look at rest of the variable name
            while CODE_STR[IDX + 1] in VAR_CHARS:
                # inc IDX
                IDX = IDX + 1
                # store char in buffer
                _buf = _buf + CODE_STR[IDX]
            # catch IDX up with IDX position in string
            IDX = IDX + 1
            return CheckReserved(_buf)

        # check for int literals
        elif CODE_STR[IDX] in DIGITS:
            # reset _buffer and store char
            _buf = "" + CODE_STR[IDX]
            # look at the rest of the number
            while CODE_STR[IDX + 1] in DIGITS:
                # inc IDX
                IDX = IDX + 1
                # store char in buffer
                _buf = _buf + CODE_STR[IDX]
            # catch up IDX and add 1 to "escape" last char
            IDX = IDX + 1
            return "IntLiteral"

        # the single-char operators
        elif CODE_STR[IDX] == '(':
            IDX = IDX + 1
            return "LParen"
        elif CODE_STR[IDX] == ')':
            IDX = IDX + 1
            return "RParen"
        elif CODE_STR[IDX] == ';':
            IDX = IDX + 1
            return "SemiColon"
        elif CODE_STR[IDX] == ',':
            IDX = IDX + 1
            return "Comma"
        elif CODE_STR[IDX] == '+':
            IDX = IDX + 1
            return "PlusOp"

        # assignment := or lexical error
        elif CODE_STR[IDX] == ':':
            if CODE_STR[IDX + 1] == '=':
                IDX = IDX + 2
                return "AssignOp"
            else:
                try:
                    raise Exception(CODE_STR[IDX])
                except Exception as ex:
                    print "LexicalError(", ex[0], ")"
                    raise
                
        # minus or comments to ignore until \n
        elif CODE_STR[IDX] == '-':
            if CODE_STR[IDX + 1] == '-':
                IDX = IDX + 2                
                while CODE_STR[IDX] != '\n':
                    IDX = IDX + 1
            else:
                IDX = IDX + 1
                return "MinusOp"

        # all invalid characters
        else:
            try:
                raise Exception(CODE_STR[IDX])
            except Exception as ex:
                print "LexicalError(", ex[0], ")"
                raise

    # if while loop doesn't activate... if SKUP_US char is
    # b/w EndSym and EOF
    IDX = IDX + 1
    return "EofSym"

"""---------------------SEMANTIC-SCANNER-------------------------------------"""

# looks at code and gives the next string, also updates the GLOBAL
#  index position for viewing the code string
# ALSO populates GLOBAL SEM_LIST... used for semantic value recording
def Semantic_Scanner():
    global CODE_STR, IDX
    while EOF != CODE_STR[IDX]:
        # do nothing
        if CODE_STR[IDX] in SKIP_US:
            IDX = IDX + 1

        # ID or reserved symbol
        elif CODE_STR[IDX] in LETTERS:
            # reset _buffer and store char
            _buf = "" + CODE_STR[IDX]
            # look at rest of the variable name
            while CODE_STR[IDX + 1] in VAR_CHARS:
                # inc IDX
                IDX = IDX + 1
                # store char in buffer
                _buf = _buf + CODE_STR[IDX]
            # catch IDX up with IDX position in string
            IDX = IDX + 1
            return _buf

        # check for int literals
        elif CODE_STR[IDX] in DIGITS:
            # reset _buffer and store char
            _buf = "" + CODE_STR[IDX]
            # look at the rest of the number
            while CODE_STR[IDX + 1] in DIGITS:
                # inc IDX
                IDX = IDX + 1
                # store char in buffer
                _buf = _buf + CODE_STR[IDX]
            # catch up IDX and add 1 to "escape" last char
            IDX = IDX + 1
            return _buf

        # the single-char operators
        elif CODE_STR[IDX] == '(':
            IDX = IDX + 1
            return "("
        elif CODE_STR[IDX] == ')':
            IDX = IDX + 1
            return ")"
        elif CODE_STR[IDX] == ';':
            IDX = IDX + 1
            return ";"
        elif CODE_STR[IDX] == ',':
            IDX = IDX + 1
            return ","
        elif CODE_STR[IDX] == '+':
            IDX = IDX + 1
            return "+"

        # assignment := or lexical error
        elif CODE_STR[IDX] == ':':
            if CODE_STR[IDX + 1] == '=':
                IDX = IDX + 2
                return ":="
            else:
                try:
                    raise Exception(CODE_STR[IDX])
                except Exception as ex:
                    print "LexicalError(", ex[0], ")"
                    raise
                
        # minus or comments to ignore until \n
        elif CODE_STR[IDX] == '-':
            if CODE_STR[IDX + 1] == '-':
                IDX = IDX + 2                
                while CODE_STR[IDX] != '\n':
                    IDX = IDX + 1
            else:
                IDX = IDX + 1
                return "-"

        # all invalid characters
        else:
            try:
                raise Exception(CODE_STR[IDX])
            except Exception as ex:
                print "LexicalError(", ex[0], ")"
                raise

    # if while loop doesn't activate... if SKUP_US char is
    # b/w EndSym and EOF
    IDX = IDX + 1
    return EOF

"""-------------------------------MAIN---------------------------------------"""

def main():
    # globals that this procedure changes
    global CODE_STR, IDX, T_IDX, SEM_LIST, OUT_FILE_NAME

    # get file info
    in_file_name = raw_input("type name of input file: good_input.txt, bad_input1.txt, or bad_input2.txt -> ")
    fin = open(in_file_name, 'r')
    CODE_STR = fin.read() + EOF

    # erase output file contents
    fout = open(OUT_FILE_NAME, 'w')

    # show the code string from file
    print '\n', "Code from", in_file_name, "\n", CODE_STR, '\n'

    # go through and populate TOK_LIST GLOBAL, reset IDX GLOBALS to 0
    while IDX < len(CODE_STR):
        TOK_LIST.append(Scanner())
    IDX = 0
    T_IDX = 0

    # now go through and get the strings of the tokens, reset GLOBALS to 0
    while IDX < len(CODE_STR):
        SEM_LIST.append(Semantic_Scanner())
    IDX = 0
    T_IDX = 0

    # show the token and semantics list from file
    print "tokens:", "\n", TOK_LIST
    print '\n', "strings:", "\n", SEM_LIST, '\n'

    # run the ad-hoc parser
    SystemGoal()

    # tell where ouput is
    print "machine code is now in", OUT_FILE_NAME

main()



