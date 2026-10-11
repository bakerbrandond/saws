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
import os
import shutil
import stat
import tempfile
import unittest
from saws.saws import Saws, shell_executable


def make_executable(directory, name):
    path = os.path.join(directory, name)
    with open(path, 'w') as f:
        f.write('#!/bin/sh\n')
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


def make_saws(shell):
    """Builds a Saws without the prompt_toolkit CLI, which needs a TTY."""
    saws = Saws.__new__(Saws)
    saws.shell = shell
    saws._handle_cd = mock.Mock(return_value=False)
    saws._colorize_output = lambda text: text
    return saws


@unittest.skipIf(os.name != 'posix', 'POSIX shells only')
class ShellExecutableTest(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir)

    def test_default_ignores_login_shell(self):
        # zsh as a login shell must not change how commands run: its NOMATCH
        # option rejects unquoted --query Reservations[*] arguments.
        with mock.patch.dict(os.environ, {'SHELL': '/usr/bin/zsh'}):
            assert shell_executable('') is None

    def test_configured_shell(self):
        bash = make_executable(self.tmp_dir, 'bash')
        assert shell_executable(bash) == bash

    def test_configured_shell_expands_user(self):
        bash = make_executable(self.tmp_dir, 'bash')
        with mock.patch.dict(os.environ, {'HOME': self.tmp_dir}):
            assert shell_executable('~/bash') == bash

    def test_bare_name_resolves_on_path(self):
        bash = make_executable(self.tmp_dir, 'mybash')
        with mock.patch.dict(os.environ, {'PATH': self.tmp_dir}):
            assert shell_executable('mybash') == bash

    def test_relative_path_resolves_once_to_absolute(self):
        # Commands may `cd` later, so a relative path must not be re-resolved
        # against whatever directory the user is in when a command runs.
        bash = make_executable(self.tmp_dir, 'mybash')
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp_dir)
        assert shell_executable(os.path.join('.', 'mybash')) == bash

    def test_missing_shell_falls_back(self):
        assert shell_executable(os.path.join(self.tmp_dir, 'nope')) is None

    def test_unknown_bare_name_falls_back(self):
        # Value: protects=a bare name not found on PATH (e.g. a typo such as
        # `shell = bsh`) falls back to /bin/sh; fails_when=the `shell is None`
        # guard after _which is dropped and os.path.abspath(None) raises
        # TypeError, crashing Saws() at startup; why_new=existing bare-name
        # test only covers a name that is found; seam=none; no_claim=does not
        # check the warning text.
        with mock.patch.dict(os.environ, {'PATH': self.tmp_dir}):
            assert shell_executable('no-such-shell') is None

    def test_directory_falls_back(self):
        # Value: protects=a directory (e.g. `shell = /bin`) is rejected;
        # fails_when=os.path.isfile is relaxed to os.path.exists, since
        # directories pass os.access(X_OK) and every command would then fail
        # to spawn; why_new=existing fallback tests use a missing path and a
        # non-executable file, neither of which is a directory; seam=none;
        # no_claim=does not cover symlinks.
        assert shell_executable(self.tmp_dir) is None

    def test_non_executable_shell_falls_back(self):
        path = os.path.join(self.tmp_dir, 'not-exec')
        open(path, 'w').close()
        assert shell_executable(path) is None

    def test_list_value_falls_back(self):
        # ConfigObj parses `shell = /bin/bash,` as a list.
        bash = make_executable(self.tmp_dir, 'bash')
        assert shell_executable([bash]) is None

    def test_windows_ignores_configured_shell(self):
        bash = make_executable(self.tmp_dir, 'bash')
        with mock.patch('saws.saws.os.name', 'nt'):
            assert shell_executable(bash) is None


class ResolveShellTest(unittest.TestCase):

    def make_saws_with_config(self, main_section):
        saws = Saws.__new__(Saws)
        saws.config = mock.Mock(MAIN='main', SHELL='shell')
        saws.config_obj = {'main': main_section}
        saws.logger = mock.Mock()
        return saws

    def test_missing_option_uses_default(self):
        # Existing ~/.sawsrc files have no `shell` key.
        saws = self.make_saws_with_config({})
        assert saws._resolve_shell() is None
        saws.logger.warning.assert_not_called()

    @unittest.skipIf(os.name != 'posix', 'POSIX shells only')
    @mock.patch('saws.saws.click')
    def test_valid_option_used_without_warning(self, mock_click):
        # Value: protects=a usable configured shell is returned and does not
        # print the "Ignoring shell" warning; fails_when=the warning condition
        # loses its `shell is None` clause and warns on every non-empty value;
        # why_new=the other _resolve_shell tests cover only missing/invalid
        # values, so a spurious warning on valid config goes unnoticed;
        # seam=none; no_claim=does not exercise ConfigObj parsing of ~/.sawsrc.
        tmp_dir = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_dir)
        bash = make_executable(tmp_dir, 'bash')
        saws = self.make_saws_with_config({'shell': bash})
        assert saws._resolve_shell() == bash
        saws.logger.warning.assert_not_called()
        mock_click.secho.assert_not_called()

    @mock.patch('saws.saws.click')
    def test_invalid_option_warns(self, mock_click):
        saws = self.make_saws_with_config({'shell': '/no/such/shell'})
        assert saws._resolve_shell() is None
        saws.logger.warning.assert_called_once()
        mock_click.secho.assert_called_once()

    @mock.patch('saws.saws.click')
    def test_empty_list_option_warns(self, mock_click):
        # `shell = ,` parses as an empty list; it must not be dropped silently.
        saws = self.make_saws_with_config({'shell': []})
        assert saws._resolve_shell() is None
        saws.logger.warning.assert_called_once()

    @mock.patch('saws.saws.click')
    def test_windows_ignores_option_without_warning(self, mock_click):
        saws = self.make_saws_with_config({'shell': 'bash'})
        with mock.patch('saws.saws.os.name', 'nt'):
            assert saws._resolve_shell() is None
        saws.logger.warning.assert_not_called()
        mock_click.secho.assert_not_called()


class ProcessCommandShellTest(unittest.TestCase):

    @mock.patch('saws.saws.subprocess')
    def test_runs_with_configured_shell(self, mock_subprocess):
        make_saws('/bin/bash')._process_command('echo hi')
        mock_subprocess.call.assert_called_with('echo hi', shell=True,
                                                executable='/bin/bash',
                                                env=mock.ANY)


@unittest.skipIf(os.name != 'posix', 'POSIX shells only')
class RealShellTest(unittest.TestCase):
    """Runs commands through real shells; the mocks above cannot catch a
    dropped executable= or shell=True."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp_dir)
        self.out = os.path.join(self.tmp_dir, 'out')

    def read_out(self):
        with open(self.out) as f:
            return f.read().strip()

    def test_default_shell_keeps_unquoted_globs(self):
        with mock.patch.dict(os.environ, {'SHELL': '/usr/bin/zsh'}):
            make_saws(None)._process_command(
                'echo --query Reservations[*].Id > %s' % self.out)
        assert self.read_out() == '--query Reservations[*].Id'

    @unittest.skipUnless(os.path.exists('/bin/bash'), 'needs bash')
    def test_configured_bash_supports_process_substitution(self):
        make_saws('/bin/bash')._process_command(
            'cat <(echo PROCSUB_OK) > %s' % self.out)
        assert self.read_out() == 'PROCSUB_OK'
