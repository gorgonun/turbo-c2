from __future__ import annotations
from typing import Generic, TypeVar, cast
from turbo_c2.turbo_events.operators.references import HasReference, HasReferences
from turbo_c2.turbo_events.operators import boolean


T = TypeVar("T", HasReference, HasReferences)
class BooleanWithReference(boolean.Boolean, Generic[T]):
    pass

B = TypeVar("B", bound=BooleanWithReference)


class And(boolean.And, HasReferences):
    def __init__(self, first_operand: Operation, second_operand: Operation):
        super().__init__(first_operand, second_operand)
        HasReferences.__init__(self, [*first_operand.references, *second_operand.references])

    def __repr__(self):
        return f"{self.__class__.__name__}({self.first_operand}, {self.second_operand})"
    
    def __str__(self):
        return repr(self)
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        return repr(self) == repr(other)


class Or(boolean.Or, HasReferences):
    def __init__(self, first_operand: Operation, second_operand: Operation):
        super().__init__(first_operand, second_operand)
        HasReferences.__init__(self, [*first_operand.references, *second_operand.references])

    def __repr__(self):
        return f"{self.__class__.__name__}({self.first_operand}, {self.second_operand})"
    
    def __str__(self):
        return repr(self)
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        return repr(self) == repr(other)


class Not(boolean.Not, HasReferences):
    def __init__(self, predicate: Operation):
        super().__init__(predicate)
        HasReferences.__init__(self, predicate.references)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.operand})"
    
    def __str__(self):
        return repr(self)
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        return repr(self) == repr(other)


class Operation(boolean.Operation, HasReferences):
    def __init__(self, predicate: B):
        super().__init__(predicate)
        HasReferences.__init__(self, [predicate.reference] if isinstance(predicate, HasReference) else cast(HasReferences, predicate).references)

    def and_(self, operation: B):
        return self.__and__(operation)
    
    def or_(self, operation: B):
        return self.__or__(operation)
    
    def not_(self):
        return self.__invert__()

    def __and__(self, operation: B):
        return self.__class__(And(Operation(self.operand), operation))
    
    def __or__(self, operation: B):
        return self.__class__(Or(Operation(self.operand), operation))
    
    def __invert__(self):
        return self.__class__(Not(Operation(self.operand)))
    
    def __str__(self):
        return str(self.operand)
    
    def __repr__(self):
        return str(self.operand)
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        return repr(self) == repr(other)
