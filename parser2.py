# Andrew Hoyle
# Assignment 2: Micro Scanner/Parser
# 810-32-3651
# 8/27/13

import string					# string. objects for GLOBAL defs
from debug import * 			# for VIEWER GLOBAL

"""--------------------------GLOBALS-----------------------------------------"""

EOF = '$'						# make sure EOF symbol is not an operator!
LETTERS = string.letters
DIGITS = string.digits
VAR_CHARS = string.letters + string.digits + '_'
SKIP_US = ' ' + '\n' + '\t'
RES_WORDS = dict( WRITE="WriteSym", READ="ReadSym", BEGIN="BeginSym", 
                 END="EndSym" )
LEGAL_TOKENS = [ "BeginSym", "EndSym", "ReadSym", "WriteSym",
				 "Id", "IntLiteral", "LParen", "RParen", "SemiColon",
				 "Comma", "AssignOp", "PlusOp", "MinusOp", "EofSym" ]

IDX = 0							# where the string is being read
CODE_STR = ""					# the code string to be compiled 
TOK_LIST = []					# list of tokens from Scanner's first run
T_IDX = 0						# which token is current
VIEWER = StackViewer("    ")	# for debugging
VIEWER.turn_on()				# turns the view switch on

"""------------------------------PARSER--------------------------------------"""

# syntactic error checker for the parser
def Match(tok_str):
	# view recursion
	VIEWER.into("Match")

	# get token from scanner and declare GLOBAL token index
	global T_IDX
	cur_tok = Scanner()

	# exception handling
	try:
		if cur_tok not in LEGAL_TOKENS:
			raise Exception(TOK_LIST[T_IDX])
	except Exception as ex:
		print "SyntaxError(", ex[0], ")"
		raise
			
	# next token
	T_IDX = T_IDX + 1

	# print token Match matched
	VIEWER.match_show(cur_tok)

	# view recursion
	VIEWER.outa("Match")

def AddOp():
	VIEWER.into("AddOp")
	
	next_tok = TOK_LIST[T_IDX]
	if next_tok == "PlusOp":
		Match("PlusOp")
	elif next_tok == "MinusOp":
		Match("MinusOp")
	else:
		try:
			raise Exception(TOK_LIST[T_IDX])
		except Exception as ex:
			print "SyntaxError(", ex[0], ")"
			raise

	VIEWER.outa("AddOp")

def Ident():
	VIEWER.into("Ident")

	Match("Id")

	VIEWER.outa("Ident")

def Primary():
	VIEWER.into("Primary")

	next_tok = TOK_LIST[T_IDX]
	if next_tok == "LParen":
		Match("LParen")
		Expression()
		Match("RParen")
	elif next_tok == "Id":
		Ident()
	elif next_tok == "IntLiteral":
		Match("IntLiteral")
	else:
		try:
			raise Exception(TOK_LIST[T_IDX])
		except Exception as ex:
			print "SyntacticError(", ex[0], ")"
			raise

	VIEWER.outa("Primary")

def Expression():
	VIEWER.into("Expression")

	Primary()

	next_tok = TOK_LIST[T_IDX]
	if next_tok == "PlusOp" or next_tok == "MinusOp":
		AddOp()
		Expression()

	VIEWER.outa("Expression")

def ExprList():
	VIEWER.into("ExprList")

	Expression()

	next_tok = TOK_LIST[T_IDX]
	if next_tok == "Comma":
		Match("Comma")
		ExprList()

	VIEWER.outa("ExprList")

def IdList():
	VIEWER.into("IdList")

	Ident()

	next_tok = TOK_LIST[T_IDX]
	if next_tok == "Comma":
		Match("Comma")
		IdList()

	VIEWER.outa("IdList")

def Statement():
	VIEWER.into("Statement")

	next_tok = TOK_LIST[T_IDX]
	if next_tok == "Id":
		Ident()
		Match("AssignOp")
		Expression()
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
		try:
			raise Exception(TOK_LIST[T_IDX])
		except Exception as ex:
			print "SyntaxError(", ex[0], ")"
			raise

	VIEWER.outa("Statement")

def StatementList():
	VIEWER.into("StatementList")

	Statement()

	next_tok = TOK_LIST[T_IDX]
	if next_tok == "Id" or next_tok == "ReadSym" or next_tok == "WriteSym":
		StatementList()

	VIEWER.outa("StatementList")

def Program():
	VIEWER.into("Program")

	Match("BeginSym")
	StatementList()
	Match("EndSym")

	VIEWER.outa("Program")

def SystemGoal():
	VIEWER.into("SystemGoal")

	Program()
	Match("EofSym")

	VIEWER.outa("SystemGoal")

# add a way to check the specific reserved word it is
def CheckReserved(_buff):
	if _buff in RES_WORDS:
		return RES_WORDS[_buff]
	else:
		return "Id"

"""------------------------------SCANNER-------------------------------------"""

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

"""-------------------------------MAIN---------------------------------------"""

def main():
	# globals that this procedure changes
	global CODE_STR, IDX, T_IDX

	# get file info
	f = open('input1.txt', 'r')
	CODE_STR = f.read() + EOF

	# show the code string from file
	print CODE_STR

	# go through and populate TOK_LIST GLOBAL, reset IDX GLOBALS to 0
	while IDX < len(CODE_STR):
		TOK_LIST.append(Scanner())
	IDX = 0
	T_IDX = 0

	# show the token list from file
	print TOK_LIST

	# run the ad hoc parser
	SystemGoal()

main()



