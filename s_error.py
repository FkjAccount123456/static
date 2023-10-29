class SException(Exception):
    """所有不可恢复错误的基类"""


class SSyntaxError(SException):
    """语法错误"""


class SNameError(SException):
    """未定义的变量/函数/类型"""


class STypeError(SException):
    """类型错误"""
