from enum import Enum


class EdgeRepresentation(str, Enum):
    QUEUE = "QUEUE"
    EXECUTION = "EXECUTION"
    CONDITION_TRUE = "CONDITION_TRUE"
    CONDITION_FALSE = "CONDITION_FALSE"
