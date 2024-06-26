from enum import Enum


class RemoteJobReplicaMode(Enum):
    MANUAL_SETTING = "manual_setting"
    FOLLOW_QUEUE = "follow_queue"
