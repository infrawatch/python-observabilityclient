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

def get_client(obj):
    return obj.app.client_manager.observabilityclient

def list2cols(cols, objs):
    return cols, [tuple([o[k] for k in cols])
                  for o in objs]

def format_labels(d: dict) -> str:
    ret = '{'
    for key, value in d.items():
        ret += "{}='{}', ".format(key, value)
    ret = ret[0:-2] + '}'
    return ret

def metrics2cols_old(m):
    cols = []
    fields = []
    first = True
    for metric in m:
        row = []
        for key, value in metric["metric"].items():
            if first:
                cols.append(key)
            row.append(value)
        if first:
            cols.append("value")
        row.append(metric["value"][1])
        fields.append(row)
        first = False
    return cols, fields

def metrics2cols(m):
    cols = []
    fields = []
    first = True
    for metric in m:
        row = []
        for key, value in metric.labels.items():
            if first:
                cols.append(key)
            row.append(value)
        if first:
            cols.append("value")
        row.append(metric.value)
        fields.append(row)
        first = False
    return cols, fields
