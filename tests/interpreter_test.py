from src.compiler.interpreter import interpret
from src.compiler.parser import parser
from src.compiler.symTab import SymTab, interpreter_locals
from src.compiler.tokenizer import tokenize

symtable = SymTab(locals=interpreter_locals, parent=None)


def test_interpreter() -> None:
    assert interpret(symtable, parser(tokenize('1+2'))) == 3
    assert interpret(symtable, parser(tokenize('1+2 *3'))) == 7
    assert interpret(symtable, parser(tokenize('1-2'))) == -1
    assert interpret(symtable, parser(tokenize(' if 1<2 then  1 else 0 '))) == 1
    assert interpret(symtable, parser(tokenize(' if 1>2 then  1 else 0 '))) == 0
    assert interpret(symtable, parser(tokenize(' { var x = 1; x = x * 10; x = x - 2; x = x / 2; x } '))) == 4
    assert interpret(symtable, parser(tokenize(' { var a = 1; var b = a * 10; var c = b - 2; a = c / 2; a } '))) == 4
