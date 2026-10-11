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

import os

__version__ = '0.4.2'


def _awscli_data_dir():
    """Gets the data dir that awscli (v1) adds to AWS_DATA_PATH on import."""
    try:
        import awscli
    except ImportError:
        return None
    return os.path.join(os.path.dirname(os.path.abspath(awscli.__file__)),
                        'data')


def aws_env():
    """Gets the environment for running aws commands.

    Importing awscli (v1), which saws uses for completion, appends its own
    data dir to AWS_DATA_PATH. The aws commands saws runs may be AWS CLI v2,
    which fails on v1's data files with "'Namespace' object has no attribute
    'cli_binary_format'" (upstream #119), so that entry is removed. Any
    AWS_DATA_PATH entries the user set are kept.

    Args:
        * None.

    Returns:
        A copy of os.environ without awscli's data dir in AWS_DATA_PATH.
    """
    env = dict(os.environ)
    awscli_data_dir = _awscli_data_dir()
    paths = [path for path in env.pop('AWS_DATA_PATH', '').split(os.pathsep)
             if path and os.path.abspath(path) != awscli_data_dir]
    if paths:
        env['AWS_DATA_PATH'] = os.pathsep.join(paths)
    return env
