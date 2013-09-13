# holds different values based on type
# maybe could just be a dictionary with value mapped to Kind?
class ExprRec:
    def __init__(self, name, kind):
        self.kind = kind
        self.name = name

# generator only works for +
class OpRec:
    def __init__(self, opType):
        self.op = opType

