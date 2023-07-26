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
from observabilityclient.utils.metric_utils import format_labels


class QueryManager(base.Manager):
    def list(self):
        return self.prom.all_metrics()

    def show(self, name):
        return self.prom.get_current_metric_value(metric_name=name)

    def query(self, query):
        """Query prometheus

        :param query: A query sent to prometheus
        :type query: str
        """
        # TODO: support custom labels in query
        query += format_labels(self.client.default_labels)
        return self.new_prom.get(query)
