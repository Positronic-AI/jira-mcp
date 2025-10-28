#!/usr/bin/env python3
"""Simple Jira MCP Server - Clean, reliable Jira integration for Claude Desktop."""

import argparse
import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from config import get_instance_config
from jira_client import JiraClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

# Global Jira client instance
jira_client: Optional[JiraClient] = None


def format_issue_summary(issue: Dict[str, Any]) -> str:
    """Format an issue for display in a compact, readable way."""
    fields = issue.get("fields", {})
    key = issue.get("key", "N/A")
    summary = fields.get("summary", "No summary")
    status = fields.get("status", {}).get("name", "Unknown")
    issue_type = fields.get("issuetype", {}).get("name", "Unknown")
    priority = fields.get("priority", {}).get("name", "None")

    assignee_info = fields.get("assignee")
    if assignee_info:
        assignee = assignee_info.get("displayName", "Unassigned")
    else:
        assignee = "Unassigned"

    return (
        f"[{key}] {summary}\n"
        f"  Type: {issue_type} | Status: {status} | Priority: {priority} | Assignee: {assignee}"
    )


def format_issue_detailed(issue: Dict[str, Any]) -> str:
    """Format an issue with full details."""
    fields = issue.get("fields", {})
    key = issue.get("key", "N/A")

    lines = [
        f"Issue: {key}",
        f"Summary: {fields.get('summary', 'No summary')}",
        f"Type: {fields.get('issuetype', {}).get('name', 'Unknown')}",
        f"Status: {fields.get('status', {}).get('name', 'Unknown')}",
        f"Priority: {fields.get('priority', {}).get('name', 'None')}",
    ]

    # Assignee
    assignee_info = fields.get("assignee")
    if assignee_info:
        lines.append(f"Assignee: {assignee_info.get('displayName', 'Unknown')} ({assignee_info.get('emailAddress', '')})")
    else:
        lines.append("Assignee: Unassigned")

    # Reporter
    reporter_info = fields.get("reporter")
    if reporter_info:
        lines.append(f"Reporter: {reporter_info.get('displayName', 'Unknown')}")

    # Dates
    if created := fields.get("created"):
        lines.append(f"Created: {created}")
    if updated := fields.get("updated"):
        lines.append(f"Updated: {updated}")

    # Description
    description = fields.get("description")
    if description:
        # Handle ADF format description
        if isinstance(description, dict):
            desc_text = extract_text_from_adf(description)
        else:
            desc_text = str(description)
        lines.append(f"\nDescription:\n{desc_text}")

    # Comments
    comments = fields.get("comment", {}).get("comments", [])
    if comments:
        lines.append(f"\nComments ({len(comments)}):")
        for comment in comments[-5:]:  # Show last 5 comments
            author = comment.get("author", {}).get("displayName", "Unknown")
            created = comment.get("created", "")
            body = comment.get("body", {})
            if isinstance(body, dict):
                body_text = extract_text_from_adf(body)
            else:
                body_text = str(body)
            lines.append(f"  [{author} @ {created}]")
            lines.append(f"  {body_text[:200]}...")

    return "\n".join(lines)


def extract_text_from_adf(adf: Dict[str, Any]) -> str:
    """Extract plain text from Atlassian Document Format."""
    if not isinstance(adf, dict):
        return str(adf)

    text_parts = []

    def extract(node):
        if isinstance(node, dict):
            if node.get("type") == "text":
                text_parts.append(node.get("text", ""))
            if "content" in node:
                for child in node["content"]:
                    extract(child)
        elif isinstance(node, list):
            for item in node:
                extract(item)

    extract(adf)
    return " ".join(text_parts)


# Define MCP tools
TOOLS: List[Tool] = [
    Tool(
        name="jira_search",
        description=(
            "Search for Jira issues using JQL (Jira Query Language). "
            "Returns a list of matching issues with key details. "
            "Examples: 'assignee = currentUser()', 'project = PROJ AND status = \"In Progress\"'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "jql": {
                    "type": "string",
                    "description": "JQL query string",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 50)",
                    "default": 50,
                },
            },
            "required": ["jql"],
        },
    ),
    Tool(
        name="jira_get_issue",
        description="Get detailed information about a specific Jira issue by its key (e.g., 'PROJ-123')",
        inputSchema={
            "type": "object",
            "properties": {
                "issue_key": {
                    "type": "string",
                    "description": "Issue key (e.g., 'PROJ-123')",
                },
            },
            "required": ["issue_key"],
        },
    ),
    Tool(
        name="jira_create_issue",
        description=(
            "Create a new Jira issue. Returns the created issue key. "
            "Common issue types: Task, Bug, Story, Epic. "
            "Common priorities: Highest, High, Medium, Low, Lowest"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "project_key": {
                    "type": "string",
                    "description": "Project key (e.g., 'PROJ')",
                },
                "summary": {
                    "type": "string",
                    "description": "Issue summary/title",
                },
                "issue_type": {
                    "type": "string",
                    "description": "Issue type (e.g., 'Task', 'Bug', 'Story')",
                },
                "description": {
                    "type": "string",
                    "description": "Issue description (optional)",
                },
                "priority": {
                    "type": "string",
                    "description": "Priority name (e.g., 'High', 'Medium', 'Low') (optional)",
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of labels (optional)",
                },
            },
            "required": ["project_key", "summary", "issue_type"],
        },
    ),
    Tool(
        name="jira_update_issue",
        description="Update fields on an existing Jira issue",
        inputSchema={
            "type": "object",
            "properties": {
                "issue_key": {
                    "type": "string",
                    "description": "Issue key (e.g., 'PROJ-123')",
                },
                "summary": {
                    "type": "string",
                    "description": "New summary/title (optional)",
                },
                "description": {
                    "type": "string",
                    "description": "New description (optional)",
                },
                "priority": {
                    "type": "string",
                    "description": "New priority name (optional)",
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New labels list (optional)",
                },
            },
            "required": ["issue_key"],
        },
    ),
    Tool(
        name="jira_add_comment",
        description="Add a comment to a Jira issue",
        inputSchema={
            "type": "object",
            "properties": {
                "issue_key": {
                    "type": "string",
                    "description": "Issue key (e.g., 'PROJ-123')",
                },
                "comment": {
                    "type": "string",
                    "description": "Comment text",
                },
            },
            "required": ["issue_key", "comment"],
        },
    ),
    Tool(
        name="jira_transition_issue",
        description=(
            "Transition a Jira issue to a new status. "
            "Common transitions: 'To Do', 'In Progress', 'Done', 'Blocked'. "
            "Available transitions depend on the project workflow."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "issue_key": {
                    "type": "string",
                    "description": "Issue key (e.g., 'PROJ-123')",
                },
                "transition_name": {
                    "type": "string",
                    "description": "Name of the transition (e.g., 'Done', 'In Progress')",
                },
            },
            "required": ["issue_key", "transition_name"],
        },
    ),
    Tool(
        name="jira_list_projects",
        description="List all Jira projects accessible to the authenticated user",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MCP tool calls and route to appropriate Jira client methods."""
    if jira_client is None:
        return [TextContent(type="text", text="Error: Jira client not initialized")]

    try:
        if name == "jira_search":
            jql = arguments["jql"]
            max_results = arguments.get("max_results", 50)

            result = jira_client.search_issues(jql=jql, max_results=max_results)
            issues = result.get("issues", [])
            # New API returns isLast instead of total
            total = result.get("total", len(issues))
            is_last = result.get("isLast", True)

            if not issues:
                return [TextContent(type="text", text=f"No issues found matching: {jql}")]

            output = []
            if total > 0 and total != len(issues):
                output.append(f"Found {total} total issue(s) (showing {len(issues)}):\n")
            elif not is_last:
                output.append(f"Showing {len(issues)} issue(s) (more available):\n")
            else:
                output.append(f"Found {len(issues)} issue(s):\n")

            for issue in issues:
                output.append(format_issue_summary(issue))
                output.append("")

            return [TextContent(type="text", text="\n".join(output))]

        elif name == "jira_get_issue":
            issue_key = arguments["issue_key"]

            issue = jira_client.get_issue(issue_key)
            output = format_issue_detailed(issue)

            return [TextContent(type="text", text=output)]

        elif name == "jira_create_issue":
            project_key = arguments["project_key"]
            summary = arguments["summary"]
            issue_type = arguments["issue_type"]
            description = arguments.get("description")
            priority = arguments.get("priority")
            labels = arguments.get("labels")

            result = jira_client.create_issue(
                project_key=project_key,
                summary=summary,
                issue_type=issue_type,
                description=description,
                priority=priority,
                labels=labels,
            )

            issue_key = result.get("key")
            return [TextContent(
                type="text",
                text=f"Created issue {issue_key}\nURL: {jira_client.base_url}/browse/{issue_key}"
            )]

        elif name == "jira_update_issue":
            issue_key = arguments["issue_key"]
            fields = {}

            if "summary" in arguments:
                fields["summary"] = arguments["summary"]
            if "description" in arguments:
                fields["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": arguments["description"]}],
                        }
                    ],
                }
            if "priority" in arguments:
                fields["priority"] = {"name": arguments["priority"]}
            if "labels" in arguments:
                fields["labels"] = arguments["labels"]

            jira_client.update_issue(issue_key, fields)
            return [TextContent(type="text", text=f"Updated issue {issue_key}")]

        elif name == "jira_add_comment":
            issue_key = arguments["issue_key"]
            comment = arguments["comment"]

            jira_client.add_comment(issue_key, comment)
            return [TextContent(type="text", text=f"Added comment to {issue_key}")]

        elif name == "jira_transition_issue":
            issue_key = arguments["issue_key"]
            transition_name = arguments["transition_name"]

            jira_client.transition_issue(issue_key, transition_name)
            return [TextContent(type="text", text=f"Transitioned {issue_key} to {transition_name}")]

        elif name == "jira_list_projects":
            projects = jira_client.list_projects()

            if not projects:
                return [TextContent(type="text", text="No projects found")]

            output = [f"Found {len(projects)} project(s):\n"]
            for project in projects:
                key = project.get("key", "N/A")
                name = project.get("name", "Unknown")
                project_type = project.get("projectTypeKey", "unknown")
                output.append(f"[{key}] {name} ({project_type})")

            return [TextContent(type="text", text="\n".join(output))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error handling tool call {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main(instance_name: Optional[str] = None):
    """Run the MCP server."""
    global jira_client

    # Load configuration
    try:
        config = get_instance_config(instance_name)
        logger.info(f"Loaded configuration for instance: {config.instance_name}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Initialize Jira client
    try:
        jira_client = JiraClient(config)
        logger.info("Jira client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Jira client: {e}")
        sys.exit(1)

    # Create MCP server
    server = Server("jira-mcp")

    # Register tool list handler
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return TOOLS

    # Register tool call handler
    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> List[TextContent]:
        return await handle_tool_call(name, arguments)

    # Run the server
    logger.info("Starting MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def test_connection(instance_name: str):
    """Test connection to a Jira instance."""
    try:
        config = get_instance_config(instance_name)
        print(f"Testing connection to {config.instance_name} at {config.url}...")

        with JiraClient(config) as client:
            user_info = client.test_connection()
            print(f"✓ Connected successfully!")
            print(f"  User: {user_info.get('displayName')} ({user_info.get('emailAddress')})")
            print(f"  Account ID: {user_info.get('accountId')}")

            # List projects as additional test
            projects = client.list_projects()
            print(f"  Accessible projects: {len(projects)}")
            for project in projects[:5]:  # Show first 5
                print(f"    - [{project['key']}] {project['name']}")

            if len(projects) > 5:
                print(f"    ... and {len(projects) - 5} more")

            return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Jira MCP Server")
    parser.add_argument(
        "--instance",
        type=str,
        help="Jira instance name (e.g., 'positronic'). Can also use JIRA_INSTANCE env var.",
    )
    parser.add_argument(
        "--test-connection",
        type=str,
        metavar="INSTANCE",
        help="Test connection to specified instance and exit",
    )

    args = parser.parse_args()

    if args.test_connection:
        success = test_connection(args.test_connection)
        sys.exit(0 if success else 1)

    # Run the MCP server
    asyncio.run(main(args.instance))
