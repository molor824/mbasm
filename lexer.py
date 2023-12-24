from peekable import *

class Newline:
    def __str__(self):
        return "newline"
class Ident:
    def __init__(self, ident: str):
        self.ident = ident
    def __str__(self):
        return f"ident({self.ident})"
class Integer:
    def __init__(self, integer: int):
        self.integer = integer
    def __str__(self):
        return f"int({self.integer})"
class Symbol:
    def __init__(self, symbol: str):
        self.symbol = symbol
    def __str__(self):
        return f"symbol({self.symbol!r})"
class String:
    def __init__(self, string: str):
        self.string = string
    def __str__(self):
        return f"str({self.string!r})"
class Character:
    def __init__(self, character: str):
        self.character = character
    def __str__(self):
        return f"char({self.character!r})"

class Lexer:
    SYMBOLS = {
        '+', '-', '*', '/', '%', '>>', '<<', '&', '|', '^', '~', ':', ',', '.', '[', ']', '(', ')'
    }
    MAX_LEN = max(len(s) for s in SYMBOLS)
    ESCAPE_SEQUENCE = {
        'n': '\n',
        't': '\t',
        '0': '\0',
        '\'': '\'',
        '"': '"',
        '\\': '\\',
    }

    def __init__(self, source: str):
        self.source = source
        self.source_iter = Peekable(enumerate(source))
    def __iter__(self):
        return self
    def get_string(self, end_ch: str = '"') -> str:
        string_builder = [] # since arrays are mutable unlike strings, it should be more performent
        try:
            while True:
                _, c = self.source_iter.next_if(lambda c: c[1] != end_ch)
                if c == '\\':
                    try:
                        _, c = self.source_iter.next_if(lambda c: c[1] in self.ESCAPE_SEQUENCE)
                    except StopIteration:
                        raise SyntaxError(f"Invalid escape sequence: {c!r}")
                    string_builder.append(self.ESCAPE_SEQUENCE[c])
                    continue
                if c == '\n' or c == '\r':
                    raise SyntaxError("Unterminated string")
                string_builder.append(c)
        except StopIteration: pass
        next(self.source_iter)
        return ''.join(string_builder)
    def __next__(self):
        for i, c in self.source_iter:
            if c == '\n':
                return Newline()
            if c.isspace():
                continue
            if c == ';':
                for _, c in self.source_iter:
                    if c == '\n':
                        break
                continue
            if c.isalpha() or c == '_':
                start = i
                end = i + 1
                try:
                    while True:
                        i, _ = self.source_iter.next_if(lambda c: c[1].isalnum() or c[1] == '_')
                        end = i + 1
                except StopIteration: pass
                return Ident(self.source[start:end])
            if c.isdigit():
                value = int(c)
                try:
                    while True:
                        _, c = self.source_iter.next_if(lambda c: c[1].isdigit())
                        value = value * 10 + int(c)
                except StopIteration: pass
                return Integer(value)
            if c == '"':
                return String(self.get_string())
            if c == '\'':
                string = self.get_string('\'')
                if len(string) < 1:
                    raise SyntaxError("Expected one character, got nothing")
                elif len(string) > 1:
                    raise SyntaxError("Too many characters in character literal")
                return String(string)

            length = min(self.MAX_LEN + i, len(self.source))
            for i1 in range(length, i, -1):
                symbol = self.source[i:i1]
                if symbol in self.SYMBOLS:
                    for _ in range(i1 - i - 1):
                        next(self.source_iter)
                    return Symbol(symbol)
            raise SyntaxError(f"Invalid character: {c!r}")

        raise StopIteration()