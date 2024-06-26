from turbo_c2.turbo_events.event_based_boolean_scheduler_globals import (
    EventBasedBooleanSchedulerGlobals,
)


def executor_settings():
    def wrapper(func):
        settings = func()
        EventBasedBooleanSchedulerGlobals.executor_settings = {
            **EventBasedBooleanSchedulerGlobals.executor_settings,
            **settings,
        }

    return wrapper
