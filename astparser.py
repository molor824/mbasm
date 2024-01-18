from lexer import *
from peekable import *
from copy import deepcopy

class Label:
    def __init__(self, label: str):
        self.label = label
    def __str__(self):
        return f"label({self.label})"
class Unary:
    def __init__(self, operand, op: str):
        self.operand = operand
        self.op = op
    def __str__(self):
        return f"unary({self.operand} {self.op})"
class Binary:
    def __init__(self, lhs, rhs, op: str):
        self.rhs = rhs
        self.lhs = lhs
        self.op = op
    def __str__(self):
        return f"binary({self.lhs} {self.rhs} {self.op})"
class Indexing:
    def __init__(self, base_reg: str, index):
        self.base_reg = base_reg
        self.index = index
    def __str__(self):
        return f"indexing({self.base_reg} {self.index})"
class Instruction:
    def __init__(self, name: str, fields: list[str], args: list):
        self.name = name
        self.fields = fields
        self.args = args
    def __str__(self):
        return f"instruction({self.name}.{'.'.join(map(str, self.fields))} {' '.join(map(str, self.args))})"

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = Peekable(lexer)
    def parse(self):
        nodes = []

        try:
            while True:
                # skip newlines
                try:
                    while True:
                        self.lexer.next_if(lambda token: isinstance(token, Newline))
                except StopIteration: pass

                stmt = self.statement()
                nodes.append(stmt)

                try: self.lexer.next_if(lambda token: isinstance(token, Newline))
                except StopIteration: break
        except StopIteration: pass

        try:
            self.lexer.peek()
            raise SyntaxError("Expected newline")
        except StopIteration: pass

        return nodes
    def statement(self):
        try: return self.label()
        except StopIteration: pass
        return self.instruction()
    def instruction(self):
        name = self.lexer.next_if(lambda token: isinstance(token, Ident)).ident
        fields = []
        args = []

        try:
            while True:
                self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == '.')
                try:
                    fields.append(self.lexer.next_if(lambda token: isinstance(token, Ident)).ident)
                    continue
                except StopIteration: pass
                try: fields.append(self.lexer.next_if(lambda token: isinstance(token, Integer)).integer)
                except StopIteration: raise SyntaxError("Expected field")
        except StopIteration: pass
        try:
            args.append(self.instruction_arg())
            while True:
                self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == ',')
                try: args.append(self.instruction_arg())
                except StopIteration: raise SyntaxError("Expected argument")
        except StopIteration: pass

        return Instruction(name, fields, args)
    def instruction_arg(self):
        try: return self.expression()
        except StopIteration: pass
        return self.indexing()
    def label(self):
        copied = deepcopy(self.lexer)
        label = copied.next_if(lambda token: isinstance(token, Ident)).ident
        copied.next_if(lambda token: isinstance(token, Symbol) and token.symbol == ':')
        next(self.lexer)
        next(self.lexer)
        return Label(label)
    def indexing(self):
        base = self.lexer.next_if(lambda token: isinstance(token, Ident))

        try: self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == '[')
        except StopIteration: return base

        try: index = self.expression()
        except StopIteration: raise SyntaxError("Expected index")

        try: self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == ']')
        except StopIteration: raise SyntaxError("Expected ']'")

        return Indexing(base.ident, index)
    def expression(self):
        return self.bitwise_or()
    def bitwise_or(self):
        return self.binary(self.bitwise_xor, self.bitwise_xor, {'|'})
    def bitwise_xor(self):
        return self.binary(self.bitwise_and, self.bitwise_and, {'^'})
    def bitwise_and(self):
        return self.binary(self.shift, self.shift, {'&'})
    def shift(self):
        return self.binary(self.term, self.term, {'<<', '>>'})
    def term(self):
        return self.binary(self.factor, self.factor, {'+', '-'})
    def factor(self):
        return self.binary(self.unary, self.unary, {'*', '/', '%'})
    def binary(self, lhs: Callable, rhs: Callable, operators: set[str]):
        left = lhs()
        
        try:
            while True:
                token = self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol in operators)
                right = rhs()
                left = Binary(left, right, token.symbol)
        except StopIteration: pass
        
        return left
    def unary(self):
        try:
            token = self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol in ['+', '-', '~'])
        except StopIteration: return self.grouping()
        
        return Unary(self.unary(), token.symbol)
    def grouping(self):
        try: self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == '(')
        except StopIteration: return self.integer()

        try: node = self.expression()
        except StopIteration: raise SyntaxError("Expected expression")
        
        try: self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == ')')
        except StopIteration: raise SyntaxError("Expected closing parenthesis")        

        return node
    def integer(self):
        return self.lexer.next_if(lambda token: isinstance(token, Character | Integer))