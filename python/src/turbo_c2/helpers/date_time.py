import datetime


class DateTime():
    datetime_provider = datetime.datetime

    @classmethod
    def now(cls):
        return cls.datetime_provider.now()
