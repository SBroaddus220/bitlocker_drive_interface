#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" 
Test cases for the bitlocker drive class.
"""

import asyncio
from pathlib import Path

import unittest
from unittest import mock
from unittest.mock import MagicMock, PropertyMock, AsyncMock

from bitlocker_drive_interface.bitlocker_drive import BitlockerDrive
from bitlocker_drive_interface.utilities.exceptions import AlreadyLockedError, AlreadyUnlockedError


# ****************
class TestBitlockerDrive(unittest.TestCase):
    
    # ****************
    def setUp(self):
        
        # Mocks the Powershell executable
        self.POWERSHELL_EXECUTABLE_PATH = MagicMock(spec=Path)
        type(self.POWERSHELL_EXECUTABLE_PATH).stat = PropertyMock(return_value=MagicMock(st_mode=0o700))
        
        # Generic drive instance
        mount_path = Path('/fake/mount')
        self.password = "decoded password"
        self.bitlocker_drive = BitlockerDrive(
            powershell_executable_path = self.POWERSHELL_EXECUTABLE_PATH,
            mount_point = mount_path, 
        )
        
    
    # ****************
    # Prepare unlock subprocess tests
    def test_prepare_unlock_subprocess_command_setup(self):
        # Arrange
        expected_command = [
            str(self.bitlocker_drive.powershell_executable_path),
            "-Command",
            f'$securePassword = ConvertTo-SecureString -String "{self.password}" -AsPlainText -Force; \
                Unlock-BitLocker -MountPoint "{self.bitlocker_drive.mount_point}" -Password $securePassword'
        ]

        with mock.patch('builtins.open', mock.mock_open(read_data="ZGVjb2RlZCBwYXNzd29yZA=="), create=True) as m, \
            mock.patch('asyncio.create_subprocess_exec', new=mock.MagicMock()) as mock_subprocess, \
            mock.patch('os.path.ismount', return_value=True):
            # Act
            command = self.bitlocker_drive.prepare_unlock_subprocess(self.password)

            # Assert
            self.assertEqual(command, expected_command)


    def test_prepare_unlock_subprocess_command_setup_different_password(self):
        # Arrange
        incorrect_password = "incorrect password"
        expected_command = [
            str(self.bitlocker_drive.powershell_executable_path),
            "-Command",
            f'$securePassword = ConvertTo-SecureString -String "{self.password}" -AsPlainText -Force; \
                Unlock-BitLocker -MountPoint "{self.bitlocker_drive.mount_point}" -Password $securePassword'
        ]

        with mock.patch('builtins.open', mock.mock_open(read_data="ZGVjb2RlZCBwYXNzd29yZA=="), create=True) as m, \
            mock.patch('asyncio.create_subprocess_exec', new=mock.MagicMock()) as mock_subprocess, \
            mock.patch('os.path.ismount', return_value=True):
            # Act
            command = self.bitlocker_drive.prepare_unlock_subprocess(incorrect_password)

            # Assert
            self.assertNotEqual(command, expected_command)
                
                
    def test_prepare_unlock_subprocess_no_mount_point(self):
        # Arrange
        with mock.patch('os.path.ismount', return_value=False):
            # Act
            with self.assertRaises(FileNotFoundError):
                self.bitlocker_drive.prepare_unlock_subprocess(self.password)
                
                
    def test_prepare_unlock_subprocess_already_unlocked(self):
        # Arrange
        with mock.patch('os.path.ismount', return_value=True), \
            mock.patch('pathlib.Path.exists', return_value=True):
            # Act
            with self.assertRaises(AlreadyUnlockedError):
                self.bitlocker_drive.prepare_unlock_subprocess(self.password)
    
    
    
    # ****************
    # Unlock tests
    def test_unlock_method(self):
        # Arrange
        with mock.patch("bitlocker_drive_interface.utilities.utilities.run_command", return_value=None) as mock_run_command, \
            mock.patch('os.path.ismount', return_value=True), \
            mock.patch('builtins.open', mock.mock_open(read_data="ZGVjb2RlZCBwYXNzd29yZA=="), create=True):
            # Act
            asyncio.run(self.bitlocker_drive.unlock(self.password, print_output=False))  # Not interested in print_output in the test case
            
            # Assert
            mock_run_command.assert_called_once()
    
    
    def test_unlock_method_prepares_subprocess(self):
        # Arrange
        mock_subprocess_command = mock.MagicMock()
        mock_subprocess_command.__iter__.return_value = iter([])  # Mocks iterable property of command

        # Manually sets the attribute to the required value to simulate prepare sync subprocess call
        def side_effect(password):
            self.bitlocker_drive.subprocess_unlock_command = mock_subprocess_command
            return mock_subprocess_command

        with mock.patch("bitlocker_drive_interface.utilities.utilities.run_command", return_value=None) as mock_run_command, \
            mock.patch('pathlib.Path.exists', return_value=True), \
            mock.patch.object(BitlockerDrive, 'prepare_unlock_subprocess', side_effect=side_effect) as mock_prepare_unlock_subprocess:

            # Act
            asyncio.run(self.bitlocker_drive.unlock(self.password))

            # Assert
            mock_prepare_unlock_subprocess.assert_called_once()
            mock_run_command.assert_called_once()

    
    # ****************
    # Prepare lock subprocess tests
    def test_prepare_lock_subprocess_command_setup(self):
        # Arrange
        expected_command = [
            str(self.bitlocker_drive.powershell_executable_path),
            "-Command",
            f'Lock-BitLocker -MountPoint "{self.bitlocker_drive.mount_point}" -ForceDismount'
        ]

        with mock.patch('asyncio.create_subprocess_exec', new=mock.MagicMock()) as mock_subprocess, \
            mock.patch('pathlib.Path.exists', return_value=True), \
            mock.patch('os.path.ismount', return_value=True):
            # Act
            command = self.bitlocker_drive.prepare_lock_subprocess()

            # Assert
            self.assertEqual(command, expected_command)
            
    
    def test_prepare_lock_subprocess_no_mount_point(self):
        # Arrange
        with mock.patch('os.path.ismount', return_value=False):
            # Act
            with self.assertRaises(FileNotFoundError):
                self.bitlocker_drive.prepare_lock_subprocess()
                
                
    def test_prepare_lock_subprocess_already_locked(self):
        # Arrange
        with mock.patch('pathlib.Path.exists', return_value=False), \
            mock.patch('os.path.ismount', return_value=True):
            # Act
            with self.assertRaises(AlreadyLockedError):
                self.bitlocker_drive.prepare_lock_subprocess()
    

    def test_lock_method_prepares_subprocess(self):
        # Arrange
        mock_subprocess_command = mock.MagicMock()
        mock_subprocess_command.__iter__.return_value = iter([])  # Mocks iterable property of command

        # Manually sets the attribute to the required value to simulate prepare sync subprocess call
        def side_effect():
            self.bitlocker_drive.subprocess_lock_command = mock_subprocess_command
            return mock_subprocess_command

        with mock.patch("bitlocker_drive_interface.utilities.utilities.run_command", return_value=None) as mock_run_command, \
            mock.patch('pathlib.Path.exists', return_value=True), \
            mock.patch.object(BitlockerDrive, 'prepare_lock_subprocess', side_effect=side_effect) as mock_prepare_lock_subprocess:

            # Act
            asyncio.run(self.bitlocker_drive.lock())

            # Assert
            mock_prepare_lock_subprocess.assert_called_once()
            mock_run_command.assert_called_once()
    
    
    # ****************
    # Lock tests
    def test_lock_method(self):
        # Arrange
        with mock.patch("bitlocker_drive_interface.utilities.utilities.run_command", return_value=None) as mock_run_command, \
            mock.patch('pathlib.Path.exists', return_value=True), \
            mock.patch('os.path.ismount', return_value=True), \
            mock.patch('builtins.open', mock.mock_open(read_data="ZGVjb2RlZCBwYXNzd29yZA=="), create=True):
            # Act
            asyncio.run(self.bitlocker_drive.lock(print_output=False))  # Not interested in print_output in the test case
            
            # Assert
            mock_run_command.assert_called_once()
    
    
# ****************
if __name__ == '__main__':
    unittest.main()
