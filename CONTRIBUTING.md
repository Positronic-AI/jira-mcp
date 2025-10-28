# Contributing to Jira MCP Server

Thank you for your interest in contributing! This project aims to be a clean, reliable MCP server for Jira integration.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/jira-mcp.git
   cd jira-mcp
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up test environment**
   ```bash
   export JIRA_TEST_URL="https://your-test-instance.atlassian.net"
   export JIRA_TEST_EMAIL="your-email@example.com"
   export JIRA_TEST_TOKEN="your-api-token"
   ```

5. **Test the connection**
   ```bash
   python server.py --test-connection test
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints throughout
- Keep functions focused and well-documented
- Write descriptive commit messages

## Testing

Before submitting a PR:

1. Test all core operations manually
2. Ensure error handling works correctly
3. Verify the server works with Claude Desktop
4. Check that logging is appropriate

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Pull Request Guidelines

- **Clear description**: Explain what your PR does and why
- **Single purpose**: One feature/fix per PR
- **Documentation**: Update docs if you change functionality
- **No credentials**: Never commit API tokens or personal info

## What We're Looking For

Good candidates for contributions:

- **Bug fixes**: Found an issue? We'd love a fix!
- **Error handling**: Improve error messages and recovery
- **Documentation**: Better examples, clearer instructions
- **New features**: Additional Jira operations (attachments, sprints, etc.)
- **Testing**: Unit tests, integration tests
- **Performance**: Optimizations that maintain reliability

## Areas We're Interested In

- Support for Jira Data Center (not just Cloud)
- Attachment upload/download
- Sprint and board operations
- Custom field handling
- Better pagination for large result sets
- Webhook support
- Caching for better performance

## Code Review Process

Maintainers will review your PR and may:

- Request changes or improvements
- Ask questions about your approach
- Suggest alternative implementations
- Merge your PR!

Please be patient - we'll try to review within a few days.

## Questions?

Open an issue for:
- Questions about the codebase
- Feature requests
- Bug reports
- General discussion

## Code of Conduct

Be respectful, constructive, and professional. We're all here to build something useful together.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
