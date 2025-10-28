"""Entry point for running jira-mcp as a module."""

from jira_mcp.server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
