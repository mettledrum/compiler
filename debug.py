# prints the push and pop stack calls for debugging and viewing recursion
class StackViewer:
	def __init__(self, spacing_string = "  "):
		# for indenting the functions
		self.indent_val = 0
		# what is displayed for indentation
		self.spacing = spacing_string
		# off by default
		self.switch = False

	def turn_on(self):
		self.switch = True

	def turn_off(self):
		self.switch = False

	def into(self, f_name):
		if self.switch:
			self.indent_val = self.indent_val + 1
			print self.spacing * self.indent_val, f_name, "IN"

	def outa(self, f_name):
		if self.switch:
			print self.spacing * self.indent_val, f_name, "OUT"
			self.indent_val = self.indent_val - 1

	def match_show(self, tok):
		if self.switch:
			self.indent_val = self.indent_val + 1
			print self.spacing * self.indent_val, tok
			self.indent_val = self.indent_val - 1

