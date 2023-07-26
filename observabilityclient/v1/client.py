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

import keystoneauth1.session

from observabilityclient.prometheus_client import PrometheusAPIClient
from observabilityclient.v1 import python_api
import prometheus_api_client


class Client(object):
    """Client for the observabilityclient api
    """

    def __init__(self, session=None, adapter_options=None,
                 session_options=None):
        """Initialize a new client for the Observabilityclient v1 API."""
        session_options = session_options or {}
        adapter_options = adapter_options or {}

        adapter_options.setdefault('service_type', "metric")

        if session is None:
            session = keystoneauth1.session.Session(**session_options)
        else:
            if session_options:
                raise ValueError("session and session_options are exclusive")

        self.session = session

        # TODO: delete the prometheus_api_client
        # TODO: figure out where to get the prometheus url.
        #       Maybe as a param to this method?
        self.prometheus_client = prometheus_api_client.PrometheusConnect(
                url="http://127.0.0.1:9090", disable_ssl=True)
        self.new_prometheus_client = PrometheusAPIClient("127.0.0.1:9090")

        self.query = python_api.QueryManager(self)
        try:
            self.project_id = self.session.get_project_id()
            self.default_labels = {
                    "project": self.project_id
                    }
        except:
            # TODO: Warning
            self.project_id = None
            self.default_labels = {
                    "project": "no-project"
                    }
            print("No project")
