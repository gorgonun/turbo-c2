from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from turbo_c2.helpers.date_time import DateTime


@dataclass
class LoggerInfo:
    name: str
    level: int


class Level(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3
    DEBUG = 4


class TurboLogger:
    global_level = Level.INFO
    loggers: dict[str, LoggerInfo] = {}

    def __init__(self, name: str, level: Level | None = None) -> None:
        self.name = name
        self.level = level or self.global_level
        if name in self.loggers:
            self.level = Level(self.loggers[name].level)
        else:
            self.loggers[name] = LoggerInfo(name, self.level)
    
    def info(self, message: str, *args) -> None:
        if self.level.value >= Level.INFO.value:
            self.__print(Level.INFO, message, *args)

    def warning(self, message: str, *args) -> None:
        if self.level.value >= Level.WARNING.value:
            self.__print(Level.WARNING, message, *args)

    def error(self, message: str, *args) -> None:
        if self.level.value >= Level.ERROR.value:
            self.__print(Level.ERROR, message, *args)

    def critical(self, message: str, *args) -> None:
        if self.level.value >= Level.CRITICAL.value:
            self.__print(Level.CRITICAL, message, *args)

    def debug(self, message: str, *args) -> None:
        if self.level.value >= Level.DEBUG.value:
            self.__print(Level.DEBUG, message, *args)

    def __print(self, level: Level, message: str, *args) -> None:
        print(f"{level.name} {DateTime.now()} [{self.name}] {message}", *args)

    @classmethod
    def get_logger(cls, name: str, level: Level | None = None) -> TurboLogger:
        if name not in cls.loggers:
            cls.loggers[name] = TurboLogger(name, level)
        return cls.loggers[name]
    
    @classmethod
    def set_level(cls, name: str, level: Level) -> None:
        if name not in cls.loggers:
            cls.loggers[name] = TurboLogger(name, level)
        cls.loggers[name].level = level

    @classmethod
    def set_all_levels(cls, level: Level) -> None:
        for logger in cls.loggers.values():
            logger.level = level
        cls.global_level = level
