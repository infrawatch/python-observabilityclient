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

from observabilityclient.utils.metric_utils import format_labels
from keystoneauth1.exceptions.auth_plugins import MissingAuthPlugin
import re


class ObservabilityRbacError(Exception):
    pass


class Rbac():
    def __init__(self, client, session, disable_rbac=False):
        self.client = client
        self.session = session
        self.disable_rbac = disable_rbac
        try:
            self.project_id = self.session.get_project_id()
            self.default_labels = {
                    "project": self.project_id
                    }
            self.rbac_init_successful = True
        except MissingAuthPlugin:
            self.project_id = None
            self.default_labels = {
                    "project": "no-project"
                    }
            self.rbac_init_successful = False

    def _enrich_labels(self, labels, disable_rbac):
        if not self.rbac_init_successful and not disable_rbac:
            raise ObservabilityRbacError("Unauthorized. Couldn't "
                                         "get project id")
        if not disable_rbac and not self.disable_rbac:
            # Include labels to enforce rbac
            if labels is not None:
                labels = {**labels, **self.default_labels}
            else:
                labels = self.default_labels
        return labels

    # TODO aren't the additional labels just making
    #      the code confusing? Are they useful?
    def enrich_query(self, query, additional_labels=None, disable_rbac=False):
        """Used to add rbac labels and additional specified labels to queries

        :param query: The query to enrich
        :type query: str
        :param additional_labels: Labels to add to the
                                  query in addition to rbac
        :type additional_labels: dict
        :param disable_rbac: Disables rbac injection if set to True
        :type disable_rbac: boolean
        """
        labels = self._enrich_labels(additional_labels, disable_rbac)
        if labels is None or labels == {}:
            return query

        metric_names = self.client.query.list(disable_rbac=disable_rbac)

        # We need to detect the locations of metric names
        # inside the query
        # NOTE the locations are the locations within the original query
        name_end_locations = []
        for name in metric_names:
            # Regex for a metric name is: [a-zA-Z_:][a-zA-Z0-9_:]*
            # We need to make sure, that "name" isn't just a part
            # of a longer word, so we try to expand it by "name_regex"
            name_regex = "[a-zA-Z_:]?[a-zA-Z0-9_:]*" + name + "[a-zA-Z0-9_:]*"
            potential_names = re.finditer(name_regex, query)
            for potential_name in potential_names:
                if potential_name.group(0) == name:
                    name_end_locations.append(potential_name.end())

        name_end_locations = sorted(name_end_locations, reverse=True)
        for name_end_location in name_end_locations:
            if (name_end_location < len(query) and
               query[name_end_location] == "{"):
                # There already are some labels
                label_section_end = query.find("}", name_end_location)
                query = (f"{query[:label_section_end]}, "
                         f"{format_labels(labels)}"
                         f"{query[label_section_end:]}")
            else:
                query = (f"{query[:name_end_location]}"
                         f"{{{format_labels(labels)}}}"
                         f"{query[name_end_location:]}")
        return query

    def append_rbac(self, query, additional_labels=None, disable_rbac=False):
        """Used to append rbac labels and additional labels to queries

        It's a simplified and faster version of enrich_query(). This just
        appends the labels at the end of the query string. For proper handling
        of complex queries, where metric names might occure elsewhere than
        just at the end, please use the enrich_query() function.

        :param query: The query to append to
        :type query: str
        :param additional_labels: Labels to add to the query
                                  in addition to rbac
        :type additional_labels: dict
        :param disable_rbac: Disables rbac injection if set to True
        :type disable_rbac: boolean
        """
        labels = self._enrich_labels(additional_labels, disable_rbac)
        if labels is None or labels == {}:
            return query
        return f"{query}{{{format_labels(labels)}}}"
