# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.common import tag
from openstack import resource
from openstack import utils


class Domain(resource.Resource, tag.TagMixin):
    resource_key = 'domain'
    resources_key = 'domains'
    base_path = '/domains'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'name',
        is_enabled='enabled',
        **tag.TagMixin._tag_query_parameters,
    )

    # Properties
    #: The description of this domain. *Type: string*
    description = resource.Body('description')
    #: Setting this attribute to ``False`` prevents users from authorizing
    #: against this domain or any projects owned by this domain, and prevents
    #: users owned by this domain from authenticating or receiving any other
    #: authorization. Additionally, all pre-existing tokens applicable
    #: to the above entities are immediately invalidated.
    #: Re-enabling a domain does not re-enable pre-existing tokens.
    #: *Type: bool*
    is_enabled = resource.Body('enabled', type=bool)
    #: The resource options for the project. Available resource options are
    #: immutable.
    options = resource.Body('options', type=dict)
    #: The links related to the domain resource.
    links = resource.Body('links')

    def assign_role_to_user(self, session, user, role, inherited):
        """Assign role to user on domain"""
        url = utils.urljoin(
            self.base_path,
            self.id,
            'users',
            user.id,
            'roles',
            role.id,
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.put(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def validate_user_has_role(self, session, user, role, inherited):
        """Validates that a user has a role on a domain"""
        url = utils.urljoin(
            self.base_path, self.id, 'users', user.id, 'roles', role.id
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.head(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def unassign_role_from_user(self, session, user, role, inherited):
        """Unassigns a role from a user on a domain"""
        url = utils.urljoin(
            self.base_path, self.id, 'users', user.id, 'roles', role.id
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.delete(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def assign_role_to_group(self, session, group, role, inherited):
        """Assign role to group on domain"""
        url = utils.urljoin(
            self.base_path,
            self.id,
            'groups',
            group.id,
            'roles',
            role.id,
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.put(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def validate_group_has_role(self, session, group, role, inherited):
        """Validates that a group has a role on a domain"""
        url = utils.urljoin(
            self.base_path, self.id, 'groups', group.id, 'roles', role.id
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.head(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def unassign_role_from_group(self, session, group, role, inherited):
        """Unassigns a role from a group on a domain"""
        url = utils.urljoin(
            self.base_path, self.id, 'groups', group.id, 'roles', role.id
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.delete(
            url,
        )
        if resp.status_code == 204:
            return True
        return False
