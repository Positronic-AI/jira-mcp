# Jira MCP Server

A clean, reliable [Model Context Protocol](https://modelcontextprotocol.io) server for Jira integration, designed for use with Claude Desktop and other MCP clients.

## Why This Exists

The existing Jira MCP servers have quality issues:
- Pydantic dependency conflicts
- Deprecated API usage (v2 instead of v3)
- Poor error handling
- Unreliable connections

This implementation focuses on:
- ✅ Modern Jira REST API v3
- ✅ Minimal, stable dependencies
- ✅ Proper error handling
- ✅ Multi-instance support
- ✅ Type safety throughout

## Features

### Core Operations
- 🔍 **Search issues** with JQL (Jira Query Language)
- 📄 **Get issue details** with full field information
- ➕ **Create issues** with descriptions, labels, and custom fields
- ✏️ **Update issues** (summary, description, labels, etc.)
- 💬 **Add comments** to issues
- 🔄 **Transition issues** between statuses
- 📋 **List projects** accessible to the user

### Multi-Instance Support
Connect to multiple Jira instances simultaneously:
- Different organizations
- Personal and work accounts
- Multiple teams

## Quick Start

### 1. Installation

**Option A: Install from PyPI (Recommended)**

```bash
pip install jira-mcp-server
```

**Option B: Install from source**

```bash
git clone https://github.com/Positronic-AI/jira-mcp.git
cd jira-mcp
pip install -e .
```

### 2. Get Your Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Claude Desktop MCP")
4. Copy the token

### 3. Test Connection

```bash
export JIRA_MYCOMPANY_URL="https://your-company.atlassian.net"
export JIRA_MYCOMPANY_EMAIL="your.email@company.com"
export JIRA_MYCOMPANY_TOKEN="your_api_token_here"

jira-mcp --test-connection mycompany
```

You should see:
```
✓ Connected successfully!
  User: Your Name (your@email.com)
  Account ID: 123abc...
  Accessible projects: N
```

### 4. Configure Claude Desktop

Edit your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "jira": {
      "command": "jira-mcp",
      "args": ["--instance", "mycompany"],
      "env": {
        "JIRA_MYCOMPANY_URL": "https://your-company.atlassian.net",
        "JIRA_MYCOMPANY_EMAIL": "your.email@company.com",
        "JIRA_MYCOMPANY_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

**Note**: If you installed in a virtual environment, use the full path to `jira-mcp`, e.g., `/path/to/venv/bin/jira-mcp`

### 5. Restart Claude Desktop

Completely quit and reopen Claude Desktop.

### 6. Test It!

Try these commands in Claude:

```
List my Jira projects

Search for issues assigned to me

Show me PROJECT-123

Create a new task in PROJECT called "Test MCP integration"
```

## Usage Examples

### Natural Language Commands

Once configured, you can use natural language with Claude:

- "Find all open bugs in the MOBILE project"
- "Show me high priority issues assigned to me"
- "Create a task about fixing the login page"
- "Add a comment to PROJ-42 saying the fix is deployed"
- "Move PROJ-42 to In Progress"
- "Update the summary of PROJ-42 to include more details"

### Direct JQL Queries

```
Search Jira with: project = PROJ AND status = "In Progress" ORDER BY priority DESC
```

## Multi-Instance Configuration

To connect multiple Jira instances:

```json
{
  "mcpServers": {
    "jira-work": {
      "command": "jira-mcp",
      "args": ["--instance", "work"],
      "env": {
        "JIRA_WORK_URL": "https://company.atlassian.net",
        "JIRA_WORK_EMAIL": "you@company.com",
        "JIRA_WORK_TOKEN": "token1"
      }
    },
    "jira-personal": {
      "command": "jira-mcp",
      "args": ["--instance", "personal"],
      "env": {
        "JIRA_PERSONAL_URL": "https://personal.atlassian.net",
        "JIRA_PERSONAL_EMAIL": "you@personal.com",
        "JIRA_PERSONAL_TOKEN": "token2"
      }
    }
  }
}
```

Claude will know which instance to use based on context.

## Architecture

```
jira-mcp/
├── server.py          # Main MCP server
├── jira_client.py     # Jira REST API v3 wrapper
├── config.py          # Configuration management
├── requirements.txt   # Python dependencies
└── examples/          # Configuration examples
```

### Key Design Decisions

**Minimal Dependencies**: Only essential, stable packages (mcp, httpx, pydantic, python-dotenv)

**Modern API**: Uses Jira REST API v3 (`/rest/api/3/search/jql`) instead of deprecated v2

**Type Safety**: Full type hints throughout for better IDE support and fewer bugs

**Error Handling**: Clear error messages propagated from Jira API

**Multi-Instance**: Environment-based configuration for multiple Jira instances

## Available Tools

The server exposes these MCP tools:

| Tool | Description |
|------|-------------|
| `jira_search` | Search issues using JQL with pagination |
| `jira_get_issue` | Get detailed issue information |
| `jira_create_issue` | Create new issues with custom fields |
| `jira_update_issue` | Update existing issue fields |
| `jira_add_comment` | Add comments to issues |
| `jira_transition_issue` | Change issue status |
| `jira_list_projects` | List accessible projects |

## Troubleshooting

### Connection fails

- Verify your API token is correct
- Check the Jira URL has no trailing slash
- Ensure your email matches the Atlassian account
- Test with: `jira-mcp --test-connection <instance>`

### Claude Desktop doesn't see the server

- Verify JSON config is valid
- Use absolute paths (not `~/` or relative)
- Restart Claude Desktop completely
- Check Claude Desktop logs for errors

### "Module not found" errors

- Ensure `jira-mcp-server` is installed: `pip install jira-mcp-server`
- If using a virtual environment, ensure it's activated or use the full path

### "Field cannot be set" errors

- Not all fields are available on all projects
- Check your project's issue type screen configuration
- Common issue: `priority` field not on screen (make it optional)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas we'd especially appreciate help:
- Unit and integration tests
- Jira Data Center support
- Attachment handling
- Sprint/board operations
- Custom field improvements

## Development

```bash
# Clone and setup
git clone https://github.com/Positronic-AI/jira-mcp.git
cd jira-mcp
pip install -e ".[dev]"

# Test connection
export JIRA_TEST_URL="https://test.atlassian.net"
export JIRA_TEST_EMAIL="test@example.com"
export JIRA_TEST_TOKEN="test_token"
jira-mcp --test-connection test
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built for use with [Claude Desktop](https://claude.ai/desktop)
- Uses the [Model Context Protocol](https://modelcontextprotocol.io)
- Inspired by the need for reliable Jira automation

## Support

- 🐛 [Report bugs](https://github.com/yourusername/jira-mcp/issues)
- 💡 [Request features](https://github.com/yourusername/jira-mcp/issues)
- 📖 [Documentation](https://github.com/yourusername/jira-mcp/wiki)
- 💬 [Discussions](https://github.com/yourusername/jira-mcp/discussions)

---

**Note**: This is an independent project and is not affiliated with Atlassian or Anthropic.
