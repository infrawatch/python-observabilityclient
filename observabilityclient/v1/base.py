#   Copyright 2022 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import os
import shutil

from osc_lib.command import command
from osc_lib.i18n import _

from observabilityclient.utils import shell


OBSLIBDIR = shell.file_check('/usr/share/osp-observability', 'directory')
OBSWRKDIR = shell.file_check(
    os.path.expanduser('~/.osp-observability'), 'directory'
)


class ObservabilityBaseCommand(command.Command):
    """Base class for observability commands."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--dev',
            action='store_true',
            help=_("Enable development output.")
        )
        parser.add_argument(
            '--messy',
            action='store_true',
            help=_("Disable cleanup of temporary files.")
        )
        return parser
