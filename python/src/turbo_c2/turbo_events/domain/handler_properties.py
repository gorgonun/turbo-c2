from dataclasses import dataclass

from turbo_c2.turbo_events.domain.handler_after_execution_property_enum import HandlerAfterExecutionPropertyEnum


@dataclass
class HandlerProperties():
    after_true: HandlerAfterExecutionPropertyEnum = HandlerAfterExecutionPropertyEnum.KEEP
    after_false: HandlerAfterExecutionPropertyEnum = HandlerAfterExecutionPropertyEnum.KEEP
