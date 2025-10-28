#!/bin/bash
# Verification script to check if the project is ready for open source release

set -e

echo "🔍 Verifying Jira MCP Server is ready for open source..."
echo ""

# Check for required files
echo "📄 Checking required files..."
required_files=(
    "README.md"
    "LICENSE"
    "CONTRIBUTING.md"
    "CHANGELOG.md"
    ".gitignore"
    "requirements.txt"
    "server.py"
    "jira_client.py"
    "config.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING!)"
        exit 1
    fi
done

# Check that sensitive files are gitignored
echo ""
echo "🔒 Checking .gitignore..."
if grep -q "\.venv" .gitignore && grep -q "\.env" .gitignore; then
    echo "  ✅ .gitignore properly configured"
else
    echo "  ❌ .gitignore may be incomplete"
    exit 1
fi

# Check for hardcoded credentials (basic check)
echo ""
echo "🔐 Checking for potential credentials..."
if grep -r "ATATT3x" --include="*.py" --include="*.json" --exclude-dir=".venv" . > /dev/null 2>&1; then
    echo "  ⚠️  Found potential API token in files:"
    grep -r "ATATT3x" --include="*.py" --include="*.json" --exclude-dir=".venv" .
    exit 1
else
    echo "  ✅ No hardcoded API tokens found"
fi

# Check Python syntax
echo ""
echo "🐍 Checking Python syntax..."
for pyfile in *.py; do
    if python3 -m py_compile "$pyfile" 2>/dev/null; then
        echo "  ✅ $pyfile"
    else
        echo "  ❌ $pyfile (syntax error!)"
        exit 1
    fi
done

# Check if venv exists (should, but won't be committed)
echo ""
echo "📦 Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "  ✅ Virtual environment exists (won't be committed)"
else
    echo "  ⚠️  No virtual environment (run: python3 -m venv .venv)"
fi

# Check example config is sanitized
echo ""
echo "🧹 Checking example config..."
if grep -q "your_jira_api_token_here" examples/claude_desktop_config.json; then
    echo "  ✅ Example config is sanitized"
else
    echo "  ❌ Example config may contain real credentials"
    exit 1
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "📋 Summary:"
echo "  • All required files present"
echo "  • No hardcoded credentials"
echo "  • Python syntax valid"
echo "  • Example configs sanitized"
echo ""
echo "🚀 Ready to publish to GitHub!"
echo ""
echo "Next steps:"
echo "  1. Review PUBLISHING.md"
echo "  2. Create GitHub repository"
echo "  3. git init && git add . && git commit"
echo "  4. git remote add origin <your-repo-url>"
echo "  5. git push -u origin main"
