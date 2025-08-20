# Dead File Detector

A comprehensive Python tool for detecting unused code and dead files in software repositories. This tool helps maintain clean codebases by identifying orphaned, unreferenced, and potentially dead files across multiple programming languages.

## Features

### 🔍 **Multi-Language Support**
- Python, JavaScript, TypeScript, Java, C/C++, C#, PHP, Ruby, Go, Rust, Swift
- HTML, CSS, SCSS, YAML, JSON, XML, and configuration files
- Shell scripts, SQL files, and documentation files

### 🎯 **Smart Detection**
- **Unreferenced Files**: Files that aren't imported or referenced by any other files
- **Orphaned Files**: Files that exist alone in directories with no other files
- **Suspicious Files**: Files that might be important despite having no references (entry points, main files)

### ⚙️ **Configurable Analysis**
- Customizable ignore patterns for build artifacts, dependencies, temporary files
- Flexible reference pattern matching for different languages and frameworks
- File size constraints to avoid scanning very large or empty files
- Special file handling for important files (README, LICENSE, etc.)

### 📊 **Comprehensive Reporting**
- Detailed text reports with categorized findings
- JSON output for CI/CD integration
- Exit codes for automated workflows (0 = clean, 1 = dead files found)

## Installation

The tool is a single Python script with no external dependencies (uses only Python standard library).

```bash
# Make executable
chmod +x detect_dead_files.py

# Run directly
python3 detect_dead_files.py /path/to/repository
```

## Usage

### Basic Usage

```bash
# Scan current directory
./detect_dead_files.py

# Scan specific repository
./detect_dead_files.py /path/to/repo

# Use custom configuration
./detect_dead_files.py . --config dead_file_config.json

# Generate JSON report
./detect_dead_files.py . --format json > report.json

# Verbose output
./detect_dead_files.py . --verbose
```

### Command Line Options

```
positional arguments:
  path                  Path to repository to scan (default: current directory)

options:
  -h, --help           Show this help message and exit
  --config CONFIG      Path to configuration file (JSON format)
  --format {text,json} Output format (default: text)
  --verbose, -v        Enable verbose logging
  --version            Show program's version number and exit
```

## Configuration

Create a `dead_file_config.json` file to customize the detection behavior:

```json
{
  "ignore_patterns": [
    ".git/*",
    "node_modules/*",
    "__pycache__/*",
    "*.pyc",
    "build/*",
    "dist/*"
  ],
  "scan_extensions": [
    ".py", ".js", ".ts", ".java", ".cpp", ".go"
  ],
  "reference_patterns": {
    "import": [
      "import\\s+(?:.*\\s+from\\s+)?['\"]([^'\"]+)['\"]",
      "require\\s*\\(\\s*['\"]([^'\"]+)['\"]\\s*\\)"
    ]
  },
  "special_files": [
    "README.md", "LICENSE", "package.json"
  ]
}
```

### Configuration Options

- **ignore_patterns**: File patterns to exclude from scanning
- **scan_extensions**: File extensions to scan for references
- **reference_patterns**: Regular expressions for finding file references
- **special_files**: Important files that should never be considered dead
- **min_file_size/max_file_size**: File size constraints

## Integration Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
- name: Detect Dead Files
  run: |
    python3 detect_dead_files.py . --format json > dead_files_report.json
    if [ $? -eq 1 ]; then
      echo "⚠️ Dead files detected - see report"
      cat dead_files_report.json
    fi
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: dead-file-detector
        name: Dead File Detector
        entry: python3 detect_dead_files.py
        language: system
        pass_filenames: false
```

### Make Target

```makefile
# Makefile
.PHONY: check-dead-files
check-dead-files:
	@echo "Checking for dead files..."
	@python3 detect_dead_files.py . || echo "Dead files found!"
```

## Output Examples

### Text Report
```
============================================================
DEAD FILE DETECTION REPORT
============================================================
Repository: /path/to/repo
Total files scanned: 42
Files with references: 38

Total potentially dead files: 4

UNREFERENCED FILES (2):
----------------------------------------
  • old_utils.py
  • legacy/deprecated.js

ORPHANED FILES (1):
----------------------------------------
  • temp/test_script.py

SUSPICIOUS FILES (1):
----------------------------------------
  • scripts/main.py

RECOMMENDATIONS:
---------------
• Review unreferenced files - they may be safe to remove
• Check orphaned files - they might be leftover from refactoring
• Investigate suspicious files - they may need explicit references
```

### JSON Report
```json
{
  "unreferenced": [
    "old_utils.py",
    "legacy/deprecated.js"
  ],
  "orphaned": [
    "temp/test_script.py"
  ],
  "suspicious": [
    "scripts/main.py"
  ]
}
```

## How It Works

1. **File Discovery**: Recursively scans the repository for all files, respecting ignore patterns
2. **Reference Extraction**: Uses regex patterns to find imports, includes, and file references
3. **Reference Resolution**: Attempts to resolve references to actual file paths
4. **Dead File Classification**: Categorizes files based on reference patterns and heuristics
5. **Report Generation**: Creates detailed reports with recommendations

## Limitations

- **Reference Resolution**: Complex import paths and dynamic references may not be detected
- **Runtime Dependencies**: Files loaded at runtime may appear dead but are actually used
- **Framework Conventions**: Some frameworks use implicit file loading that may not be detected
- **Generated Files**: Files created at build time may not be properly analyzed

## Best Practices

1. **Review Before Deleting**: Always manually review files before removing them
2. **Use Version Control**: Test in a branch first to ensure nothing breaks
3. **Custom Configuration**: Tailor the configuration to your project's specific needs
4. **Regular Scans**: Include in your regular code maintenance routine
5. **Team Reviews**: Have team members review dead file reports before cleanup

## Contributing

This tool is designed for SRE and DevOps workflows. Enhancements welcome for:
- Additional language support
- Improved reference detection algorithms
- Framework-specific detection patterns
- Performance optimizations for large repositories

## Author

Created by Joseph Kibaki - NOC Analyst & SRE Enthusiast
- Focus: Infrastructure automation and observability
- Expertise: Python automation, monitoring systems, reliability engineering

---

*Part of the SRE toolkit for maintaining clean, observable, and reliable infrastructure codebases.*