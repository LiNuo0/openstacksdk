# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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

"""
test_cloud_endpoints
----------------------------------

Tests Keystone endpoints commands.
"""

import uuid

from testtools import matchers

from openstack.tests.unit import base


class TestCloudEndpoints(base.TestCase):
    def get_mock_url(
        self,
        service_type='identity',
        interface='public',
        resource='endpoints',
        append=None,
        base_url_append='v3',
    ):
        return super().get_mock_url(
            service_type, interface, resource, append, base_url_append
        )

    def _dummy_url(self):
        return f'https://{uuid.uuid4().hex}.example.com/'

    def test_create_endpoint(self):
        service_data = self._get_service_data()
        public_endpoint_data = self._get_endpoint_v3_data(
            service_id=service_data.service_id,
            interface='public',
            url=self._dummy_url(),
        )
        public_endpoint_data_disabled = self._get_endpoint_v3_data(
            service_id=service_data.service_id,
            interface='public',
            url=self._dummy_url(),
            enabled=False,
        )
        admin_endpoint_data = self._get_endpoint_v3_data(
            service_id=service_data.service_id,
            interface='admin',
            url=self._dummy_url(),
            region=public_endpoint_data.region_id,
        )
        internal_endpoint_data = self._get_endpoint_v3_data(
            service_id=service_data.service_id,
            interface='internal',
            url=self._dummy_url(),
            region=public_endpoint_data.region_id,
        )

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='services', append=[service_data.service_id]
                    ),
                    status_code=200,
                    json=service_data.json_response_v3,
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json=public_endpoint_data_disabled.json_response,
                    validate=dict(
                        json=public_endpoint_data_disabled.json_request
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='services', append=[service_data.service_id]
                    ),
                    status_code=200,
                    json=service_data.json_response_v3,
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json=public_endpoint_data.json_response,
                    validate=dict(json=public_endpoint_data.json_request),
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json=internal_endpoint_data.json_response,
                    validate=dict(json=internal_endpoint_data.json_request),
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json=admin_endpoint_data.json_response,
                    validate=dict(json=admin_endpoint_data.json_request),
                ),
            ]
        )

        endpoints = self.cloud.create_endpoint(
            service_name_or_id=service_data.service_id,
            region=public_endpoint_data_disabled.region_id,
            url=public_endpoint_data_disabled.url,
            interface=public_endpoint_data_disabled.interface,
            enabled=False,
        )

        # Test endpoint values
        self.assertThat(
            endpoints[0].id,
            matchers.Equals(public_endpoint_data_disabled.endpoint_id),
        )
        self.assertThat(
            endpoints[0].url,
            matchers.Equals(public_endpoint_data_disabled.url),
        )
        self.assertThat(
            endpoints[0].interface,
            matchers.Equals(public_endpoint_data_disabled.interface),
        )
        self.assertThat(
            endpoints[0].region_id,
            matchers.Equals(public_endpoint_data_disabled.region_id),
        )
        self.assertThat(
            endpoints[0].region_id,
            matchers.Equals(public_endpoint_data_disabled.region_id),
        )
        self.assertThat(
            endpoints[0].is_enabled,
            matchers.Equals(public_endpoint_data_disabled.enabled),
        )

        endpoints_2on3 = self.cloud.create_endpoint(
            service_name_or_id=service_data.service_id,
            region=public_endpoint_data.region_id,
            public_url=public_endpoint_data.url,
            internal_url=internal_endpoint_data.url,
            admin_url=admin_endpoint_data.url,
        )

        # Three endpoints should be returned, public, internal, and admin
        self.assertThat(len(endpoints_2on3), matchers.Equals(3))

        # test keys and values are correct for each endpoint created
        for result, reference in zip(
            endpoints_2on3,
            [
                public_endpoint_data,
                internal_endpoint_data,
                admin_endpoint_data,
            ],
        ):
            self.assertThat(result.id, matchers.Equals(reference.endpoint_id))
            self.assertThat(result.url, matchers.Equals(reference.url))
            self.assertThat(
                result.interface, matchers.Equals(reference.interface)
            )
            self.assertThat(
                result.region_id, matchers.Equals(reference.region_id)
            )
            self.assertThat(
                result.is_enabled, matchers.Equals(reference.enabled)
            )
        self.assert_calls()

    def test_update_endpoint(self):
        service_data = self._get_service_data()
        dummy_url = self._dummy_url()
        endpoint_data = self._get_endpoint_v3_data(
            service_id=service_data.service_id,
            interface='admin',
            enabled=False,
        )
        reference_request = endpoint_data.json_request.copy()
        reference_request['endpoint']['url'] = dummy_url
        self.register_uris(
            [
                dict(
                    method='PATCH',
                    uri=self.get_mock_url(append=[endpoint_data.endpoint_id]),
                    status_code=200,
                    json=endpoint_data.json_response,
                    validate=dict(json=reference_request),
                )
            ]
        )
        endpoint = self.cloud.update_endpoint(
            endpoint_data.endpoint_id,
            service_name_or_id=service_data.service_id,
            region=endpoint_data.region_id,
            url=dummy_url,
            interface=endpoint_data.interface,
            enabled=False,
        )

        # test keys and values are correct
        self.assertThat(
            endpoint.id, matchers.Equals(endpoint_data.endpoint_id)
        )
        self.assertThat(
            endpoint.service_id, matchers.Equals(service_data.service_id)
        )
        self.assertThat(endpoint.url, matchers.Equals(endpoint_data.url))
        self.assertThat(
            endpoint.interface, matchers.Equals(endpoint_data.interface)
        )

        self.assert_calls()

    def test_list_endpoints(self):
        endpoints_data = [self._get_endpoint_v3_data() for e in range(1, 10)]
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'endpoints': [
                            e.json_response['endpoint'] for e in endpoints_data
                        ]
                    },
                )
            ]
        )

        endpoints = self.cloud.list_endpoints()
        # test we are getting exactly len(self.mock_endpoints) elements
        self.assertThat(len(endpoints), matchers.Equals(len(endpoints_data)))

        # test keys and values are correct
        for i, ep in enumerate(endpoints_data):
            self.assertThat(endpoints[i].id, matchers.Equals(ep.endpoint_id))
            self.assertThat(
                endpoints[i].service_id, matchers.Equals(ep.service_id)
            )
            self.assertThat(endpoints[i].url, matchers.Equals(ep.url))
            self.assertThat(
                endpoints[i].interface, matchers.Equals(ep.interface)
            )

        self.assert_calls()

    def test_search_endpoints(self):
        endpoints_data = [
            self._get_endpoint_v3_data(region='region1') for e in range(0, 2)
        ]
        endpoints_data.extend(
            [self._get_endpoint_v3_data() for e in range(1, 8)]
        )
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'endpoints': [
                            e.json_response['endpoint'] for e in endpoints_data
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'endpoints': [
                            e.json_response['endpoint'] for e in endpoints_data
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'endpoints': [
                            e.json_response['endpoint'] for e in endpoints_data
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'endpoints': [
                            e.json_response['endpoint'] for e in endpoints_data
                        ]
                    },
                ),
            ]
        )

        # Search by id
        endpoints = self.cloud.search_endpoints(
            id=endpoints_data[-1].endpoint_id
        )
        # # test we are getting exactly 1 element
        self.assertEqual(1, len(endpoints))
        self.assertThat(
            endpoints[0].id, matchers.Equals(endpoints_data[-1].endpoint_id)
        )
        self.assertThat(
            endpoints[0].service_id,
            matchers.Equals(endpoints_data[-1].service_id),
        )
        self.assertThat(
            endpoints[0].url, matchers.Equals(endpoints_data[-1].url)
        )
        self.assertThat(
            endpoints[0].interface,
            matchers.Equals(endpoints_data[-1].interface),
        )

        # Not found
        endpoints = self.cloud.search_endpoints(id='!invalid!')
        self.assertEqual(0, len(endpoints))

        # Multiple matches
        endpoints = self.cloud.search_endpoints(
            filters={'region_id': 'region1'}
        )
        # # test we are getting exactly 2 elements
        self.assertEqual(2, len(endpoints))

        # test we are getting the correct response for region/region_id compat
        endpoints = self.cloud.search_endpoints(
            filters={'region_id': 'region1'}
        )
        # # test we are getting exactly 2 elements, this is v3
        self.assertEqual(2, len(endpoints))

        self.assert_calls()

    def test_delete_endpoint(self):
        endpoint_data = self._get_endpoint_v3_data()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[endpoint_data.endpoint_id]),
                    status_code=200,
                    json=endpoint_data.json_response['endpoint'],
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(append=[endpoint_data.endpoint_id]),
                    status_code=204,
                ),
            ]
        )

        # Delete by id
        self.cloud.delete_endpoint(id=endpoint_data.endpoint_id)
        self.assert_calls()
