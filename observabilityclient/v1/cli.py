#   Copyright 2023 Red Hat, Inc.
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

from observabilityclient.v1 import base
from observabilityclient.utils import metric_utils

from cliff import lister


class List(base.ObservabilityBaseCommand, lister.Lister):
    """Query prometheus for list of all metrics"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = metric_utils.get_client(self)
        metrics = client.query.list()
        return ["metric_name"], [[m] for m in metrics]


class Show(base.ObservabilityBaseCommand, lister.Lister):
    """Query prometheus for the current value of metric"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
                'name',
                )
        return parser

    def take_action(self, parsed_args):
        client = metric_utils.get_client(self)
        metric = client.query.show(parsed_args.name)
        return metric_utils.metrics2cols_old(metric)


class Query(base.ObservabilityBaseCommand, lister.Lister):
    """Query prometheus for the current value of metrics"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
                'query'
                )
        return parser

    def take_action(self, parsed_args):
        client = metric_utils.get_client(self)
        metric = client.query.query(parsed_args.query)
        ret = metric_utils.metrics2cols(metric)
        return ret
