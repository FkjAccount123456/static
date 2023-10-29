from enum import Enum, unique


@unique
class TokenType(Enum):
    EOF = 0
    # Operators
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    MOD = 30
    EQ = 5
    NE = 6
    GT = 7
    LT = 8
    GE = 9
    LE = 10
    LSH = 11
    RSH = 12
    AND = 13
    OR = 14
    BITAND = 15
    BITOR = 16
    XOR = 17
    NOT = 18
    INV = 19
    LPAREN = 20
    RPAREN = 21
    LSQBR = 22
    RSQBR = 23
    BEGIN = 24
    END = 25
    COMMA = 26
    COLON = 27
    SEMICOLON = 28
    ASSIGN = 29
    # Val
    ID = 100
    CONST = 101
    # Keywords
    IF = 200
    ELSE = 201
    WHILE = 202
    LET = 203
    FN = 204
    RETURN = 207
    BREAK = 205
    CONTINUE = 206


operators = [
    ('+', TokenType.ADD),
    ('-', TokenType.SUB),
    ('*', TokenType.MUL),
    ('/', TokenType.DIV),
    ('%', TokenType.MOD),
    ('==', TokenType.EQ),
    ('!=', TokenType.NE),
    ('>=', TokenType.GE),
    ('<=', TokenType.LE),
    ('<<', TokenType.LSH),
    ('>>', TokenType.RSH),
    ('>', TokenType.GT),
    ('<', TokenType.LT),
    ('&&', TokenType.AND),
    ('||', TokenType.OR),
    ('&', TokenType.BITAND),
    ('|', TokenType.BITOR),
    ('^', TokenType.XOR),
    ('!', TokenType.NOT),
    ('~', TokenType.INV),
    ('(', TokenType.LPAREN),
    (')', TokenType.RPAREN),
    ('[', TokenType.LSQBR),
    (']', TokenType.RSQBR),
    ('{', TokenType.BEGIN),
    ('}', TokenType.END),
    (',', TokenType.COMMA),
    (':', TokenType.COLON),
    (';', TokenType.SEMICOLON),
]
escape = {
    'r': '\r',
    't': '\t',
    'a': '\a',
    'f': '\f',
    'v': '\v',
    'b': '\b',
    'n': '\n',
    '"': '"',
    '\'': '\'',
    '\\': '\\',
}
prio = {
    TokenType.MUL: 100,
    TokenType.DIV: 100,
    TokenType.MOD: 100,
    TokenType.ADD: 99,
    TokenType.SUB: 99,
    TokenType.LSH: 98,
    TokenType.RSH: 98,
    TokenType.EQ: 97,
    TokenType.NE: 97,
    TokenType.GT: 96,
    TokenType.LT: 96,
    TokenType.GE: 96,
    TokenType.LE: 96,
    TokenType.BITAND: 95,
    TokenType.BITOR: 94,
    TokenType.XOR: 93,
    TokenType.AND: 92,
    TokenType.OR: 91,
}
keywords = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "let": TokenType.LET,
    "fn": TokenType.FN,
    "return": TokenType.RETURN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
}
