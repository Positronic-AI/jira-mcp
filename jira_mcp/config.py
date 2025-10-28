"""Configuration management for Jira MCP server."""

import os
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class JiraInstanceConfig(BaseModel):
    """Configuration for a single Jira instance."""

    instance_name: str = Field(description="Friendly name for this instance (e.g., 'positronic')")
    url: HttpUrl = Field(description="Jira instance URL (e.g., https://lit-ai.atlassian.net)")
    email: str = Field(description="Email address for authentication")
    api_token: str = Field(description="Jira API token")

    @classmethod
    def from_env(cls, instance_name: str) -> "JiraInstanceConfig":
        """
        Load configuration from environment variables.

        Expected environment variables:
        - JIRA_{INSTANCE}_URL
        - JIRA_{INSTANCE}_EMAIL
        - JIRA_{INSTANCE}_TOKEN

        Args:
            instance_name: Instance identifier (e.g., 'positronic')

        Returns:
            JiraInstanceConfig object

        Raises:
            ValueError: If required environment variables are missing
        """
        instance_upper = instance_name.upper()

        url = os.getenv(f"JIRA_{instance_upper}_URL")
        email = os.getenv(f"JIRA_{instance_upper}_EMAIL")
        token = os.getenv(f"JIRA_{instance_upper}_TOKEN")

        if not url:
            raise ValueError(f"Missing JIRA_{instance_upper}_URL environment variable")
        if not email:
            raise ValueError(f"Missing JIRA_{instance_upper}_EMAIL environment variable")
        if not token:
            raise ValueError(f"Missing JIRA_{instance_upper}_TOKEN environment variable")

        return cls(
            instance_name=instance_name,
            url=url,
            email=email,
            api_token=token
        )


def get_instance_config(instance_name: Optional[str] = None) -> JiraInstanceConfig:
    """
    Get configuration for a specific Jira instance.

    Args:
        instance_name: Instance identifier. If None, attempts to read from JIRA_INSTANCE env var.

    Returns:
        JiraInstanceConfig object

    Raises:
        ValueError: If instance_name is not provided and JIRA_INSTANCE is not set
    """
    if instance_name is None:
        instance_name = os.getenv("JIRA_INSTANCE")
        if not instance_name:
            raise ValueError(
                "No instance specified. Provide --instance argument or set JIRA_INSTANCE environment variable"
            )

    return JiraInstanceConfig.from_env(instance_name)
