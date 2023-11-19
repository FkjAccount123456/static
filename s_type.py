from s_ast import Scope
import s_ast as ast
from s_type import *
from typing import Any


class Type:
    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...

    def __eq__(self, other) -> bool:
        ...

    def issubscriptable(self) -> bool:
        ...

    def new(self) -> Any:
        ...


class BasicType(Type):
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, BasicType) and self.name == other.name

    def issubscriptable(self) -> bool:
        return self.name == "str"

    def new(self) -> Any:
        if self.name == "int":
            return 0
        elif self.name == "bool":
            return False
        elif self.name == "float":
            return 0.0
        elif self.name == "str":
            return ""
        elif self.name == "NoneType":
            return None
        else:
            return None


class TemplateType(Type):
    def __init__(self, tname: str, targs: list[Type]):
        self.tname, self.targs = tname, targs

    def __str__(self) -> str:
        return "{}<{}>".format(self.tname, ", ".join(map(str, self.targs)))

    def __repr__(self) -> str:
        return "{}<{}>".format(self.tname, ", ".join(map(str, self.targs)))

    def __eq__(self, other) -> bool:
        return isinstance(other, TemplateType) and self.tname == other.tname and self.targs == other.targs

    def issubscriptable(self) -> bool:
        return self.tname == "list"

    def new(self) -> Any:
        if self.tname == "list":
            return []
        else:
            return None


def ListType(base: Type):
    return TemplateType("list", [base])


def FunctionType(ret_type: Type, param_types: list[Type]):
    return TemplateType("function", [ret_type, *param_types])


IntType = BasicType("int")
FloatType = BasicType("float")
BoolType = BasicType("bool")
StrType = BasicType("str")
NoneType = BasicType("None")


class Function:
    def __init__(self, params: list[str], param_types: list[Type], ret_type: Type, body: ast.Block, closure: Scope):
        self.params, self.param_types = params, param_types
        self.ret_type = ret_type
        self.body = body
        self.closure = closure

    def __call__(self, *args):
        new_scope = Scope(self.closure)
        new_scope.variables = dict(zip(self.params, args))
        ret = self.body.run(new_scope)
        if ret is None:
            return ret
        return ret.ret_val
