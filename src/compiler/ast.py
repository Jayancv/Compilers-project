from dataclasses import dataclass, field

from src.compiler.tokenizer import SourceLocation
from src.compiler.types import Type, Unit, BasicType


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


@dataclass
class BreakContinue(Expression):
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BreakContinue):
            return NotImplemented

        return self.name == other.name


@dataclass
class Return(Expression):
    value: Expression | None


@dataclass
class FunctionDef():
    location: SourceLocation
    name: Identifier
    params: list[Identifier]
    param_types: list[BasicType]
    body: Block
    return_type: BasicType


@dataclass
class Module:
    "base class for expressions and fun definitions"
    functions: list[FunctionDef]
    expr: Expression | None
