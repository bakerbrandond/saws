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
import unittest
import saws
from saws.resource.resource import Resource
from saws.saws import Saws


class AwsEnvTest(unittest.TestCase):
    """Importing awscli v1 adds its data dir to AWS_DATA_PATH. Commands must
    not inherit it, or AWS CLI v2 fails with "'Namespace' object has no
    attribute 'cli_binary_format'" (upstream #119)."""

    def test_awscli_import_pollutes_environ(self):
        # Precondition for the fix: awscli (imported via saws.saws) did set it.
        assert 'awscli' in os.environ.get('AWS_DATA_PATH', '')

    def test_env_drops_awscli_data_path(self):
        with mock.patch.dict(os.environ,
                             {'AWS_DATA_PATH': saws._awscli_data_dir()}):
            assert 'AWS_DATA_PATH' not in saws.aws_env()

    def test_env_drops_empty_and_normalized_entries(self):
        awscli_dir = saws._awscli_data_dir()
        polluted = os.pathsep.join(['', awscli_dir + os.sep, ''])
        with mock.patch.dict(os.environ, {'AWS_DATA_PATH': polluted}):
            assert 'AWS_DATA_PATH' not in saws.aws_env()

    def test_env_without_awscli_keeps_all_entries(self):
        user_paths = os.pathsep.join(['/a', '/b'])
        with mock.patch('saws._awscli_data_dir', return_value=None), \
                mock.patch.dict(os.environ, {'AWS_DATA_PATH': user_paths}):
            assert saws.aws_env()['AWS_DATA_PATH'] == user_paths

    def test_env_keeps_user_data_path(self):
        polluted = os.pathsep.join(['/my/models', saws._awscli_data_dir()])
        with mock.patch.dict(os.environ, {'AWS_DATA_PATH': polluted}):
            assert saws.aws_env()['AWS_DATA_PATH'] == '/my/models'

    def test_env_leaves_process_environ_untouched(self):
        # Value: protects=aws_env() returns a copy and leaves os.environ (which
        # the in-process awscli v1 completer reads) unchanged; fails_when=the
        # dict(os.environ) copy is dropped so env.pop('AWS_DATA_PATH') unsets
        # it for the whole process; why_new=the precondition test only checks
        # os.environ before aws_env() is ever called in this class;
        # seam=none; no_claim=does not prove completion still works end to end.
        polluted = os.pathsep.join(['/my/models', saws._awscli_data_dir()])
        with mock.patch.dict(os.environ, {'AWS_DATA_PATH': polluted}):
            saws.aws_env()
            assert os.environ['AWS_DATA_PATH'] == polluted

    def test_env_keeps_everything_else(self):
        with mock.patch.dict(os.environ, {'AWS_PROFILE': 'dev'}):
            assert saws.aws_env()['AWS_PROFILE'] == 'dev'

    @mock.patch('saws.saws.subprocess')
    def test_typed_commands_use_clean_env(self, mock_subprocess):
        s = Saws.__new__(Saws)
        s.shell = None
        s._handle_cd = mock.Mock(return_value=False)
        s._colorize_output = lambda text: text
        s.completer = mock.Mock(replace_shortcut=lambda text: text)
        s.handle_docs = mock.Mock(return_value=False)
        s._process_command('aws iam get-credential-report')
        env = mock_subprocess.call.call_args[1]['env']
        assert 'awscli' not in env.get('AWS_DATA_PATH', '')

    @mock.patch('saws.resource.resource.subprocess')
    def test_resource_queries_use_clean_env(self, mock_subprocess):
        Resource._query_aws(mock.Mock(), 'aws s3 ls')
        env = mock_subprocess.check_output.call_args[1]['env']
        assert 'awscli' not in env.get('AWS_DATA_PATH', '')
