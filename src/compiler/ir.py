from dataclasses import dataclass


@dataclass(frozen=True)
class IRVar:
    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Instruction():
    """Base class for IR instructions"""


@dataclass(frozen=True)
class Call(Instruction):
    func: IRVar
    args: list[IRVar]
    dest: IRVar


@dataclass(frozen=True)
class LoadIntConst(Instruction):
    value: int
    dest: IRVar


@dataclass(frozen=True)
class Copy(Instruction):
    source: IRVar
    dest: IRVar


@dataclass(frozen=True)
class Label(Instruction):
    name: str


@dataclass(frozen=True)
class Jump(Instruction):
    label: Label


@dataclass(frozen=True)
class CondJump(Instruction):
    cond: IRVar
    then_label: Label
    else_label: Label
