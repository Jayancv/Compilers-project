from dataclasses import dataclass, field

from src.compiler.tokenizer import SourceLocation
from src.compiler.types import Type, Unit


@dataclass
class AstType:
    """Abstract base class for AST tree type node"""


@dataclass
class TypeInt(AstType):
    type: str


@dataclass
class TypeBool(AstType):
    type: str


@dataclass
class Expression:
    """Abstract base class for AST tree nodes"""
    location: SourceLocation
    type: Type = field(kw_only=True, default=Unit)  # use for type checking


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class Literal(Expression):
    value: int | bool | None


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


@dataclass
class UnaryOp(Expression):
    operator: str
    expr: Expression


@dataclass
class VarDeclaration(Expression):
    name: Identifier
    var_type: AstType | None
    value: Expression


@dataclass
class WhileLoop(Expression):
    condition: Expression
    do_action: Expression


@dataclass
class Block(Expression):
    statements: list[Expression]


@dataclass
class FunctionCall(Expression):
    call: Identifier
    args: list[Expression]
