"""Plugins package - Pyrogram will load modules from here.
This package contains a wrapper module that imports all submodules
from the `Maker` and `KERO` packages so their handlers register
without Pyrogram scanning the whole repository.
"""

__all__ = ["load_both"]
