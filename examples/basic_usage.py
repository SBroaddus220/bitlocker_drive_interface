#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script showcases how you can unlock/lock a Bitlocker drive using the BitlockerDrive class. 
Set proper values for the variables used to initialize the BITLOCKER_DRIVE instance below before running this script.
"""

import logging
import asyncio
from pathlib import Path

# Adds package to path
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from bitlocker_drive_interface.bitlocker_drive import BitlockerDrive
from bitlocker_drive_interface.utilities.exceptions import AlreadyLockedError, AlreadyUnlockedError

BITLOCKER_DRIVE = BitlockerDrive(
    powershell_executable_path = Path("path/to/powershell.exe"),
    mount_point = Path("path/to/mount/point"),
)
BITLOCKER_DRIVE_PASSWORD = "password"


# **********
# Sets up logger
logger = logging.getLogger(__name__)

PROGRAM_LOG_FILE_PATH = Path(__file__).resolve().parent.parent / "program_log.txt"

LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # Doesn't disable other loggers that might be active
    "formatters": {
        "default": {
            "format": "[%(levelname)s][%(funcName)s] | %(asctime)s | %(message)s",
        },
        "simple": {  # Used for console logging
            "format": "[%(levelname)s][%(funcName)s] | %(message)s",
        },
    },
    "handlers": {
        "logfile": {
            "class": "logging.FileHandler",  # Basic file handler
            "formatter": "default",
            "level": "INFO",
            "filename": PROGRAM_LOG_FILE_PATH.as_posix(),
            "mode": "a",
            "encoding": "utf-8",
        },
        "console_stdout": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
        "console_stderr": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "ERROR",
            "stream": "ext://sys.stderr",
        },
    },
    "root": {  # Simple program, so root logger uses all handlers
        "level": "DEBUG",
        "handlers": [
            "logfile",
            "console_stdout",
            "console_stderr",
        ]
    }
}


# **********
async def unlock_bitlocker_drive(password: str) -> None:
    """Attempts to unlock the Bitlocker drive. If the drive is already unlocked, the function will continue.
    
    Args:
        password (str): Password to unlock the Bitlocker drive.
    """
    try:
        await BITLOCKER_DRIVE.unlock(password)
    except AlreadyUnlockedError:
        logger.warning(f"Bitlocker drive at {BITLOCKER_DRIVE.mount_point} is already unlocked. Continuing...")
    
    
async def lock_bitlocker_drives() -> None:
    """Attempts to lock the Bitlocker drive. If the drive is already locked, the function will continue."""
    try:
        await BITLOCKER_DRIVE.lock()
    except AlreadyLockedError:
        logger.warning(f"Bitlocker drive at {BITLOCKER_DRIVE.mount_point} is already locked. Continuing...")

    
# **********
if __name__ == "__main__":
    import logging.config
    logging.disable(logging.DEBUG)
    logging.config.dictConfig(LOGGER_CONFIG)
    asyncio.run(unlock_bitlocker_drive(BITLOCKER_DRIVE_PASSWORD))
    