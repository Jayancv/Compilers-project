from src.compiler.interpreter import interpret
from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize


def test_interpreter() -> None:
    assert interpret(parser(tokenize('1+2'))) == 3
    assert interpret(parser(tokenize('1+2 *3'))) == 7
    assert interpret(parser(tokenize('1-2'))) == -1
    assert interpret(parser(tokenize(' if 1<2 then  1 else 0 '))) == 1
    assert interpret(parser(tokenize(' if 1>2 then  1 else 0 '))) == 0
