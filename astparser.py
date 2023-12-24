from lexer import *
from peekable import *

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

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = Peekable(lexer)
    def parse(self):
        nodes = []

        try:
            while True:
                stmt = self.statement()
                nodes.append(stmt)
                print(stmt)
        except StopIteration: pass

        return nodes
    def statement(self):
        return self.expression()
    def label(self):
        expr = self.expression()
        if not isinstance(expr, Ident):
            return expr
        try:
            self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == ':')
        except StopIteration: return expr

        return Label(expr.ident)
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
    def indexing(self):
        try: self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == '[')
        except StopIteration: return self.grouping()

        try:
            index = self.expression()
        except StopIteration: raise SyntaxError("Expected expression")
    
    def grouping(self):
        try: self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == '(')
        except StopIteration: return self.primary()

        try: node = self.expression()
        except StopIteration: raise SyntaxError("Expected expression")
        
        try: self.lexer.next_if(lambda token: isinstance(token, Symbol) and token.symbol == ')')
        except StopIteration: raise SyntaxError("Expected closing parenthesis")        

        return node
    def primary(self):
        try: return self.lexer.next_if(lambda token: isinstance(token, Character | String | Integer))
        except StopIteration: raise SyntaxError("Expected one of identifier, character, string, integer")