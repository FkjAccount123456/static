from typing import Any
from s_error import SSyntaxError
from s_data import TokenType, operators, escape, keywords


class Token:
    def __init__(self, ln: int, col: int, tp: TokenType, val: Any = None):
        self.ln, self.col, self.tp, self.val = ln, col, tp, val


class CodeStream:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.ln, self.col = 0, 0

    def cur(self):
        if self.pos >= len(self.code):
            raise SSyntaxError("unexpected EOF.")
        return self.code[self.pos]

    def next(self, num: int = 1):
        for i in range(num):
            if self.pos < len(self.code):
                if self.code[self.pos] == '\n':
                    self.ln += 1
                    self.col = 0
                else:
                    self.col += 1
                self.pos += 1
            else:
                break

    def cmp(self, pat: str, skip: bool = False):
        if self.pos + len(pat) >= len(self.code):
            return False
        for i in range(len(pat)):
            if pat[i] != self.code[self.pos + i]:
                return False
        self.next(len(pat))
        return True

    def eof(self):
        return self.pos >= len(self.code)


class Lexer:
    def __init__(self, code: str):
        self.code = CodeStream(code)

    def skip(self):
        while not self.code.eof() and (self.code.cur() in " \n\t" or self.code.cmp("//") or self.code.cmp("/*")):
            if self.code.cur() in " \n\t":
                self.code.next()
            elif self.code.cmp("//"):
                while not self.code.eof() and self.code.cur() != '\n':
                    self.code.next()
            else:
                self.code.next(2)
                while not self.code.cmp("*/"):
                    self.code.next()
                self.code.next(2)

    def escape(self):
        if self.code.eof():
            raise SSyntaxError("unexpected EOF.")
        elif self.code.cur() in escape:
            res = escape[self.code.cur()]
            self.code.next()
            return res
        elif ord('0') <= ord(self.code.cur()) <= ord('7'):
            res = ord(self.code.cur()) - ord('0')
            self.code.next()
            while not self.code.eof() and ord('0') <= ord(self.code.cur()) <= ord('7'):
                res *= 8
                res += ord(self.code.cur()) - ord('0')
                self.code.next()
            return chr(res)
        else:
            raise SSyntaxError("unknown escape sequence at line {}, column {}.".format(
                self.code.ln, self.code.col))

    def next(self):
        self.skip()

        if self.code.eof():
            return Token(self.code.ln, self.code.col, TokenType.EOF)
        elif self.code.cur().isdigit():
            num = ""
            while not self.code.eof() and (self.code.cur().isdigit() or self.code.cur() == '.'):
                num += self.code.cur()
                self.code.next()
            if num.count('.') == 1:
                return Token(self.code.ln, self.code.col, TokenType.CONST, float(num))
            if num.count('.') > 1:
                raise SSyntaxError(f"wrong number '{num}'.")
            return Token(self.code.ln, self.code.col, TokenType.CONST, int(num))
        elif self.code.cur().isalpha():
            ident = ""
            while not self.code.eof() and (self.code.cur().isalnum() or self.code.cur() == '_'):
                ident += self.code.cur()
                self.code.next()
            if ident in keywords:
                return Token(self.code.ln, self.code.col, keywords[ident])
            elif ident == 'True':
                return Token(self.code.ln, self.code.col, TokenType.CONST, True)
            elif ident == 'False':
                return Token(self.code.ln, self.code.col, TokenType.CONST, False)
            elif ident == 'None':
                return Token(self.code.ln, self.code.col, TokenType.CONST, None)
            else:
                return Token(self.code.ln, self.code.col, TokenType.ID, ident)
        elif self.code.cur() == '"':
            self.code.next()
            string = ""
            while self.code.cur() != '"':
                if self.code.cur() == '\\':
                    self.code.next()
                    string += self.escape()
                else:
                    string += self.code.cur()
                    self.code.next()
            self.code.next()
            return Token(self.code.ln, self.code.col, TokenType.CONST, string)
        else:
            for pat, res in operators:
                if self.code.cmp(pat, True):
                    return Token(self.code.ln, self.code.col, res)
            raise SSyntaxError(f"unknown character '{self.code.cur()}'.")
