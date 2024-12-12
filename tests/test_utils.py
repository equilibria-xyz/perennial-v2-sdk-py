from functools import wraps
from time import time
import logging
import inspect


# Setup for the function tracker logger
timer_logger = logging.getLogger("FunctionTimer")

# File handler to write log messages to a file
timer_tracker_handler = logging.FileHandler('functionTimer.log')
timer_tracker_handler.setLevel(logging.INFO)
timer_tracker_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
timer_tracker_handler.setFormatter(timer_tracker_formatter)

# Add the file handler to the logger
timer_logger.addHandler(timer_tracker_handler)
timer_logger.setLevel(logging.INFO)

def time_function_call(func):
    """
    A decorator to log the cost time of function calls, making it track the slow part of the program
    including the file name where the function is defined.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        module = inspect.getmodule(func)
        if module is not None and hasattr(module, '__file__'):
            file_name = module.__file__
            # Extract just the file name from the path for brevity
            file_name = file_name.split('/')[-1]
        else:
            file_name = 'Unknown'

        _time = time()
        result = func(*args, **kwargs)
        cost_time = time() - _time
        timer_logger.info("{func_name} in {file_name} : Time cost: {cost_time:.3f}s".format(func_name=func.__name__, file_name=file_name, cost_time=cost_time))
        return result
    return wrapper