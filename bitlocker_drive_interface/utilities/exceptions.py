#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains custom exceptions for the package.
"""

# **********
class AlreadyLockedError(Exception):
    """Raised when a container, file system, or drive is already locked."""
    pass


class AlreadyUnlockedError(Exception):
    """Raised when a container, file system, or drive is already unlocked."""
    pass


# **********
if __name__ == "__main__":
    pass
