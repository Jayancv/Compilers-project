from src.compiler.parser import parser
from src.compiler.symTab import SymTab
from src.compiler.tokenizer import tokenize
from src.compiler.type_checker import typecheck
from src.compiler.types import Int, Bool, Unit


def get_new_symTab() -> SymTab:
    return SymTab(locals={}, parent=None)


def test_type_checker() -> None:
    assert typecheck(parser(tokenize('1+2')), get_new_symTab()) == Int
    assert typecheck(parser(tokenize('1+2>3')), get_new_symTab()) == Bool
    assert typecheck(parser(tokenize('if 1 > 3 then 4')), get_new_symTab()) == Unit
    assert typecheck(parser(tokenize('if 1 > 3 then 4 else 2')), get_new_symTab()) == Int
    assert typecheck(parser(tokenize('if 1>3 then 4>0 else 2<1')), get_new_symTab()) == Bool
    assert typecheck(parser(tokenize('var a: Int = 1')), get_new_symTab()) == Int
    assert typecheck(parser(tokenize('var b: Bool = false')), get_new_symTab()) == Bool

    fail_typechecker('(1<3)+2')
    fail_typechecker('if 1  then 2 else 4')
    fail_typechecker('if 1<3 then 2 else 3>0')
    fail_typechecker('var x: Int = true')
    fail_typechecker('var x: Bool = 2')


def fail_typechecker(code: str) -> None:
    expr = parser(tokenize(code))
    failed = False
    try:
        typecheck(expr, get_new_symTab())
    except Exception:
        failed = True

    assert failed, f'Type checking done for {code}'
