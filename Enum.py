from enum import Enum

class StatusEnum(str, Enum):
    enabled = "enabled"
    disabled = "disabled"

class ContactEnum(str, Enum):
    primary = "primary"
    secondary = "secondary"
