# Roundabout way
from . import client, exceptions, utils

try:
    import importlib.metadata as impmd
except (ModuleNotFoundError, ImportError):
    # If we can't import importlib.metadata (because we're in an older version 
    # of python), try importlib_metadata (the backport)
    try:
        import importlib_metadata as impmd
    except (ModuleNotFoundError, ImportError):
        # In this case, we can't determine the version
        impmd = None
        
try:
    __version__ = impmd.version("atlasapiclient")
except Exception:
    __version__ = "unknown"


