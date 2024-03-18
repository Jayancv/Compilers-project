from src.compiler.ir_generator import generate_ir
from src.compiler.parser import parser
from src.compiler.symTab import SymTab, root_types
from src.compiler.tokenizer import tokenize
from src.compiler.type_checker import typecheck


def test_generate_ir_exp() -> None:
    nodes = parser(tokenize('1 + 2 * 3'))
    if nodes is None:
        raise Exception('Failed to parse input')
    typecheck(nodes, SymTab(locals={}, parent=None))
    expected = [
        'LoadIntConst(1, x1)',
        'LoadIntConst(2, x2)',
        'LoadIntConst(3, x3)',
        'Call(*, [x2, x3], x4)',
        'Call(+, [x1, x4], x5)',
        'Call(print_int, [x5], x6)'
    ]

    ir_instructions = generate_ir(root_types, nodes)
    output = [str(ins) for ins in ir_instructions['main']]

    assert output == expected


def test_generate_ir_var() -> None:
    nodes = parser(tokenize('{ var x=3; x+2;}'))
    if nodes is None:
        raise Exception('Failed to parse input')
    typecheck(nodes, SymTab(locals={}, parent=None))
    expected = ['LoadIntConst(3, x1)',
                'Copy(x1, x2)',
                'LoadIntConst(2, x3)',
                'Call(+, [x2, x3], x4)']

    ir_instructions = generate_ir(root_types, nodes)
    output = [str(ins) for ins in ir_instructions['main']]

    assert output == expected


def test_generate_ir_opt() -> None:
    nodes = parser(tokenize('true and true'))
    if nodes is None:
        raise Exception('Failed to parse input')
    typecheck(nodes, SymTab(locals={}, parent=None))
    expected = ['LoadBoolConst(True, x1)',
                'CondJump(x1, Label(L1), Label(L2))',
                'Label(L1)',
                'LoadBoolConst(True, x2)',
                'Copy(x2, x3)',
                'Jump(Label(L3))',
                'Label(L2)',
                'LoadBoolConst(False, x3)',
                'Jump(Label(L3))',
                'Label(L3)',
                'LoadBoolConst(True, x4)',
                'Call(and, [x1, x4], x5)',
                'Call(print_bool, [x5], x6)']

    ir_instructions = generate_ir(root_types, nodes)
    output = [str(ins) for ins in ir_instructions['main']]

    assert output == expected
