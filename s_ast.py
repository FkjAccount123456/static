from typing import Any, TypeAlias
from s_type import *
from enum import Enum, unique
from s_error import SNameError, STypeError
from s_data import TokenType
from s_type import Type


@unique
class SignalType(Enum):
    RETURN = 0
    CONTINUE = 1
    BREAK = 2


class RunSignal:
    def __init__(self, signal: SignalType, ret_val: Any = None):
        self.signal, self.ret_val = signal, ret_val


class Scope:
    def __init__(self, parent: "Scope | None" = None):
        self.parent = parent
        self.variables: dict[str, Any] = {}
        self.functions: dict[str, Any] = {}

    def find(self, name: str):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.find(name)
        raise SNameError(f"undefined variable '{name}'.")

    def find_func(self, name: str):
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.find_func(name)
        raise SNameError(f"undefined function '{name}'.")

    def set(self, name: str, val):
        if name in self.variables:
            self.variables[name] = val
            return
        if self.parent:
            self.parent.set(name, val)
            return
        raise SNameError(f"undefined variable '{name}'.")

    def define(self, name: str, val):
        self.variables[name] = val


class Expr:
    """表达式"""

    def check(self, scope: Scope) -> Type:
        ...

    def eval(self, scope: Scope) -> Any:
        ...


class Stmt:
    """语句"""

    def check(self, scope: Scope) -> Type | None:
        ...

    def run(self, scope: Scope) -> RunSignal | None:
        ...


class Block(Stmt):
    def __init__(self, stmts: list[Stmt]):
        self.stmts = stmts

    def check(self, scope: Scope) -> Type | None:
        ret_type = None
        for stmt in self.stmts:
            ret = stmt.check(scope)
            if ret is not None:
                if ret_type is not None and ret_type != ret:
                    raise STypeError(
                        f"conflicting return type '{ret}' and '{ret_type}'.")
                ret_type = ret
        return ret_type

    def run(self, scope: Scope) -> RunSignal | None:
        for stmt in self.stmts:
            ret = stmt.run(scope)
            if ret:
                return ret


class NoOp(Stmt):
    ...


class ExprStmt(Stmt):
    def __init__(self, expr: Expr):
        self.expr = expr

    def check(self, scope: Scope) -> Type | None:
        self.expr.check(scope)

    def run(self, scope: Scope) -> RunSignal | None:
        self.expr.eval(scope)


class IfStmt(Stmt):
    def __init__(self, cases: list[tuple[Expr, Block]], else_block: Block):
        self.cases, self.else_block = cases, else_block

    def check(self, scope: Scope) -> Type | None:
        ret_type = None
        for cond, body in self.cases:
            cond.check(scope)
            ret = body.check(Scope(scope))
            if ret is not None:
                if ret_type is not None and ret_type != ret_type:
                    raise STypeError(
                        f"conflicting return type '{ret}' and '{ret_type}'.")
                ret_type = ret
        ret = self.else_block.check(Scope(scope))
        if ret is not None:
            if ret_type is not None and ret_type != ret_type:
                raise STypeError(
                    f"conflicting return type '{ret}' and '{ret_type}'.")
        return ret_type
    
    def run(self, scope: Scope) -> RunSignal | None:
        for cond, body in self.cases:
            if cond.eval(scope):
                return body.run(Scope(scope))
        return self.else_block.run(Scope(scope))
    

class WhileStmt(Stmt):
    def __init__(self, cond: Expr, body: Block):
        self.cond, self.body = cond, body

    def check(self, scope: Scope) -> Type | None:
        self.cond.check(scope)
        return self.body.check(Scope(scope))
    
    def run(self, scope: Scope) -> RunSignal | None:
        while self.cond.eval(scope):
            ret = self.body.run(Scope(scope))
            if ret:
                if ret.signal == SignalType.BREAK:
                    break
                if ret.signal == SignalType.RETURN:
                    return ret
                

class VarDecl(Stmt):
    def __init__(self, variables: list[tuple[str, Type, Expr | None]]):
        self.variables = variables

    def check(self, scope: Scope) -> Type | None:
        for name, tp, val in self.variables:
            scope.define(name, tp)

    def run(self, scope: Scope) -> RunSignal | None:
        for name, tp, val in self.variables:
            if val:
                scope.define(name, val.eval(scope))
            else:
                scope.define(name, None)


class Assign(Stmt):
    def __init__(self, left: Expr, right: Expr):
        self.left, self.right = left, right

    def check(self, scope: Scope) -> Type | None:
        if not isinstance(self.left, Variable) and not isinstance(self.left, IndexOp):
            raise STypeError("left of the assignment is not a l-value.")
        left = self.left.check(scope)
        right = self.right.check(scope)
        if left != right:
            raise STypeError(f"conflicting left type '{left}' and right type '{right}' when assigning.")

    def run(self, scope: Scope) -> RunSignal | None:
        right = self.right.eval(scope)
        if isinstance(self.left, Variable):
            scope.set(self.left.name, right)
        elif isinstance(self.left, IndexOp):
            left_base = self.left.base.eval(scope)
            left_index = self.left.index.eval(scope)
            left_base[left_index] = right


class Const(Expr):
    def __init__(self, val: Any):
        self.val = val

    def check(self, scope: Scope) -> Type | None:
        return BasicType(type(self.val).__name__)

    def eval(self, scope: Scope) -> Any:
        return self.val


class Variable(Expr):
    def __init__(self, name: str):
        self.name = name

    def check(self, scope: Scope) -> Type | None:
        return scope.find(self.name)

    def eval(self, scope: Scope) -> Any:
        return scope.find(self.name)


class Binary(Expr):
    def __init__(self, op: TokenType, left: Expr, right: Expr):
        self.op, self.left, self.right = op, left, right

    def check(self, scope: Scope) -> Type:
        op = self.op
        left, right = self.left.check(scope), self.right.check(scope)
        if op in (TokenType.EQ, TokenType.NE, TokenType.AND, TokenType.OR):
            return BasicType("bool")
        if isinstance(left, BasicType) and isinstance(right, BasicType) and \
                left.name in ("int", "float", "bool") and right.name in ("int", "float", "bool"):
            if op in (TokenType.GT, TokenType.LT, TokenType.GE, TokenType.LE):
                return BoolType
            if "float" in (left.name, right.name):
                return FloatType
            return IntType
        if op == TokenType.ADD and left.issubscriptable() and right.issubscriptable():
            return left
        if op == TokenType.MUL and (left == IntType and right.issubscriptable()
                                    or left.issubscriptable() and right == IntType):
            return right
        raise STypeError(
            f"unsupported binary operation '{op}' between type '{left}' and type '{right}'.")

    def eval(self, scope: Scope) -> Any:
        op = self.op
        left = self.left.eval(scope)
        if op == TokenType.AND:
            if not left:
                return False
            else:
                return bool(self.right.eval(scope))
        if op == TokenType.OR:
            if left:
                return True
            else:
                return bool(self.right.eval(scope))
        right = self.right.eval(scope)
        return {
            TokenType.ADD: lambda a, b: a + b,
            TokenType.SUB: lambda a, b: a - b,
            TokenType.MUL: lambda a, b: a * b,
            TokenType.DIV: lambda a, b: a / b,
            TokenType.MOD: lambda a, b: a % b,
            TokenType.EQ: lambda a, b: a == b,
            TokenType.NE: lambda a, b: a != b,
            TokenType.GT: lambda a, b: a > b,
            TokenType.LT: lambda a, b: a < b,
            TokenType.GE: lambda a, b: a >= b,
            TokenType.LE: lambda a, b: a <= b,
            TokenType.LSH: lambda a, b: a << b,
            TokenType.RSH: lambda a, b: a >> b,
            TokenType.BITAND: lambda a, b: a & b,
            TokenType.BITOR: lambda a, b: a | b,
            TokenType.XOR: lambda a, b: a ^ b,
        }[op](left, right)


class Unary(Expr):
    def __init__(self, op: TokenType, val: Expr):
        self.op, self.val = op, val

    def check(self, scope: Scope) -> Type:
        op = self.op
        val = self.val.check(scope)
        if op == TokenType.NOT:
            return BoolType
        if val in (IntType, BoolType):
            return IntType
        if val == FloatType:
            return FloatType
        raise STypeError(f"unsupported unary operation '{op}' on type '{val}'")

    def eval(self, scope: Scope) -> Any:
        return {
            TokenType.ADD: lambda x: +x,
            TokenType.SUB: lambda x: -x,
            TokenType.NOT: lambda x: not x,
            TokenType.INV: lambda x: ~x,
        }[self.op](self.val.eval(scope))
    

class IndexOp(Expr):
    def __init__(self, base: Expr, index: Expr):
        self.base, self.index = base, index

    def check(self, scope: Scope) -> Type:
        base, index = self.base.check(scope), self.index.check(scope)
        if index != IntType:
            raise STypeError(f"can't use type '{index}' as index.")
        if isinstance(index, TemplateType) and index.tname == "list":
            return index.targs[0]
        elif index == StrType:
            return StrType
        else:
            raise STypeError(f"type '{base}' is not subscriptable.")

    def eval(self, scope: Scope) -> Any:
        return self.base.eval(scope)[self.index.eval(scope)]
