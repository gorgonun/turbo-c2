from enum import Enum


class NodeRepresentation(str, Enum):
    ACTION = "ACTION"
    DECISION = "DECISION"
    GROUP = "GROUP"
