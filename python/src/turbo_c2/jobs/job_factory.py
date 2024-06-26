import abc

from turbo_c2.jobs.job_constructor import JobConstructor


class JobFactory(abc.ABC):
    def get_job_constructor(self) -> JobConstructor:
        raise NotImplementedError()
