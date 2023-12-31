#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module holds utilities used by other modules.
"""

import os
import string
import asyncio
import logging
from pathlib import Path
from typing import Set, List

# **********
# Sets up logger
logger = logging.getLogger(__name__)

# **********
def available_drive_letters() -> Set[str]:
    """Fetches a set of available drive letters for the system.

    Returns:
        Set[str]: Set of available drive letters.
    """
    logger.info("Fetching available drive letters.")
    return {letter for letter in string.ascii_uppercase if not os.path.exists(letter + ":\\")}


def is_mounted(path: Path) -> bool:
    """Checks if a path is exists and is a mount for a file system.

    Args:
        path (Path): Path to check.

    Returns:
        bool: Whether the path is mounted.
    """
    logger.info(f"Checking if path is mounted: {path}")
    return os.path.ismount(path) and path.exists()


async def run_command(command: List[str], print_output: bool = True) -> None:
    """Runs a command in an asynchronous subprocess.

    Args:
        command (List[str]): Command represented as a list of arguments.
        print_output (bool, optional): Whether to print the output of the command. Defaults to True.
    """
    # Create the subprocess, redirect the standard output into a pipe
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,  # Capture stdout
        stderr=asyncio.subprocess.PIPE   # Capture stderr, if needed
    )

    stdout, stderr = await process.communicate()  # Read from stdout and stderr
    
    if process.returncode != 0:
        raise RuntimeError(f"Command failed: {command}\n{stderr.decode()}")

    # Decode and print the stdout and stderr
    if print_output:
        print(stdout.decode())
        print(stderr.decode())


# **********
if __name__ == "__main__":
    pass
