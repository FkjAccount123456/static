class Type:
    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...

    def __eq__(self, other) -> bool:
        ...

    def issubscriptable(self) -> bool:
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


def ListType(base: Type):
    return TemplateType("list", [base])


IntType = BasicType("int")
FloatType = BasicType("float")
BoolType = BasicType("bool")
StrType = BasicType("str")
NoneType = BasicType("None")
