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
