from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize
from src.compiler.type_checker import typecheck
from src.compiler.types import Int, Bool, Unit


def test_type_checker() -> None:
    assert typecheck(parser(tokenize('1+2'))) == Int
    assert typecheck(parser(tokenize('1+2>3'))) == Bool
    assert typecheck(parser(tokenize('if 1 > 3 then 4'))) == Unit
    assert typecheck(parser(tokenize('if 1 > 3 then 4 else 2'))) == Int
    assert typecheck(parser(tokenize('if 1>3 then 4>0 else 2<1'))) == Bool



    fail_typechecker('(1<3)+2')
    fail_typechecker('if 1  then 2 else 4')
    fail_typechecker('if 1<3 then 2 else 3>0')


def fail_typechecker(code: str) -> None:
    expr = parser(tokenize(code))
    failed = False
    try:
        typecheck(expr)
    except Exception:
        failed = True

    assert failed, f"Type checking done for {code}"
