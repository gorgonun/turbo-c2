from turbo_c2.globals.scheduler_globals import SchedulerGlobals



class DefaultSchedulerGlobals(SchedulerGlobals):
    pass


scheduler_globals_object = None
scheduler_globals = None

def get_scheduler_globals_object():
    global scheduler_globals_object
    if scheduler_globals_object is None:
        scheduler_globals_object = DefaultSchedulerGlobals

    return scheduler_globals_object


def get_scheduler_globals():
    global scheduler_globals
    if scheduler_globals is None:
        scheduler_globals = get_scheduler_globals_object()()

    return scheduler_globals
