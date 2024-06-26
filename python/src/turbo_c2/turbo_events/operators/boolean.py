from __future__ import annotations
import abc
from typing import TypeVar


T = TypeVar("T")


class Boolean(abc.ABC):
    pass


class BinaryOperation(Boolean):
    def __init__(self, first_operand: Boolean, second_operand: Boolean) -> None:
        self.first_operand = first_operand
        self.second_operand = second_operand

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.first_operand}, {self.second_operand})"


class UnaryOperation(Boolean):
    def __init__(self, operand: Boolean) -> None:
        self.operand = operand

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.operand})"


class And(BinaryOperation):
    def __init__(self, first_operand: Boolean, second_operand: Boolean):
        self.first_operand = first_operand
        self.second_operand = second_operand
        super().__init__(first_operand, second_operand)

    def __bool__(self) -> bool:
        return bool(self.first_operand) and bool(self.second_operand)


class Or(BinaryOperation):
    def __init__(self, first_operand: Boolean, second_operand: Boolean):
        self.first_operand = first_operand
        self.second_operand = second_operand

        super().__init__(first_operand, second_operand)

    def __bool__(self) -> bool:
        return bool(self.first_operand) or bool(self.second_operand)
    

class Not(UnaryOperation):
    def __init__(self, operand: Boolean):
        self.operand = operand

        super().__init__(operand)

    def __bool__(self) -> bool:
        return not bool(self.operand)


class Operation(UnaryOperation):
    def __init__(self, operand: Boolean):
        self.operand = operand

        super().__init__(operand)

    def __and__(self, operation: Boolean):
        return self.__class__(And(self.operand, operation))
    
    def __or__(self, operation: Boolean):
        return self.__class__(Or(self.operand, operation))
    
    def __invert__(self):
        return self.__class__(Not(self.operand))

    def __bool__(self) -> bool:
        return bool(self.operand)
    
    def __repr__(self) -> str:
        return str(self.operand)
