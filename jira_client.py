"""Jira REST API v3 client wrapper."""

import logging
from typing import Any, Dict, List, Optional
import httpx
from config import JiraInstanceConfig

logger = logging.getLogger(__name__)


class JiraClient:
    """Simple, reliable Jira REST API v3 client."""

    def __init__(self, config: JiraInstanceConfig):
        """
        Initialize Jira client.

        Args:
            config: JiraInstanceConfig with URL, email, and API token
        """
        self.config = config
        self.base_url = str(config.url).rstrip("/")
        self.api_base = f"{self.base_url}/rest/api/3"

        # Setup authentication
        self.auth = (config.email, config.api_token)

        # Create httpx client with reasonable defaults
        self.client = httpx.Client(
            auth=self.auth,
            timeout=30.0,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        logger.info(f"Initialized Jira client for {self.config.instance_name} at {self.base_url}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle HTTP response and errors.

        Args:
            response: httpx Response object

        Returns:
            Parsed JSON response

        Raises:
            Exception: On HTTP errors with detailed message
        """
        try:
            response.raise_for_status()
            return response.json() if response.text else {}
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_json = e.response.json()
                error_detail = error_json.get("errorMessages", [])
                if not error_detail:
                    error_detail = error_json.get("errors", {})
            except Exception:
                error_detail = e.response.text

            logger.error(f"Jira API error: {e.response.status_code} - {error_detail}")
            raise Exception(f"Jira API error ({e.response.status_code}): {error_detail}")

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Jira instance.

        Returns:
            Dictionary with connection status and user info

        Raises:
            Exception: On connection failure
        """
        logger.info(f"Testing connection to {self.config.instance_name}")
        response = self.client.get(f"{self.api_base}/myself")
        user_info = self._handle_response(response)
        logger.info(f"Connected successfully as {user_info.get('emailAddress')}")
        return user_info

    def search_issues(
        self,
        jql: str,
        start_at: int = 0,
        max_results: int = 50,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search for issues using JQL.

        Args:
            jql: JQL query string
            start_at: Starting index for pagination (default: 0)
            max_results: Maximum number of results to return (default: 50)
            fields: List of fields to return (default: key, summary, status, assignee, priority)

        Returns:
            Dictionary with search results including issues, total, startAt, maxResults

        Raises:
            Exception: On API errors
        """
        if fields is None:
            fields = ["key", "summary", "status", "assignee", "priority", "issuetype", "created", "updated"]

        # New /search/jql endpoint expects GET with query params
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
            "fields": ",".join(fields),
        }

        logger.info(f"Searching issues with JQL: {jql}")
        response = self.client.get(f"{self.api_base}/search/jql", params=params)
        return self._handle_response(response)

    def get_issue(self, issue_key: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            fields: List of fields to return (default: all)

        Returns:
            Dictionary with issue details

        Raises:
            Exception: On API errors
        """
        params = {}
        if fields:
            params["fields"] = ",".join(fields)

        logger.info(f"Getting issue {issue_key}")
        response = self.client.get(f"{self.api_base}/issue/{issue_key}", params=params)
        return self._handle_response(response)

    def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
        **extra_fields,
    ) -> Dict[str, Any]:
        """
        Create a new issue.

        Args:
            project_key: Project key (e.g., 'PROJ')
            summary: Issue summary/title
            issue_type: Issue type (e.g., 'Task', 'Bug', 'Story')
            description: Issue description (optional)
            priority: Priority name (e.g., 'High', 'Medium', 'Low') (optional)
            assignee: Assignee account ID or email (optional)
            labels: List of labels (optional)
            **extra_fields: Additional custom fields

        Returns:
            Dictionary with created issue details (key, id, self)

        Raises:
            Exception: On API errors
        """
        fields: Dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }

        # Add description if provided (using ADF format)
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            }

        # Add priority if provided
        if priority:
            fields["priority"] = {"name": priority}

        # Add assignee if provided
        if assignee:
            fields["assignee"] = {"accountId": assignee}

        # Add labels if provided
        if labels:
            fields["labels"] = labels

        # Add any extra fields
        fields.update(extra_fields)

        payload = {"fields": fields}

        logger.info(f"Creating issue in project {project_key}: {summary}")
        response = self.client.post(f"{self.api_base}/issue", json=payload)
        return self._handle_response(response)

    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> None:
        """
        Update an existing issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            fields: Dictionary of fields to update

        Raises:
            Exception: On API errors
        """
        payload = {"fields": fields}

        logger.info(f"Updating issue {issue_key}")
        response = self.client.put(f"{self.api_base}/issue/{issue_key}", json=payload)
        self._handle_response(response)

    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """
        Add a comment to an issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            comment: Comment text

        Returns:
            Dictionary with created comment details

        Raises:
            Exception: On API errors
        """
        # Use ADF (Atlassian Document Format) for comment body
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment}],
                    }
                ],
            }
        }

        logger.info(f"Adding comment to issue {issue_key}")
        response = self.client.post(f"{self.api_base}/issue/{issue_key}/comment", json=payload)
        return self._handle_response(response)

    def transition_issue(self, issue_key: str, transition_name: str) -> None:
        """
        Transition an issue to a new status.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            transition_name: Name of the transition (e.g., 'Done', 'In Progress')

        Raises:
            Exception: On API errors or if transition is not found
        """
        # First, get available transitions
        logger.info(f"Getting available transitions for {issue_key}")
        response = self.client.get(f"{self.api_base}/issue/{issue_key}/transitions")
        transitions_data = self._handle_response(response)

        # Find the transition ID by name
        transition_id = None
        for transition in transitions_data.get("transitions", []):
            if transition["name"].lower() == transition_name.lower():
                transition_id = transition["id"]
                break

        if not transition_id:
            available = [t["name"] for t in transitions_data.get("transitions", [])]
            raise Exception(
                f"Transition '{transition_name}' not found for {issue_key}. "
                f"Available transitions: {', '.join(available)}"
            )

        # Perform the transition
        payload = {"transition": {"id": transition_id}}

        logger.info(f"Transitioning {issue_key} to {transition_name}")
        response = self.client.post(f"{self.api_base}/issue/{issue_key}/transitions", json=payload)
        self._handle_response(response)

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects accessible to the user.

        Returns:
            List of project dictionaries with key, name, and other details

        Raises:
            Exception: On API errors
        """
        logger.info("Listing all projects")
        response = self.client.get(f"{self.api_base}/project")
        return self._handle_response(response)
