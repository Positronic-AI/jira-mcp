# Publishing to PyPI

This guide explains how to publish the `jira-mcp-server` package to PyPI.

## Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Verify your email

2. **Test PyPI Account** (Optional but recommended)
   - Create account at https://test.pypi.org/account/register/
   - Use for testing before publishing to real PyPI

3. **API Tokens**
   - Go to https://pypi.org/manage/account/token/
   - Create API token for uploads
   - Save it securely (you'll only see it once!)

## Setup

1. **Install build tools**
   ```bash
   pip install --upgrade build twine
   ```

2. **Configure PyPI credentials**

   Create `~/.pypirc`:
   ```ini
   [pypi]
   username = __token__
   password = pypi-your-api-token-here

   [testpypi]
   username = __token__
   password = pypi-your-test-api-token-here
   ```

   **Security**: Set restrictive permissions:
   ```bash
   chmod 600 ~/.pypirc
   ```

## Building the Package

1. **Clean previous builds**
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

2. **Build the package**
   ```bash
   python -m build
   ```

   This creates:
   - `dist/jira_mcp_server-1.0.0.tar.gz` (source distribution)
   - `dist/jira_mcp_server-1.0.0-py3-none-any.whl` (wheel)

3. **Verify the build**
   ```bash
   twine check dist/*
   ```

   Should show:
   ```
   Checking dist/jira_mcp_server-1.0.0.tar.gz: PASSED
   Checking dist/jira_mcp_server-1.0.0-py3-none-any.whl: PASSED
   ```

## Testing on Test PyPI (Recommended)

1. **Upload to Test PyPI**
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Test installation**
   ```bash
   # In a new virtual environment
   python -m venv test_env
   source test_env/bin/activate
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ jira-mcp-server
   ```

   Note: `--extra-index-url` is needed for dependencies

3. **Test the command**
   ```bash
   jira-mcp --help
   ```

4. **If everything works, clean up**
   ```bash
   deactivate
   rm -rf test_env
   ```

## Publishing to PyPI

1. **Final checks**
   - [ ] Version number updated in `pyproject.toml`
   - [ ] CHANGELOG.md updated
   - [ ] README.md accurate
   - [ ] All tests pass
   - [ ] Package tested on Test PyPI

2. **Upload to PyPI**
   ```bash
   twine upload dist/*
   ```

3. **Verify**
   - Visit https://pypi.org/project/jira-mcp-server/
   - Check the page renders correctly
   - Test installation:
     ```bash
     pip install jira-mcp-server
     ```

## Post-Publishing

1. **Tag the release on GitHub**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Create GitHub Release**
   - Go to https://github.com/Positronic-AI/jira-mcp/releases/new
   - Select tag `v1.0.0`
   - Add release notes from CHANGELOG.md
   - Publish release

3. **Announce**
   - Update README with PyPI badge
   - Tweet/post about the release
   - Update documentation

## Publishing Updates

For subsequent releases:

1. **Update version**
   - Edit `pyproject.toml`: `version = "1.0.1"`
   - Update `jira_mcp/__init__.py`: `__version__ = "1.0.1"`
   - Update `CHANGELOG.md`

2. **Clean and rebuild**
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   twine check dist/*
   ```

3. **Upload**
   ```bash
   twine upload dist/*
   ```

4. **Tag and release**
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes

Examples:
- `1.0.0` - Initial release
- `1.0.1` - Bug fix
- `1.1.0` - Add attachment support
- `2.0.0` - Change API structure (breaking)

## Troubleshooting

### "File already exists"
- You can't re-upload the same version
- Bump the version number and rebuild

### "Invalid or non-existent authentication"
- Check your API token in `~/.pypirc`
- Ensure it starts with `pypi-`
- Regenerate if needed

### "Package name too similar"
- PyPI prevents confusingly similar names
- Our name `jira-mcp-server` should be unique

### Build failures
- Check `pyproject.toml` syntax
- Ensure all files are included in `MANIFEST.in`
- Verify imports work: `python -c "import jira_mcp"`

## Security Best Practices

1. **Never commit API tokens** to git
2. **Use API tokens**, not passwords
3. **Set token permissions** to "Upload packages only"
4. **Rotate tokens** periodically
5. **Use 2FA** on your PyPI account

## Additional Resources

- PyPI Help: https://pypi.org/help/
- Packaging Tutorial: https://packaging.python.org/tutorials/packaging-projects/
- Twine Documentation: https://twine.readthedocs.io/

---

## Quick Reference

```bash
# Complete publishing workflow
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*                         # Real PyPI
git tag v1.0.0
git push origin v1.0.0
```
