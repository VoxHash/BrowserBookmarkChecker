#!/bin/bash
# Script to create and push the first release (v1.0.0)

set -e

echo "🚀 Creating release v1.0.0..."

# Check if we're on the right branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "⚠️  Warning: You're not on main/master branch. Current branch: $CURRENT_BRANCH"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if tag already exists
if git rev-parse v1.0.0 >/dev/null 2>&1; then
    echo "⚠️  Tag v1.0.0 already exists locally"
    read -p "Delete and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d v1.0.0
    else
        echo "❌ Aborted"
        exit 1
    fi
fi

# Create tag
echo "📝 Creating tag v1.0.0..."
git tag -a v1.0.0 -m "Release v1.0.0 - Initial release"

echo "✅ Tag created locally"
echo ""
echo "📤 To push the release:"
echo "   git push origin main"
echo "   git push origin v1.0.0"
echo ""
echo "🔔 The GitHub Actions release workflow will automatically:"
echo "   - Build distribution packages for Windows, macOS, and Linux"
echo "   - Create a GitHub release with release notes"
echo "   - Upload distribution artifacts"
echo ""
read -p "Push now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Pushing to remote..."
    git push origin main || git push origin master
    git push origin v1.0.0
    echo "✅ Release pushed! Check GitHub Actions for build status."
else
    echo "ℹ️  Tag created locally. Push manually when ready."
fi
