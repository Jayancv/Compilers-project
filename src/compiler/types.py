from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    """Base class of the main types"""


@dataclass(frozen=True)
class BasicType(Type):
    name: str


@dataclass(frozen=True)
class FunctionType(Type):
    params: list[BasicType]
    return_type: BasicType


Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')

# Function types
Arithmetic = FunctionType([Int, Int], Int)
Comparison = FunctionType([Int, Int], Bool)
Logical = FunctionType([Bool, Bool], Bool)

PrintInt = FunctionType([Int], Unit)
PrintBool = FunctionType([Bool], Unit)
ReadInt = FunctionType([], Int)
