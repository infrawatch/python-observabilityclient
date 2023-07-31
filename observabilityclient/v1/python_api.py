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
    def list(self, disable_rbac=False):
        """Lists metric names

        :param disable_rbac: Disables rbac injection if set to True
        :type disable_rbac: boolean
        """
        if disable_rbac or self.client.rbac.disable_rbac:
            metric_names = self.prom.label_values("__name__")
            return metric_names
        else:
            match = f"{{{format_labels(self.client.rbac.default_labels)}}}"
            metrics = self.prom.series(match)
            if metrics == []:
                return []
            unique_metric_names = list(set([m['__name__'] for m in metrics]))
            return sorted(unique_metric_names)

    # TODO: What's the difference between show and query
    # TODO: Should this allow labels being specified like query below?
    def show(self, name, disable_rbac=False):
        """Shows current values for metrics of a specified name

        :param disable_rbac: Disables rbac injection if set to True
        :type disable_rbac: boolean
        """
        enriched = self.client.rbac.append_rbac(name,
                                                disable_rbac=disable_rbac)
        return self.prom.query(enriched)

    def query(self, query, labels=None, disable_rbac=False):
        """Sends a query to prometheus. Allows to specify additional labels.

        The query can be any PromQL query. The additional labels will be added
        to all metric names inside the query as well as labels for enforcing
        rbac. Having labels as part of a query is allowed.

        A call like this:
        query("sum(name1) - sum(name2{label1='value'})", {label2:'value2'})
        will result in a query string like this:
        "sum(name1{label2='value2', rbac='rbac_value'}) -
            sum(name2{label1='value', label2='value2', rbac='rbac_value'})"

        :param query: Custom query string
        :type query: str
        :param labels: Dictionary of labels to add to the query
        :type labels: dict
        :param disable_rbac: Disables rbac injection if set to True
        :type disable_rbac: boolean
        """
        query = self.client.rbac.enrich_query(query, labels, disable_rbac)
        return self.prom.query(query)

    def delete(self, matches, start=None, end=None):
        """Deletes metrics from Prometheus

        The metrics aren't deleted immediately. Do a call to clean_tombstones()
        to speed up the deletion. If start and end isn't specified, then
        minimum and maximum timestamps are used.

        :param matches: List of matches to match which metrics to delete
        :type matches: [str]
        :param start: timestamp from which to start deleting
        :type start: rfc3339 or unix_timestamp
        :param end: timestamp until which to delete
        :type end: rfc3339 or unix_timestamp
        """
        # TODO Do we want to restrict access to the admin api endpoints?
        #      We could either try to inject the project label like in
        #      query. We could also do some check right here, before
        #      it gets to prometheus.
        return self.prom.delete(matches, start, end)

    def clean_tombstones(self):
        """Instructs prometheus to clean tombstones"""
        return self.prom.clean_tombstones()

    def snapshot(self):
        "Creates a snapshot of the current data"
        return self.prom.snapshot()
