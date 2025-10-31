# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release
- Full Jira REST API v3 support
- Seven core MCP tools:
  - `jira_search` - JQL search with pagination
  - `jira_get_issue` - Detailed issue retrieval
  - `jira_create_issue` - Issue creation
  - `jira_update_issue` - Field updates
  - `jira_add_comment` - Add comments
  - `jira_transition_issue` - Status transitions
  - `jira_list_projects` - Project discovery
- Multi-instance support
- Connection testing utility
- Type hints throughout
- Comprehensive error handling
- ADF (Atlassian Document Format) support for descriptions and comments

### Technical Details
- Uses modern `/rest/api/3/search/jql` endpoint
- Handles new API response format (`isLast` pagination)
- Minimal dependencies (mcp, httpx, pydantic, python-dotenv)
- Environment-based configuration
- Context manager support for proper resource cleanup

## [1.1.0] - 2025-10-31

### Added
- **Epic/Parent linking support**: Create issues directly under epics or as subtasks
  - New `parent` parameter in `jira_create_issue` tool
- **Issue linking**: Create relationships between issues
  - New `jira_link_issues` tool with support for Relates, Blocks, Duplicates, etc.
- **Epic management**: Query all issues belonging to an epic
  - New `jira_get_epic_issues` tool
- **Transition discovery**: Get available transitions before attempting to change status
  - New `jira_get_transitions` tool
- **User management**: Search and assign users
  - New `jira_search_users` tool for finding users by name or email
  - New `jira_assign_issue` tool for assigning/unassigning issues
- Enhanced JiraClient with six new methods:
  - `link_issues()` - Create issue links
  - `get_issue_links()` - Retrieve issue links
  - `get_epic_issues()` - Query epic children
  - `get_available_transitions()` - List valid transitions
  - `search_users()` - Find users
  - `assign_issue()` - Manage assignees

### Improved
- Better error handling for issue linking operations
- Enhanced documentation with advanced usage examples
- More descriptive tool responses including URLs and relationship info

## [Unreleased]

### Planned Features
- Unit and integration tests
- Jira Data Center support
- Attachment upload/download
- Sprint and board operations
- Enhanced custom field handling
- Webhook support
- Caching for improved performance
- Batch operations
