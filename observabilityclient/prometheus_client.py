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

    def __str__(self) -> str:
        if self.resp.status_code != requests.codes.ok:
            if self.resp.status_code != 204:
                decoded = self.resp.json()
                if 'error' in decoded:
                    return f'[{self.resp.status_code}] {decoded["error"]}'
            return f'[{self.resp.status_code}] {self.resp.reason}'
        else:
            decoded = self.resp.json()
            return f'[{decoded.status}]'

    def __repr__(self) -> str:
        if self.resp.status_code != requests.codes.ok:
            if self.resp.status_code != 204:
                decoded = self.resp.json()
                if 'error' in decoded:
                    return f'[{self.resp.status_code}] {decoded["error"]}'
            return f'[{self.resp.status_code}] {self.resp.reason}'
        else:
            decoded = self.resp.json()
            return f'[{decoded.status}]'


class PrometheusMetric:
    def __init__(self, input):
        self.timestamp = input['value'][0]
        self.labels = input['metric']
        self.value = input['value'][1]


class PrometheusAPIClient:
    def __init__(self, host):
        self._host = host
        self._session = requests.Session()
        self._session.verify = False

    def set_ca_cert(self, ca_cert):
        self._session.verify = ca_cert

    def set_client_cert(self, client_cert, client_key):
        self._session.cert = client_cert
        self._session.key = client_key

    def set_basic_auth(self, auth_user, auth_password):
        self._session.auth = (auth_user, auth_password)

    def _get(self, endpoint, params=None):
        url = (f"{'https' if self._session.verify else 'http'}://"
               f"{self._host}/api/v1/{endpoint}")
        resp = self._session.get(url, params=params,
                                 headers={'Accept': 'application/json'})
        if resp.status_code != requests.codes.ok:
            raise PrometheusAPIClientError(resp)
        decoded = resp.json()
        if decoded['status'] != 'success':
            raise PrometheusAPIClientError(resp)

        return decoded

    def _post(self, endpoint, params=None):
        url = (f"{'https' if self._session.verify else 'http'}://"
               f"{self._host}/api/v1/{endpoint}")
        resp = self._session.post(url, params=params,
                                  headers={'Accept': 'application/json'})
        if resp.status_code != requests.codes.ok:
            raise PrometheusAPIClientError(resp)
        decoded = resp.json()
        if 'status' in decoded and decoded['status'] != 'success':
            raise PrometheusAPIClientError(resp)
        return decoded

    def query(self, query):
        """Sends custom queries to Prometheus and
           returns results as [PrometheusMetric]

        :param query: the query to send
        :type query: str
        """
        # TODO: Remove the prints. (I'll leave them here for some time, because
        #       they are sometimes pretty useful while playing around with
        #       RBAC for example)
        print("query: ")
        print(query)
        decoded = self._get("query", dict(query=query))

        if decoded['data']['resultType'] == 'vector':
            result = [PrometheusMetric(i) for i in decoded['data']['result']]
        else:
            result = [PrometheusMetric(decoded)]
        return result

    def series(self, matches):
        """Queries the /series/ endpoint of prometheus,
           returns the data it receives

        :param matches: List of matches to send as parameters
        :type matches: [str]
        """
        decoded = self._get("series", {"match[]": matches})

        return decoded['data']

    def labels(self):
        """Queries the /labels/ endpoint of prometheus, returns list of labels

        There isn't a way to tell prometheus to restrict
        which labels to return. It's not possible to enforce
        rbac with this for example.
        """
        decoded = self._get("labels")

        return decoded['data']

    def label_values(self, label):
        """Queries prometheus for values of a specified label.

        :param label: Name of label for which to return values
        :type label: str
        """
        decoded = self._get(f"label/{label}/values")

        return decoded['data']

    # ---------
    # admin api
    # ---------

    def delete(self, matches, start=None, end=None):
        """Deletes some metrics from prometheus

        :param matches: List of matches, that specify which metrics to delete
        :type matches [str]
        :param start: Timestamp from which to start deleting.
                      None for as early as possible.
        :type start: timestamp
        :param end: Timestamp until which to delete.
                    None for as late as possible.
        :type end: timestamp
        """
        # NOTE Prometheus doesn't seem to return anything except
        #      of 204 status code. There doesn't seem to be a
        #      way to know if anything got actually deleted.
        #      It does however return 500 code and error msg
        #      if the admin APIs are disabled.

        try:
            self._post("admin/tsdb/delete_series", {"match[]": matches,
                                                    "start": start,
                                                    "end": end})
        except PrometheusAPIClientError as exc:
            # The 204 is allowed here. 204 is "No Content",
            # which is expected on a successful call
            if exc.resp.status_code != 204:
                raise exc

    def clean_tombstones(self):
        """Asks prometheus to clean tombstones"""
        try:
            self._post("admin/tsdb/clean_tombstones")
        except PrometheusAPIClientError as exc:
            # The 204 is allowed here. 204 is "No Content",
            # which is expected on a successful call
            if exc.resp.status_code != 204:
                raise exc

    def snapshot(self):
        """Creates snapshot of all current data and returns the file name,
           which contains the data.
        """
        ret = self._post("admin/tsdb/snapshot")
        return ret["data"]["name"]
