from contextvars import ContextVar
from typing import Generic, TypeVar 

T = TypeVar("T")

class HiddenValue:
    pass 

_default = HiddenValue()

class RecyclableContextVar(Generic[T]):
    """ 
    RecyclableContextVar is a wrapper around ContextVar
    It's safe to use in gunicorn with thread recycling, but features like `reset` are not available for now

    NOTE: you need to call `increment_thread_recycles` before requests
    """

    
