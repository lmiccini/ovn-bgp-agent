# Copyright 2021 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_concurrency import processutils
from oslo_log import log as logging

from ovn_bgp_agent import constants
import ovn_bgp_agent.privileged.frrk8s

LOG = logging.getLogger(__name__)


@ovn_bgp_agent.privileged.frrk8s_cmd.entrypoint
def run_frrk8s_config(frr_config_file):

    f = open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r")
    token = f.read()
    f.close()
    
    c = open(frr_config_file, "r")
    snippet = c.read()
    c.close

    content = {"spec": {"raw": {"rawConfig": "%s" % snippet}}}

    url = "https://kubernetes.default.svc/apis/frrk8s.metallb.io/v1beta1/namespaces/metallb-system/frrconfigurations/test0"
    headers={'Authorization': 'Bearer '+token, 'Content-Type': 'application/merge-patch+json'}
    cacert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'

    try:
        r = requests.patch(url, headers=headers, verify=cacert, data=json.dumps(content))
    except Exception as e:
        LOG.exception("Unable to patch frrconfiguration with %s. Exception: %s",
                      frr_config_file, e)
        raise


#@ovn_bgp_agent.privileged.frrk8s_cmd.entrypoint
#def run_frrk8s_command(command):
#
#    full_args = ['/usr/bin/vtysh', '--vty_socket', constants.FRR_SOCKET_PATH,
#                 '-c', command]
#    try:
#        return processutils.execute(*full_args)[0]
#    except Exception as e:
#        LOG.exception("Unable to execute vtysh with %s. Exception: %s",
#                      full_args, e)
#        raise
