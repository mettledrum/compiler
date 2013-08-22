# Andrew Hoyle
# Assignment 1: Micro Scanner
# 810-32-3651
# 8/20/13

# string. objects
import string

# make sure symbol not used otherwise
EOF = '$'
letters = string.letters
digits = string.digits
var_chars = string.letters + string.digits + '_'
skip_us = ' ' + '\n' + '\t'
res_words = dict(WRITE="WriteSym", READ="ReadSym", BEGIN="BeginSym", 
                 END="EndSym")

# GLOBALS
IDX = 0		# where the string is being read

# add a way to check the specific reserved word it is
def CheckReserved(_buff):
	if _buff in res_words:
		return res_words[_buff]
	else:
		return "Id"

# looks at string and gives the next token, also updates the GLOBAL
#  index position for viewing the code string
def Scanner(st):
	global IDX
	# EOF found
	if st[IDX] == EOF:
		IDX = IDX + 1
		return "EofSym"
	# still chars to check out
	else:
		while EOF != st[IDX]:
			# do nothing
			if st[IDX] in skip_us:
				IDX = IDX + 1

			# ID or reserved symbol
			elif st[IDX] in letters:
				# reset _buffer and store char
				_buf = "" + st[IDX]
				# look at rest of the variable name
				while st[IDX + 1] in var_chars:
					# inc IDX
					IDX = IDX + 1
					# store char in buffer
					_buf = _buf + st[IDX]
				# catch IDX up with IDX position in string
				IDX = IDX + 1
				return CheckReserved(_buf)

			# check for int literals
			elif st[IDX] in digits:
				# reset _buffer and store char
				_buf = "" + st[IDX]
				# look at the rest of the number
				while st[IDX + 1] in digits:
					# inc IDX
					IDX = IDX + 1
					# store char in buffer
					_buf = _buf + st[IDX]
				# catch up IDX and add 1 to "escape" last char
				IDX = IDX + 1
				return "IntLiteral"

			# the single-char operators
			elif st[IDX] == '(':
				IDX = IDX + 1
				return "LParen"
			elif st[IDX] == ')':
				IDX = IDX + 1
				return "RParen"
			elif st[IDX] == ';':
				IDX = IDX + 1
				return "SemiColon"
			elif st[IDX] == ',':
				IDX = IDX + 1
				return "Comma"
			elif st[IDX] == '+':
				IDX = IDX + 1
				return "PlusOp"

			# assignment := or lexical error
			elif st[IDX] == ':':
				if st[IDX + 1] == '=':
					IDX = IDX + 2
					return "AssignOp"
				else:
					IDX = IDX + 1
					return "LexicalError"			# should include char too

			# minus or comments to ignore until \n
			elif st[IDX] == '-':
				if st[IDX + 1] == '-':
					IDX = IDX + 2				
					while st[IDX] != '\n':
						IDX = IDX + 1
				else:
					IDX = IDX + 1
					return "MinusOp"

			# all invalid characters
			else:
				IDX = IDX + 1
				return "LexicalError"				# include error char
	
def main():
	f = open('input1.txt', 'r')
	# add terminating character at end
	code_string = f.read() + EOF
	token_count = 1
	# run scanner until the end of the code string is reached
	while IDX < len(code_string):
		print token_count, Scanner(code_string)
		token_count = token_count + 1
		#print IDX

main()


