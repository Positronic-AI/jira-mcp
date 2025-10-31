# Jira MCP Server v1.1.0 Enhancements

## Overview
Enhanced the Jira MCP server with critical missing features, particularly **Epic/Parent linking** which was the primary pain point discovered during our Jira migration testing.

## What Was Missing (Problem Statement)
During our lit-mux roadmap migration to Jira, we discovered that the MCP server couldn't:
1. **Link tasks to their parent Epics** - All tasks showed as "No Epic" in Jira
2. Query issues belonging to an Epic
3. Create arbitrary relationships between issues (Blocks, Relates, etc.)
4. Search for users to assign issues
5. Discover available transitions before attempting to change status

This made the Jira integration significantly less useful for hierarchical project management.

## New Features in v1.1.0

### 1. Epic/Parent Linking ✅
**Problem Solved**: Tasks can now be created directly under Epics

**Changes**:
- Added `parent` parameter to `jira_create_issue` tool
- Updated `JiraClient.create_issue()` to accept parent issue key
- Parent is set using the `parent` field in the Jira API

**Usage**:
```python
# Claude can now do this:
"Create a task under epic KAN-4 for implementing model selection UI"

# Which translates to:
jira_create_issue(
    project_key="KAN",
    summary="Implement model selection UI",
    issue_type="Task",
    parent="KAN-4"  # <-- NEW!
)
```

### 2. Issue Linking 🔗
**Problem Solved**: Can create relationships between issues

**New Tool**: `jira_link_issues`

**Changes**:
- Added `JiraClient.link_issues()` method
- Added `JiraClient.get_issue_links()` method for querying existing links
- Supports all standard link types: Relates, Blocks, Is Blocked By, Duplicates, Clones

**Usage**:
```python
# Link two issues
jira_link_issues(
    inward_issue="KAN-14",
    outward_issue="KAN-4",
    link_type="Relates"
)
```

### 3. Epic Management 📊
**Problem Solved**: Can query all tasks under an Epic

**New Tool**: `jira_get_epic_issues`

**Changes**:
- Added `JiraClient.get_epic_issues()` method
- Uses JQL query `parent = {epic_key}` under the hood
- Returns all child issues with full details

**Usage**:
```python
# Get all tasks under an epic
jira_get_epic_issues(epic_key="KAN-4", max_results=100)

# Returns formatted list of all child issues
```

### 4. Transition Discovery 🔄
**Problem Solved**: Can see available transitions before attempting to change status

**New Tool**: `jira_get_transitions`

**Changes**:
- Added `JiraClient.get_available_transitions()` method
- Shows transition name, target status, and transition ID
- Prevents "invalid transition" errors

**Usage**:
```python
# Get available transitions
jira_get_transitions(issue_key="KAN-14")

# Returns:
# - To Do → In Progress (ID: 21)
# - To Do → Done (ID: 31)
```

### 5. User Management 👥
**Problem Solved**: Can search for users and assign issues properly

**New Tools**:
- `jira_search_users` - Find users by name or email
- `jira_assign_issue` - Assign or unassign issues

**Changes**:
- Added `JiraClient.search_users()` method
- Added `JiraClient.assign_issue()` method
- Returns account IDs needed for assignment

**Usage**:
```python
# Search for a user
jira_search_users(query="john.doe")
# Returns: account ID needed for assignment

# Assign issue
jira_assign_issue(issue_key="KAN-14", account_id="abc123...")

# Unassign issue
jira_assign_issue(issue_key="KAN-14")  # No account_id = unassign
```

## Technical Implementation

### Files Changed
1. **jira_mcp/jira_client.py** (+127 lines)
   - Added `parent` parameter to `create_issue()`
   - Added 6 new methods:
     - `link_issues()`
     - `get_issue_links()`
     - `get_epic_issues()`
     - `get_available_transitions()`
     - `search_users()`
     - `assign_issue()`

2. **jira_mcp/server.py** (+146 lines)
   - Added `parent` parameter to `jira_create_issue` tool schema
   - Added 5 new MCP tools with proper input schemas
   - Added handler logic for all new tools
   - Enhanced response messages with more context

3. **Documentation**
   - Updated README.md with new features and examples
   - Updated CHANGELOG.md with v1.1.0 release notes
   - Created this ENHANCEMENTS.md document

### API Endpoints Used
- `POST /rest/api/3/issueLink` - Create issue links
- `GET /rest/api/3/issue/{key}?fields=issuelinks` - Get issue links
- `GET /rest/api/3/search/jql?jql=parent={key}` - Query epic children
- `GET /rest/api/3/issue/{key}/transitions` - Get available transitions
- `GET /rest/api/3/user/search?query={query}` - Search users
- `PUT /rest/api/3/issue/{key}/assignee` - Assign user

All endpoints use Jira REST API v3 for maximum compatibility.

## Testing Recommendations

### Basic Test
```bash
# Test connection still works
jira-mcp --test-connection litai
```

### Integration Tests
1. **Create Epic with Children**:
   ```
   Create an epic called "Test Epic"
   Create a task under that epic called "Test Task"
   ```

2. **Link Issues**:
   ```
   Link KAN-14 to KAN-4 with "Relates" type
   ```

3. **Query Epic Children**:
   ```
   Show me all issues under epic KAN-4
   ```

4. **User Assignment**:
   ```
   Search for user "ben" and assign KAN-14 to them
   ```

5. **Transitions**:
   ```
   What transitions are available for KAN-14?
   Move KAN-14 to In Progress
   ```

## Breaking Changes
None. This is a backward-compatible enhancement.

All existing functionality remains unchanged. New parameters are optional.

## Future Enhancements (Not in v1.1.0)
- Update issue parent (change epic after creation)
- Remove issue links
- Watchers support
- Sprint operations
- Attachment handling
- Batch operations for bulk updates

## Migration Guide for Claude Desktop

### If You're Already Using v1.0.0:
1. Update the package:
   ```bash
   pip install --upgrade jira-mcp-simple
   ```

2. Restart Claude Desktop

3. No config changes needed - all new features work automatically!

### New Natural Language Examples You Can Use:
```
"Create a task under epic KAN-4"
"Show me all issues under epic KAN-4"
"Link KAN-14 to KAN-4"
"What transitions can I use for KAN-14?"
"Search for user john.doe"
"Assign KAN-14 to account abc123"
```

## Summary
This enhancement solves the primary limitation discovered during real-world usage: **the inability to manage Epic hierarchies**. With v1.1.0, the Jira MCP server is now suitable for full project management workflows, not just flat issue tracking.

The implementation maintains the original design philosophy:
- ✅ Clean, minimal code
- ✅ Modern API v3 usage
- ✅ Type safety throughout
- ✅ Proper error handling
- ✅ Clear, informative responses

---

**Version**: 1.1.0
**Release Date**: October 31, 2025
**Maintainer**: Ben Vierck (ben@positronic.ai)
