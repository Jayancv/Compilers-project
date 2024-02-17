from dataclasses import dataclass


@dataclass
class Expression:
    """Abstract base class for AST tree nodes"""


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class Literal(Expression):
    value: int


@dataclass
class Operators(Expression):
    operation: str


@dataclass
class TreeOperator(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class IfExpression(Expression):
    condition: Expression
    then_clause: Expression
    else_clause: Expression | None
