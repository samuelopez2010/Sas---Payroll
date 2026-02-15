
import threading

_thread_locals = threading.local()

def set_current_company(company):
    """Sets the company for the current thread."""
    _thread_locals.company = company

def get_current_company():
    """Gets the company for the current thread."""
    return getattr(_thread_locals, 'company', None)

def remove_current_company():
    """Removes the company for the current thread."""
    if hasattr(_thread_locals, 'company'):
        del _thread_locals.company
