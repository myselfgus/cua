#!/usr/bin/env bash
#
# Pre-commit hook for secret detection
# This script runs before each commit to check for secrets
#
# Installation: Copy this file to .git/hooks/pre-commit and make it executable
# Or use: ln -s ../../scripts/pre-commit-hook.sh .git/hooks/pre-commit

set -e

echo "🔍 Running pre-commit secret detection..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python3 not found. Skipping secret detection."
    exit 0
fi

# Run secret scanner
if python3 scripts/secret_scanner.py --check-only; then
    echo "✅ No secrets detected. Commit proceeding."
    exit 0
else
    echo ""
    echo "🚨 COMMIT BLOCKED: Secrets detected in your changes!"
    echo ""
    echo "🔧 To fix automatically:"
    echo "   python3 scripts/secret_scanner.py --fix"
    echo ""
    echo "🔍 To review detected secrets:"
    echo "   python3 scripts/secret_scanner.py"
    echo ""
    echo "⚠️  After fixing, add your changes and commit again."
    exit 1
fi