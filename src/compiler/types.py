from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    """Base class of the main types"""


@dataclass(frozen=True)
class BasicType(Type):
    name: str


Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')
