from s_data import TokenType, prio
from s_lex import Token, Lexer
from s_error import SSyntaxError
import s_ast as ast
from s_type import *


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = lexer.next()

    def eat(self, expect: TokenType | None = None) -> Token:
        if expect and self.token.tp != expect:
            raise SSyntaxError(
                f"unexpected token '{self.token.tp}' at line {self.token.ln}, column {self.token.col}, expected '{expect}'.")
        old = self.token
        self.token = self.lexer.next()
        return old

    def parse_block(self) -> ast.Block:
        stmts: list[ast.Stmt] = []
        self.eat(TokenType.BEGIN)
        while self.token.tp != TokenType.END:
            stmts.append(self.parse_stmt())
        self.eat(TokenType.END)
        return ast.Block(stmts)

    def parse_expr(self) -> ast.Expr:
        res = self.parse_factor()

        if self.token.tp in prio:
            op = self.eat().tp
            res = ast.Binary(op, res, self.parse_factor())
            while self.token.tp in prio:
                op = self.eat().tp
                factor = self.parse_factor()
                if prio[res.op] > prio[op]:
                    res = ast.Binary(op, res, factor)
                else:
                    res = ast.Binary(res.op, res.left,
                                     ast.Binary(op, res.right, factor))

        return res

    def parse_factor(self) -> ast.Expr:
        prefix = []
        while self.token.tp in (TokenType.ADD, TokenType.SUB, TokenType.NOT, TokenType.INV):
            prefix.append(self.eat())

        if self.token.tp == TokenType.CONST:
            res = ast.Const(self.eat().val)
        elif self.token.tp == TokenType.ID:
            res = ast.Variable(self.eat().val)
        elif self.token.tp == TokenType.LPAREN:
            self.eat()
            res = self.parse_expr()
            self.eat(TokenType.RPAREN)
        else:
            raise SSyntaxError(
                f"unknown token '{self.token.tp}' at line {self.token.ln}, column {self.token.col}.")

        while self.token in ():
            ...

        for i in reversed(prefix):
            res = ast.Unary(i, res)
        return res

    def parse_var_decl(self) -> tuple[str, Type, ast.Expr | None]:
        name = self.eat(TokenType.ID).val
        self.eat(TokenType.COLON)
        tp = self.parse_type()
        if self.token.tp == TokenType.ASSIGN:
            self.eat()
            val = self.parse_expr()
        else:
            val = None
        return name, tp, val

    def parse_stmt(self) -> ast.Stmt:
        if self.token.tp == TokenType.SEMICOLON:
            self.eat()
            return ast.NoOp()
        elif self.token.tp == TokenType.IF:
            self.eat()
            cases = [(self.parse_expr(), self.parse_block())]
            while self.token.tp == TokenType.ELSE:
                self.eat()
                if self.token.tp != TokenType.IF:
                    return ast.IfStmt(cases, self.parse_block())
                cases.append((self.parse_expr(), self.parse_block()))
            return ast.IfStmt(cases, ast.Block([]))
        elif self.token.tp == TokenType.WHILE:
            self.eat()
            return ast.WhileStmt(self.parse_expr(), self.parse_block())
        elif self.token.tp == TokenType.LET:
            self.eat()
            variables = [self.parse_var_decl()]
            while self.token.tp == TokenType.COMMA:
                self.eat()
                variables.append(self.parse_var_decl())
            self.eat(TokenType.SEMICOLON)
            return ast.VarDecl(variables)
        else:
            left = self.parse_expr()
            self.eat(TokenType.SEMICOLON)
            return ast.ExprStmt(left)

    def parse_type(self) -> Type:
        res = self.eat(TokenType.ID).val

        if self.token.tp == TokenType.LT:
            self.eat()
            targs: list[Type] = []
            if self.token.tp != TokenType.GT:
                targs.append(self.parse_type())
                while self.token.tp == TokenType.COMMA:
                    self.eat()
                    targs.append(self.parse_type())
            self.eat(TokenType.GT)
            res = TemplateType(res, targs)
        else:
            res = BasicType(res)

        while self.token.tp == TokenType.LSQBR:
            self.eat()
            res = ListType(res)
            self.eat(TokenType.RSQBR)

        return res
