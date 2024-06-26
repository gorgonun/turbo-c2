from typing import TypeVar
from turbo_c2.turbo_events.operators.event_expression import EventExpression
from turbo_c2.jobs.dynamic_job.dynamic_job import DynamicJob


T = TypeVar("T", bound=EventExpression)


# FIXME: implement this
class RemoteDynamicHandler(DynamicJob):
    pass
