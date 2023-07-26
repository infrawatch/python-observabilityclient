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

import requests

class PrometheusAPIClientError(Exception):
    def __init__(self, response):
        self.resp = response

    def __repr__(self) -> str:
        if resp.status_code != requests.codes.ok:
            return f'[{self.resp.status_code}] {self.resp.reason}'
        else:
            decoded = self.resp.json()
            return f'[{decoded.status}]'


class PrometheusMetric:
    def __init__(self, input):
        self.timestamp = input['value'][0]
        self.labels = input['metric']
        self.value = input['value'][1]


class PrometheusRBAC:
    # TODO(mmagr): this class will be responsible for attaching Keystone
    #              tenant info to prometheus queries
    def __init__(self, rbac):
        """TODO"""

    def enrich_query(self, query):
        # TODO
        return query


class PrometheusAPIClient:
    def __init__(self, host, rbac=None):
        self._host = host
        self._rbac = PrometheusRBAC(rbac)
        self._session = requests.Session()
        self._session.verify = False

    def set_ca_cert(self, ca_cert):
        self._session.verify = ca_cert

    def set_client_cert(self, client_cert, client_key):
        self._session.cert = client_cert
        self._session.key = client_key

    def set_basic_auth(self, auth_user, auth_password):
        self._session.auth = (auth_user, auth_password)

    def get(self, query):
        url = (f"{'https' if self._session.verify else 'http'}://"
               f"{self._host}/api/v1/query")
        q = self._rbac.enrich_query(query)
        resp = self._session.get(url, params=dict(query=q),
                                 headers={'Accept': 'application/json'})
        if resp.status_code != requests.codes.ok:
            raise PrometheusAPIClientError(resp)
        decoded = resp.json()
        if decoded['status'] != 'success':
            raise PrometheusAPIClientError(resp)

        if decoded['data']['resultType'] == 'vector':
            result = [PrometheusMetric(i) for i in decoded['data']['result']]
        else:
            result = [PrometheusMetric(decoded)]
        return result
