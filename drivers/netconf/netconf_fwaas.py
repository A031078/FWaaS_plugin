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
# @author: Hemanth N, hemanth.n@tcs.com, Tata Consultancy Services

from neutron.agent.linux import ip_lib

from neutron.openstack.common import log as logging
from neutron.services.firewall.drivers import fwaas_base

LOG = logging.getLogger(__name__)

class NetconfFwaasDriver(fwaas_base.FwaasDriverBase):
    def __init__(self):
        LOG.debug(_("Initializing fwaas Netconf driver"))

    def __init__(self , root_helper, ip,  network_id, uname, password, ncport):
		LOG.debug(_("Initializing fwaas Netconf driver"))
        self.__ip = "server="+ip
        self.__uname = "user="+uname
        self.__password = "password="+password
        self.__ncport = "ncport="+ncport
	self.root_helper = root_helper
	self.__network_id = network_id

    def create_firewall(self, apply_list, firewall):
	LOG.debug(_('Creating firewall %(fw_id)s for tenant %(tid)s)'),
                  {'fw_id': firewall['id'], 'tid': firewall['tenant_id']})
        
        return self.update_firewall(apply_list, firewall)

    def update_firewall(self, apply_list, firewall):
	LOG.debug(_('Updating firewall %(fw_id)s for tenant %(tid)s)'),
                  {'fw_id': firewall['id'], 'tid': firewall['tenant_id']})
        
        if firewall['admin_state_up']:
            return self._update_firewall(apply_list, firewall)
        else:
            return self.apply_default_policy(apply_list, firewall)

    def delete_firewall(self, apply_list, firewall):
	LOG.debug(_('Deleting firewall %(fw_id)s for tenant %(tid)s)'),
                  {'fw_id': firewall['id'], 'tid': firewall['tenant_id']})
        
        command = "delete /vyatta-firewall"
        self.executeCommands(command)
        
        return True

    def apply_default_policy(self, apply_list, firewall):
	LOG.debug(_('Applying firewall %(fw_id)s for tenant %(tid)s)'),
                  {'fw_id': firewall['id'], 'tid': firewall['tenant_id']})

	firewall_policy = firewall['firewall_policy_id']
		
	#Delete firewall policy or rule? Apply default policy hardcoded?
	# delete /vyatta-firewall/firewall-name[name='%s']/rule
	# replace /vyatta-firewall/firewall-name[name='%s']/default-action --value='drop'
		
	command_list = []
	command_list.append("delete /vyatta-firewall/firewall-name[name='%s']/rule" % firewall_policy)
	command_list.append("replace /vyatta-firewall/firewall-name[name='%s']/default-action --value='drop'" % firewall_policy)
		
	for command in command_list:
	    self.executeCommands(command)
	    
        return True
    
    def create_nat(self, apply_list, nat):
	LOG.debug(_('Applying NAT %(nat_id)s for tenant %(tid)s)'),
                 {'nat_id': nat['id'], 'tid': nat['tenant_id']})
        
        command_list = []
	    
	vyatta_rules = {
		"source_address": "replace /vyatta-nat/source/rule[name='%s']/source/address --value='%s'",
		"outbound_interface": "replace /vyatta-nat/source/rule[name='%s']/outbound-interface --value='%s'",
		"destination_address": "replace /vyatta-nat/source/rule[name='%s']/destination/address --value='%s'",
		"translation": "replace /vyatta-nat/source/rule[name='%s']/translation/address --value='%s'"	
        }
	    
	command_list.append("replace /vyatta-nat/source/rule[name='%s']" % nat['id'])
	    
        for k,v in vyatta_rules:
        if nat[k]:
            command_list.append(v % (nat['id'], nat[k]))
		
	LOG.debug(_("NAT Policy Command list (%s)"), command_list)
		
	for command in commandlist:
	    self.executeCommands(command)
	    
	return True
	
    def delete_nat(self, apply_list, nat):
	LOG.debug(_('Deleting NAT %(nat_id)s for tenant %(tid)s)'),
                  {'nat_id': nat['id'], 'tid': nat['tenant_id']})
        
        command = "delete /vyatta-nat"
        self.executeCommands(command)
        
        return True
    
    def create_zone(self, apply_list, zone):
        LOG.debug(_('Applying ZONE %(zone_name)s for tenant %(tid)s)'),
                  {'zone_name': zone['zone_name'], 'tid': zone['tenant_id']})
        
        command_list = []
	    
        vyatta_rules = {
		"interface": "replace /vyatta-zone-policy/zone[name='%s']/interface --value='%s'",
		"default_action": "replace /vyatta-zone-policy/zone[name='%s']/default_action --value='%s'",
		"from_zone": "replace /vyatta-zone-policy/zone[name='%s']/from[name='%s']",
		"firewall": "replace /vyatta-zone-policy/zone[name='%s']/firewall/name --value='%s'",
        }
        
        command_list.append("replace /vyatta-zone-policy/zone[name='%s']" % zone['zone_name'])
        
        for k,v in vyatta_rules:
	    if zone[k]:
		command_list.append(v % (zone['zone_name'], zone[k]))
		
	LOG.debug(_("ZONE Command list (%s)"), command_list)
		
	for command in command_list:
	    self.executeCommands(command)
	    
        return True
    
    def delete_zone(self, apply_list, zone):
	LOG.debug(_('Deleting ZONE %(zone_name)s for tenant %(tid)s)'),
                  {'zone_name': zone['zone_name'], 'tid': nat['tenant_id']})
        
        command = "delete /vyatta-zone-policy"
        self.executeCommands(command)
        
        return True
    
    def _update_firewall(self, apply_list, firewall):
        LOG.debug(_("Updating firewall (%s)"), firewall['id'])
        
        firewall_policy = firewall['firewall_policy_id']
        
        command_list = []
        
        vyatta_rules = {
		"action": "replace /vyatta-firewall/firewall-name[name='%s']/rule[name='%s']/action --value='%s'",
		"protocol": "replace /vyatta-firewall/firewall-name[name='%s']/rule[name='%s']/protocol --value='%s'",
		"source_ip_address": "replace /vyatta-firewall/firewall-name[name='%s']/rule[name='%s']/source/address --value='%s'",
		"destination_ip_address": "replace /vyatta-firewall/firewall-name[name='%s']/rule[name='%s']/destination/address --value='%s'",
		"source_port_range_min": "replace /vyatta-firewall/firewall-name[name='%s']/rule[name='%s']/source/port --value='%s'",
		"destination_port_range_min": "replace /vyatta-firewall/firewall-name[name='%s']/rule[name='%s']/destination/port --value='%s'"
        }
        
        firewall_policy_name = firewall_policy['name']
        command_list.append("replace /vyatta-firewall /firewall-name[name='%s']" % firewall_policy_name)
        command_list.append("replace /vyatta-firewall /firewall-name[name='%s']/default-action --value='drop'" % firewall_policy_name)
        
        if firewall_policy['firewall_rules'] is not None:
	    for rule in firewallpolicy['firewall_rules']:
		if not rule['enabled']:
		    continue
				
		if rule['ip_version'] == 4:
		    for k,v in vyatta_rules:
		        if rule[k]:
			    command_list.append(v % (firewall_policy_name, rule['id'], rule[k]))
			else:
			    LOG.warn(_("Unsupported IP version rule."))
		
		LOG.debug(_("Firewall Policy Command list (%s)"), command_list)

        for command in command_list:
	    self.executeCommands(command)
	    
        return True

    def executeCommands(self, command):
	executionList = ['/home/anirudh/workspace1/OpenYuma-master/netconf/target/bin/yangcli']
	executionList.extend([self.__ip, self.__uname, self.__password, self.__ncport])
	executionList.append(command);
		
	# TODO: How to get Namespace.. something fishy
	# TODO: Is apply_list is list of Firewalls???
	namespace = "qdhcp-" + self.__network_id
	ns = ip_lib.IPWrapper(self.root_helper, namespace)
	
	while(True):
	    retVal = ns.netns.execute(executionList,addl_env)
	    if  retVal.find("mgr_io failed") == -1:
		break;
		
	return retVal
