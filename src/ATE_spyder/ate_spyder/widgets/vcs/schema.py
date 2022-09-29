# -*- coding: utf-8 -*-

# Copyright © Semi ATE

"""
Some Git service repository initialization schemas.
"""

# Standard library imports
from __future__ import annotations

import sys
from types import MappingProxyType
from typing import Optional, Tuple, List

# PEP 589 and 544 are available from Python 3.8 onwards
if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


GitHubLicenses = MappingProxyType({
    'Apache license 2.0': 'apache-2.0',
    'Boost Software License 1.0': 'bsl-1.0',
    'BSD 2-clause "Simplified" license': 'bsd-2-clause',
    'BSD 3-clause "New" or "Revised" license': 'bsd-3-clause',
    'BSD 3-clause Clear license': 'bsd-3-clause-clear',
    'Eclipse Public License 1.0': 'epl-1.0',
    'Eclipse Public License 2.0': 'epl-2.0',
    'European Union Public License 1.1': 'eupl-1.1',
    'GNU Affero General Public License v3.0': 'agpl-3.0',
    'GNU General Public License v2.0': 'gpl-2.0',
    'GNU General Public License v3.0': 'gpl-3.0',
    'GNU Lesser General Public License v2.1': 'lgpl-2.1',
    'GNU Lesser General Public License v3.0': 'lgpl-3.0',
    'Microsoft Public License': 'ms-pl',
    'MIT': 'mit',
    'Mozilla Public License 2.0': 'mpl-2.0',
    'The Unlicense': 'unlicense',
    'zLib License': 'zlib',
})


class GitHubUser(TypedDict):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: Optional[str]
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: str
    name: Optional[str]
    company: Optional[str]
    blog: Optional[str]
    location: Optional[str]
    email: Optional[str]
    hireable: Optional[bool]
    bio: Optional[str]
    twitter_username: Optional[str]
    public_repos: int
    public_gists: int
    followers: int
    following: int
    created_at: str
    updated_at: str
    private_gists: int
    total_private_repos: int
    owned_private_repos: int
    disk_usage: int
    collaborators: int
    two_factor_authentication: bool
    plan: dict
    suspended_at: Optional[str]
    business_plus: bool
    ldap_dn: str


class GitHubOrganizationInfo(TypedDict):
    login: str
    id: str
    node_id: str
    url: str
    repos_url: str
    events_url: str
    hooks_url: str
    issues_url: str
    members_url: str
    public_members_url: str
    avatar_url: str
    description: Optional[str]


class GitHubOrganization(GitHubOrganizationInfo):
    name: str
    company: str
    blog: str
    location: str
    email: str
    twitter_username: Optional[str]
    is_verified: bool
    has_organization_projects: bool
    has_repository_projects: bool
    public_repos: int
    public_gists: int
    followers: int
    following: int
    html_url: str
    created_at: str
    type: str
    total_private_repos: int
    owned_private_repos: int
    private_gists: Optional[int]
    disk_usage: Optional[int]
    collaborators: Optional[int]
    billing_email: Optional[str]
    plan: dict
    default_repository_permission: Optional[str]
    members_can_create_repositories: Optional[bool]
    two_factor_requirement_enabled: Optional[bool]
    members_allowed_repository_creation_type: str
    members_can_create_public_repositories: bool
    members_can_create_private_repositories: bool
    members_can_create_internal_repositories: bool
    members_can_create_pages: bool
    members_can_create_public_pages: bool
    members_can_create_private_pages: bool
    members_can_fork_private_repositories: Optional[bool]
    web_commit_signoff_required: bool
    updated_at: str
    advanced_security_enabled_for_new_repositories: bool
    dependabot_alerts_enabled_for_new_repositories: bool
    dependabot_security_updates_enabled_for_new_repositories: bool
    dependency_graph_enabled_for_new_repositories: bool
    secret_scanning_enabled_for_new_repositories: bool
    secret_scanning_push_protection_enabled_for_new_repositories: bool


class GitHubUserRepoPermissions(TypedDict):
    admin: bool
    maintain: bool
    push: bool
    triage: bool
    pull: bool


class GitHubRepository(TypedDict):
    id: int
    node_id: int
    name: str
    full_name: str
    owner: GitHubUser
    private: bool
    html_url: str
    description: Optional[str]
    fork: bool
    url: str
    archive_url: str
    assignees_url: str
    blobs_url: str
    branches_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: str
    deployments_url: str
    downloads_url: str
    events_url: str
    foks_url: str
    git_commits_url: str
    git_refs_url: str
    git_tags_url: str
    git_url: str
    issue_comment_url: str
    issue_events_url: str
    issues_url: str
    keys_url: str
    labels_url: str
    languages_url: str
    merges_url: str
    milestones_url: str
    notifications_url: str
    pulls_url: str
    releases_url: str
    ssh_url: str
    stargazers_url: str
    statuses_url: str
    subscribers_url: str
    subscription_url: str
    tags_url: str
    teams_url: str
    trees_url: str
    clone_url: str
    mirror_url: Optional[str]
    hooks_url: str
    svn_url: str
    homepage: Optional[str]
    language: Optional[str]
    forks_count: int
    stargazers_count: int
    watchers_count: int
    size: int
    default_branch: str
    open_issues_count: int
    is_template: bool
    topics: List[str]
    has_issues: bool
    has_projects: bool
    has_wiki: bool
    has_pages: bool
    has_downloads: bool
    archived: bool
    disabled: bool
    visibility: str
    pushed_at: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    permissions: GitHubUserRepoPermissions
    role_name: str
    template_repository: dict
    temp_clone_token: str
    delete_branch_on_merge: bool
    subscribers_count: int
    network_count: int
    code_of_conduct: dict
    license: dict
    forks: int
    open_issues: int
    watchers: int
    allow_forking: bool
    web_commit_signoff_required: bool


class GitHubCommit(TypedDict):
    sha: str
    url: str


class GitHubBranch(TypedDict):
    name: str
    commit: GitHubCommit
    protected: bool
    protection: dict
    protection_url: str
