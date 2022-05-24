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

import argparse
import jinja2
import os
import yaml

from osc_lib.command import command
from osc_lib.i18n import _

from observabilityclient.utils import runner
from observabilityclient.utils import shell


OBSLIBDIR = shell.file_check('/usr/share/osp-observability', 'directory')
OBSWRKDIR = shell.file_check('/var/lib/osp-observability', 'directory')
OBSTMPDIR = shell.file_check(os.path.join(OBSWRKDIR, 'tmp'), 'directory')


_j2env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(OBSLIBDIR, 'playbooks')),
    variable_start_string='{!', variable_end_string='!}'
)


class ObservabilityBaseCommand(command.Command):
    """Base class for observability commands."""

    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=prog_name,
            add_help=False
        )
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
        parser.add_argument(
            '--workdir',
            default=OBSWRKDIR,
            help=_("Working directory for observability commands.")
        )
        parser.add_argument(
            '--moduledir',
            default=None,
            help=_("Directory with additional Ansible modules.")
        )
        parser.add_argument(
            '--ssh-user',
            default='heat-admin',
            help=_("Username to be used for SSH connection.")
        )
        parser.add_argument(
            '--ssh-key',
            default='/home/stack/.ssh/id_rsa',
            help=_("SSH private key to be used for SSH connection.")
        )
        parser.add_argument(
            '--ansible-cfg',
            default=os.path.join(OBSWRKDIR, 'ansible.cfg'),
            help=_("Path to Ansible configuration.")
        )
        parser.add_argument(
            '--config',
            default=None,
            help=_("Path to playbook configuration file.")
        )
        return parser

    def _run_playbook(self, playbook, inventory, parsed_args):
        """Run Ansible raw playbook"""
        # prepare playbook template parameters and playbook content
        if parsed_args.config:
            with open(parsed_args.config, 'r') as paramfile:
                params = yaml.safe_load(paramfile)
        else:
            params = dict()
        template = _j2env.get_template("%s.j2" % playbook)
        content = template.render(workdir=OBSWRKDIR, **params)
        # create playbook file temporarily and execute it
        rnr = runner.AnsibleRunner(parsed_args.workdir,
                                   moduledir=parsed_args.moduledir,
                                   ssh_user=parsed_args.ssh_user,
                                   ssh_key=parsed_args.ssh_key,
                                   ansible_cfg=parsed_args.ansible_cfg)
        with shell.tempdir(OBSTMPDIR, prefix=os.path.splitext(playbook)[0],
                           clear=not parsed_args.messy) as tmpdir:
            playbook = os.path.join(tmpdir, playbook)
            with open(playbook, 'w') as playfile:
                playfile.write(content)
            if parsed_args.messy:
                print("Running playbook %s" % playbook)
            rnr.run(playbook, inventory, debug=parsed_args.dev)
            rnr.destroy(clear=not parsed_args.messy)

    def _execute(self, command, parsed_args):
        """Execute local command"""
        with shell.tempdir(OBSTMPDIR, prefix='exec',
                           clear=not parsed_args.messy) as tmpdir:
            rc, out, err = shell.execute(command, workdir=tmpdir,
                                         can_fail=parsed_args.dev,
                                         use_shell=True)
        return rc, out, err
