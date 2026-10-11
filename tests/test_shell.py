# -*- coding: utf-8 -*-

# Copyright 2015 Donne Martin. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from __future__ import unicode_literals
from __future__ import print_function
import mock
import unittest
from saws.saws import shell_executable


class ShellExecutableTest(unittest.TestCase):

    @mock.patch('saws.saws.os')
    def test_posix_uses_user_shell(self, mock_os):
        mock_os.name = 'posix'
        mock_os.getenv.return_value = '/bin/bash'
        assert shell_executable() == '/bin/bash'

    @mock.patch('saws.saws.os')
    def test_posix_without_shell_uses_default(self, mock_os):
        mock_os.name = 'posix'
        mock_os.getenv.return_value = ''
        assert shell_executable() is None

    @mock.patch('saws.saws.os')
    def test_windows_uses_default(self, mock_os):
        mock_os.name = 'nt'
        mock_os.getenv.return_value = 'C:\\tools\\bash.exe'
        assert shell_executable() is None
