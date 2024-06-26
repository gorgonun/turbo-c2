from turbo_c2.turbo_events.event_based_boolean_scheduler_globals import (
    EventBasedBooleanSchedulerGlobals,
)


def consumer_settings():
    def wrapper(func):
        settings = func()
        EventBasedBooleanSchedulerGlobals.consumer_settings = {
            **EventBasedBooleanSchedulerGlobals.consumer_settings,
            **settings,
        }

    return wrapper
