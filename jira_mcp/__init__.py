"""Jira MCP Server - A clean, reliable MCP server for Jira integration."""

__version__ = "1.0.0"
__author__ = "Ben Vierck"
__email__ = "ben@positronic.ai"

from jira_mcp.config import JiraInstanceConfig, get_instance_config
from jira_mcp.jira_client import JiraClient

__all__ = [
    "JiraInstanceConfig",
    "get_instance_config",
    "JiraClient",
]
