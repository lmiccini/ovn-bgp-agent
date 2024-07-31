# Copyright 2022 Red Hat, Inc.
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

from unittest import mock

from ovn_bgp_agent import constants
from ovn_bgp_agent.drivers.openstack.watchers import base_watcher
from ovn_bgp_agent.tests import base as test_base
from ovn_bgp_agent.tests import utils


class FakeOVNLBEvent(base_watcher.OVNLBEvent):
    def run(self):
        pass


class TestOVNLBEvent(test_base.TestCase):

    def setUp(self):
        super(TestOVNLBEvent, self).setUp()
        self.ovnlb_event = FakeOVNLBEvent(
            mock.Mock(), [mock.Mock()])

    def test__get_router(self):
        row = utils.create_row(
            external_ids={constants.OVN_LB_LR_REF_EXT_ID_KEY: 'neutron-net'})
        self.assertEqual('net', self.ovnlb_event._get_router(
            row, constants.OVN_LB_LR_REF_EXT_ID_KEY))
        self.assertEqual('net', self.ovnlb_event._get_router(row))
        row = utils.create_row(
            external_ids={constants.OVN_LR_NAME_EXT_ID_KEY: 'neutron-router1'})
        self.assertEqual('router1', self.ovnlb_event._get_router(
            row, constants.OVN_LR_NAME_EXT_ID_KEY))
        row = utils.create_row(external_ids={})
        self.assertEqual(None, self.ovnlb_event._get_router(row))

    def test__is_vip(self):
        row = utils.create_row(
            external_ids={constants.OVN_LB_VIP_IP_EXT_ID_KEY: '192.168.1.50',
                          constants.OVN_LB_VIP_FIP_EXT_ID_KEY: '172.24.4.5'},
            vips={'192.168.1.50:80': '192.168.1.100:80',
                  '172.24.4.5:80': '192.168.1.100:80'})
        self.assertFalse(self.ovnlb_event._is_vip(row, '172.24.4.5'))
        self.assertTrue(self.ovnlb_event._is_vip(row, '192.168.1.50'))
        row = utils.create_row(external_ids={})
        self.assertFalse(self.ovnlb_event._is_vip(row, '172.24.4.5'))
        self.assertFalse(self.ovnlb_event._is_vip(row, '192.168.1.50'))

    def test__is_fip(self):
        row = utils.create_row(
            external_ids={constants.OVN_LB_VIP_IP_EXT_ID_KEY: '192.168.1.50',
                          constants.OVN_LB_VIP_FIP_EXT_ID_KEY: '172.24.4.5'},
            vips={'192.168.1.50:80': '192.168.1.100:80',
                  '172.24.4.5:80': '192.168.1.100:80'})
        self.assertTrue(self.ovnlb_event._is_fip(row, '172.24.4.5'))
        self.assertFalse(self.ovnlb_event._is_fip(row, '192.168.1.50'))
        row = utils.create_row(external_ids={})
        self.assertFalse(self.ovnlb_event._is_fip(row, '172.24.4.5'))
        self.assertFalse(self.ovnlb_event._is_fip(row, '192.168.1.50'))

    def test__get_ip_from_vips(self):
        row = utils.create_row(
            external_ids={constants.OVN_LB_VIP_IP_EXT_ID_KEY: '192.168.1.50',
                          constants.OVN_LB_VIP_FIP_EXT_ID_KEY: '172.24.4.5'},
            vips={'192.168.1.50:80': '192.168.1.100:80',
                  '172.24.4.5:80': '192.168.1.100:80'})
        self.assertEqual(self.ovnlb_event._get_ip_from_vips(row),
                         ['192.168.1.50', '172.24.4.5'])


class FakeLSPChassisEvent(base_watcher.LSPChassisEvent):
    def run(self):
        pass


class TestLSPChassisEvent(test_base.TestCase):

    def setUp(self):
        super(TestLSPChassisEvent, self).setUp()
        self.lsp_event = FakeLSPChassisEvent(
            mock.Mock(), [mock.Mock()])

    def test__has_additional_binding(self):
        row = utils.create_row(
            options={constants.OVN_REQUESTED_CHASSIS: 'host1,host2'})
        self.assertTrue(self.lsp_event._has_additional_binding(row))

    def test__has_additional_binding_no_options(self):
        row = utils.create_row()
        self.assertFalse(self.lsp_event._has_additional_binding(row))

    def test__has_additional_binding_single_host(self):
        row = utils.create_row(
            options={constants.OVN_REQUESTED_CHASSIS: 'host1'})
        self.assertFalse(self.lsp_event._has_additional_binding(row))

    def test__get_network(self):
        row = utils.create_row(
            external_ids={constants.OVN_LS_NAME_EXT_ID_KEY: 'test-net'})
        self.assertEqual('test-net', self.lsp_event._get_network(row))
        row = utils.create_row(external_ids={})
        self.assertEqual(None, self.lsp_event._get_network(row))


class FakeLRPChassisEvent(base_watcher.LRPChassisEvent):
    def run(self):
        pass


class TestLRPChassisEvent(test_base.TestCase):

    def setUp(self):
        super(TestLRPChassisEvent, self).setUp()
        self.lrp_event = FakeLRPChassisEvent(
            mock.Mock(), [mock.Mock()])

    def test__get_network(self):
        row = utils.create_row(
            external_ids={constants.OVN_LS_NAME_EXT_ID_KEY: 'test-net'})
        self.assertEqual('test-net', self.lrp_event._get_network(row))
        row = utils.create_row(external_ids={})
        self.assertEqual(None, self.lrp_event._get_network(row))


class TestChassisCreateEvent(test_base.TestCase):
    _event = base_watcher.ChassisCreateEvent

    def setUp(self):
        super(TestChassisCreateEvent, self).setUp()
        self.chassis = '935f91fa-b8f8-47b9-8b1b-3a7a90ef7c26'
        self.agent = mock.Mock(chassis=self.chassis)
        self.event = self._event(self.agent)

    def test_run(self):
        self.assertTrue(self.event.first_time)
        self.event.run(mock.Mock(), mock.Mock(), mock.Mock())

        self.assertFalse(self.event.first_time)
        self.agent.sync.assert_not_called()

    def test_run_not_first_time(self):
        self.event.first_time = False
        self.event.run(mock.Mock(), mock.Mock(), mock.Mock())
        self.agent.sync.assert_called_once_with()


class TestChassisPrivateCreateEvent(TestChassisCreateEvent):
    _event = base_watcher.ChassisPrivateCreateEvent
