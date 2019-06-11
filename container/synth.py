# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script is used to synthesize generated parts of this library."""
import synthtool as s
from synthtool import gcp

gapic = gcp.GAPICGenerator()
common = gcp.CommonTemplates()

service = 'container'
versions = ['v1', 'v1beta1']
config_pattern = '/google/container/artman_container_{version}.yaml'

# ----------------------------------------------------------------------------
# Generate container GAPIC layer
# ----------------------------------------------------------------------------
for version in versions:
    library = gapic.py_library(
        service,
        version,
        config_path=config_pattern.format(version=version),
        artman_output_name=f'{service}-{version}',
        include_protos=True,
    )

    s.move(library / f'google/cloud/{service}_{version}')
    s.move(library / f'tests/unit/gapic/{version}')

    # Issues exist where python files should define the source encoding
    # https://github.com/googleapis/gapic-generator/issues/2097
    s.replace(
        "google/**/proto/*_pb2.py",
        r"(^.*$\n)*",
        r"# -*- coding: utf-8 -*-\n\g<0>")


    # Workaround https://github.com/googleapis/gapic-generator/issues/2449
    s.replace(
        f'google/cloud/{service}_{version}/proto/cluster_service_pb2.py',
        r"nodePool>\n",
        r"nodePool>`__\n",
    )
    s.replace(
        f'google/cloud/{service}_{version}/proto/cluster_service_pb2.py',
        r"(\s+)`__ instead",
        r"\g<1>instead",
    )

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(unit_cov_level=76, cov_level=77)
s.move(templated_files)

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
