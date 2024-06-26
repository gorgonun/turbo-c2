from turbo_c2.turbo_events.event_store.event_store import EventStore
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.operators.event_expression import EventExpression
from turbo_c2.turbo_events.operators.event_operators import (
    Operation,
    And,
    Or,
    Not,
)


class EventOperatorController:
    def __init__(self, operation: Operation | And | Or | Not) -> None:
        self.__operation = operation

    async def evaluate(self, event_store: EventStore, cache: dict[EventReference, bool] | None = None):
        # FIXME: add cache for tree evaluation
        events = {}

        async def evaluate_operation(
            operation: Operation | And | Or | Not | EventExpression,
        ):

            if isinstance(operation, Operation):
                return await evaluate_operation(operation.operand)

            elif isinstance(operation, And):
                return (await evaluate_operation(operation.first_operand)) and (
                    await evaluate_operation(operation.second_operand)
                )

            elif isinstance(operation, Or):
                return (await evaluate_operation(operation.first_operand)) or (
                    await evaluate_operation(operation.second_operand)
                )

            elif isinstance(operation, Not):
                return not (await evaluate_operation(operation.operand))

            if cache:
                result = cache[operation.reference]
                events[operation.reference] = result[0] if isinstance(result, list) and len(result) == 1 else result
                return result

            return await event_store.event_happened(operation.reference)

        return await evaluate_operation(self.__operation), list(events.values())
