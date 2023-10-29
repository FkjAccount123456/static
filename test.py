from s_parse import Parser
from s_lex import Lexer
from s_ast import Scope

text = "(1+1)*2"
lexer = Lexer(text)
parser = Parser(lexer)
print(parser.parse_expr().eval(Scope()))
