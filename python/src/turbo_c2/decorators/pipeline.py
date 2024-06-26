from typing import Callable
from turbo_c2.abstractions.pipeline import Pipeline


def pipeline():
    def wrapped(func: Callable[[Pipeline], None]):
        pipeline = Pipeline()
        func(pipeline)
        return pipeline
    return wrapped
