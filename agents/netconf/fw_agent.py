# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014 Tata Consultancy Services
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Anirudh Vedantam, anirudh.vedantam@tcs.com, Tata Consultancy Services Ltd.

import eventlet
import netaddr
from oslo.config import cfg

from neutron.agent.common import config
from neutron.agent import l3_agent
from neutron.agent.linux import external_process
from neutron.agent.linux import interface
from neutron.agent.linux import ip_lib
from neutron.common import constants as l3_constants
from neutron.common import legacy
from neutron.common import topics
from neutron.openstack.common import log as logging
from neutron.openstack.common import service
from neutron import service as neutron_service
from neutron.services.firewall.agents.fw_netconf import firewall_l3_agent as firewall_netconf_agent
#from neutron.services.firewall.agents.varmour import varmour_api
#from neutron.services.firewall.agents.varmour import varmour_utils as va_utils
from neutron.services.firewall.agents.l3reference import firewall_l3_agent

LOG = logging.getLogger(__name__)

class vArmourL3NATAgent(l3_agent.L3NATAgent,
                        firewall_netconf_agent.FWaaSNetconfAgentRpcCallback):
    def __init__(self, host, conf=None):
        LOG.debug(_('NETCONF L3NATAgent: __init__'))
        #self.rest = varmour_api.vArmourRestAPI()
        super(vArmourL3NATAgent, self).__init__(host, conf)

class vArmourL3NATAgentWithStateReport(vArmourL3NATAgent,
                                       l3_agent.L3NATAgentWithStateReport):
    pass


def main():
    eventlet.monkey_patch()
    conf = cfg.CONF
    #firewall_l3_agent.FWaaSL3AgentRpcCallback = firewall_netconf_agent.FWaaSNetconfAgentRpcCallback
    conf.register_opts(vArmourL3NATAgent.OPTS)
    config.register_interface_driver_opts_helper(conf)
    config.register_use_namespaces_opts_helper(conf)
    config.register_agent_state_opts_helper(conf)
    config.register_root_helper(conf)
    conf.register_opts(interface.OPTS)
    conf.register_opts(external_process.OPTS)
    conf(project='neutron')
    config.setup_logging(conf)
    legacy.modernize_quantum_config(conf)
    server = neutron_service.Service.create(
        binary='neutron-l3-agent',
        topic=topics.L3_AGENT,
        report_interval=cfg.CONF.AGENT.report_interval,
        manager='neutron.services.firewall.agents.fw_netconf.fw_agent.'
                'vArmourL3NATAgentWithStateReport')
    service.launch(server).wait()
