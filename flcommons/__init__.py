"""Public community SDK name; the existing Client import remains compatible."""
from fl_commons.sdk import Client as FLStudio, APIError

__all__ = ["FLStudio", "APIError"]
