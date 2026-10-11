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
import os
import shutil
import tempfile


def use_temp_resources_file(test, resources, data_file):
    """Points resources at a temporary copy of a saws/data file.

    Resources write their cache back to resources_path, so tests must not
    point it at a checked-in fixture.

    Args:
        * test: The unittest.TestCase, used to register cleanup.
        * resources: An instance of saws.resources.AwsResources.
        * data_file: A file name in saws/data, or None for an empty file.

    Returns:
        None.
    """
    tmp_dir = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, tmp_dir)
    path = os.path.join(tmp_dir, 'resources.txt')
    if data_file is not None:
        resources._set_resources_path(os.path.join('data', data_file))
        shutil.copy(resources.resources_path, path)
    resources.resources_path = path
