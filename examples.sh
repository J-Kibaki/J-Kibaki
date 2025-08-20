#!/bin/bash
# 
# Dead File Detector Example Usage Script
# Demonstrates various ways to use the dead file detection tool
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DETECTOR="$SCRIPT_DIR/detect_dead_files.py"

echo "🔍 Dead File Detector - Example Usage"
echo "======================================"
echo

# Check if the detector exists
if [[ ! -f "$DETECTOR" ]]; then
    echo "❌ Dead file detector not found at $DETECTOR"
    exit 1
fi

# Example 1: Basic scan of current repository
echo "Example 1: Basic scan of current repository"
echo "-------------------------------------------"
python3 "$DETECTOR" "$SCRIPT_DIR"
echo

# Example 2: JSON output for automation
echo "Example 2: JSON output for CI/CD integration"
echo "---------------------------------------------"
echo "Command: python3 detect_dead_files.py . --format json"
python3 "$DETECTOR" "$SCRIPT_DIR" --format json
echo

# Example 3: Using custom configuration
echo "Example 3: Using custom configuration"
echo "-------------------------------------"
if [[ -f "$SCRIPT_DIR/dead_file_config.json" ]]; then
    echo "Command: python3 detect_dead_files.py . --config dead_file_config.json"
    python3 "$DETECTOR" "$SCRIPT_DIR" --config "$SCRIPT_DIR/dead_file_config.json"
else
    echo "ℹ️  No custom config file found (dead_file_config.json)"
fi
echo

# Example 4: Verbose output
echo "Example 4: Verbose output for debugging"
echo "---------------------------------------"
echo "Command: python3 detect_dead_files.py . --verbose"
python3 "$DETECTOR" "$SCRIPT_DIR" --verbose
echo

# Example 5: Help information
echo "Example 5: Help and usage information"
echo "-------------------------------------"
python3 "$DETECTOR" --help
echo

echo "✅ All examples completed!"
echo
echo "💡 Tips for using the dead file detector:"
echo "  • Use --format json for CI/CD integration"
echo "  • Create custom config files for project-specific rules"
echo "  • Review suspicious files - they may be entry points"
echo "  • Always test in a branch before deleting files"
echo
echo "🔧 Integration examples:"
echo "  • CI/CD: Store JSON output as build artifacts"
echo "  • Pre-commit: Add as a git hook for automatic checking"
echo "  • Monitoring: Track dead file metrics over time"