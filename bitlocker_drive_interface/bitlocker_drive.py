#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the BitlockerDrive class, which is used to unlock and lock Bitlocker drives.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List

from bitlocker_drive_interface.utilities import utilities
from bitlocker_drive_interface.utilities.exceptions import (AlreadyLockedError, AlreadyUnlockedError)


# **********
# Sets up logger
logger = logging.getLogger(__name__)


# **********
class BitlockerDrive:
    """Represents a Bitlocker drive that can be unlocked or locked."""
    
    def __init__(self, powershell_executable_path: Path, mount_point: Path) -> None:
        """Instantiates a new BitlockerDrive object.

        Args:
            powershell_executable_path (Path): Path to the PowerShell executable.
            mount_point (Path): Path to the mount point of the Bitlocker drive
        """
        self.powershell_executable_path = powershell_executable_path
        self.mount_point = mount_point
        
        #: Command to unlock the Bitlocker drive.
        self.subprocess_unlock_command: Optional[List[str]] = None
        
        #: Command to lock the Bitlocker drive.
        self.subprocess_lock_command: Optional[List[str]] = None
    
    
    def prepare_unlock_subprocess(self, password: str) -> List[str]:
        """Prepares the command to unlock the Bitlocker drive.
        
        Args:
            password (str): Password to unlock the Bitlocker drive.

        Raises:
            FileNotFoundError: If the password file for the Bitlocker drive is not found.

        Returns:
            List[str]: Command to unlock the Bitlocker drive.
        """
        if not os.path.ismount(self.mount_point):
            raise FileNotFoundError(f"Mount point at {self.mount_point} not found.")
        if utilities.is_mounted(self.mount_point):
            raise AlreadyUnlockedError(f"Mount point at {self.mount_point} is already mounted.")
        
        logger.info(f"Preparing to unlock Bitlocker drive at {self.mount_point}")
        
        # Command to convert password to secure string and unlock drive
        command = [
            f"{self.powershell_executable_path}",
            "-Command",
            f'$securePassword = ConvertTo-SecureString -String "{password}" -AsPlainText -Force; \
                Unlock-BitLocker -MountPoint "{self.mount_point}" -Password $securePassword'
        ]
        
        self.subprocess_unlock_command = command
        
        return self.subprocess_unlock_command
    
    
    async def unlock(self, password: str, print_output: bool = True) -> None:
        """Unlocks the Bitlocker drive.

        Args:
            print_output (bool, optional): Whether to print the output to the console. Defaults to True.
        """
        self.prepare_unlock_subprocess(password)
        logger.info(f"Unlocking Bitlocker drive at {self.mount_point}")
        try:
            await utilities.run_command(self.subprocess_unlock_command, print_output=print_output)
        except RuntimeError as e:
            logger.error(f"Error running unlock command: {str(e)}")
    
    
    def prepare_lock_subprocess(self) -> List[str]:
        """Prepares the command to lock the Bitlocker drive.

        Raises:
            FileNotFoundError: If the Bitlocker drive is not mounted.

        Returns:
            List[str]: Command to lock the Bitlocker drive.
        """
        if not os.path.ismount(self.mount_point):
            raise FileNotFoundError(f"Mount point at {self.mount_point} not found.")
        if not utilities.is_mounted(self.mount_point):
            raise AlreadyLockedError(f"Mount point at {self.mount_point} is already dismounted")
        
        logger.info(f"Preparing to lock Bitlocker drive at {self.mount_point}")
        
        # Command to lock drive
        command = [
            f"{self.powershell_executable_path}",
            "-Command",
            f'Lock-BitLocker -MountPoint "{self.mount_point}" -ForceDismount'
        ]
        
        self.subprocess_lock_command = command
        
        return self.subprocess_lock_command
    
    
    async def lock(self, print_output: bool = True) -> None:
        """Locks the Bitlocker drive.

        Args:
            print_output (bool, optional): Whether to print the output to the console. Defaults to True.
        """
        self.prepare_lock_subprocess()
        logger.info(f"Locking Bitlocker drive at {self.mount_point}")
        try:
            await utilities.run_command(self.subprocess_lock_command, print_output=print_output)
        except RuntimeError as e:
            logger.error(f"Error running lock command: {str(e)}")


# **********
if __name__ == "__main__":
    pass
