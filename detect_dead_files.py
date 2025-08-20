#!/usr/bin/env python3
"""
Dead Code Detection Tool
========================

A comprehensive tool to detect unused code and dead files in repositories.
Designed for SRE and DevOps workflows to maintain clean codebases.

Author: Joseph Kibaki
Purpose: Identify orphaned, unused, and dead files across multiple languages
"""

import os
import re
import sys
import json
import argparse
import fnmatch
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class DeadFileDetector:
    """
    A comprehensive dead file detection engine that analyzes repositories
    for unused, unreferenced, and orphaned files across multiple languages.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the detector with configuration."""
        self.config = self._load_config(config_path)
        self.file_references: Dict[str, Set[str]] = defaultdict(set)
        self.all_files: Set[str] = set()
        self.scanned_extensions: Set[str] = set()
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from file or use defaults."""
        default_config = {
            "ignore_patterns": [
                ".git/*",
                "*.log",
                "*.tmp",
                "node_modules/*",
                "__pycache__/*",
                "*.pyc",
                ".pytest_cache/*",
                "venv/*",
                "env/*",
                ".env",
                "dist/*",
                "build/*",
                "target/*",
                ".DS_Store",
                "*.swp",
                "*.bak",
                "coverage/*",
                ".coverage",
                ".tox/*"
            ],
            "scan_extensions": [
                ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", 
                ".h", ".hpp", ".cs", ".php", ".rb", ".go", ".rs", ".swift",
                ".kt", ".scala", ".sh", ".bash", ".ps1", ".sql", ".html",
                ".css", ".scss", ".sass", ".less", ".vue", ".yaml", ".yml",
                ".json", ".xml", ".md", ".txt", ".cfg", ".conf", ".ini"
            ],
            "reference_patterns": {
                "import": [
                    r"import\s+(?:.*\s+from\s+)?['\"]([^'\"]+)['\"]",
                    r"from\s+['\"]([^'\"]+)['\"]\s+import",
                    r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
                    r"#include\s*[<\"]([^>\"]+)[>\"]",
                    r"@import\s+['\"]([^'\"]+)['\"]"
                ],
                "file_path": [
                    r"['\"]([^'\"]*\.[a-zA-Z0-9]+)['\"]",
                    r"src=['\"]([^'\"]+)['\"]",
                    r"href=['\"]([^'\"]+)['\"]"
                ]
            },
            "special_files": [
                "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md",
                "requirements.txt", "package.json", "Dockerfile", "Makefile",
                ".gitignore", ".dockerignore", "setup.py", "pyproject.toml",
                "Cargo.toml", "pom.xml", "build.gradle", "composer.json"
            ],
            "min_file_size": 1,
            "max_file_size": 10485760  # 10MB
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                logger.info("Using default configuration")
        
        return default_config
    
    def _should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored based on patterns."""
        for pattern in self.config["ignore_patterns"]:
            if fnmatch.fnmatch(file_path, pattern) or pattern in file_path:
                return True
        return False
    
    def _is_scannable_file(self, file_path: str) -> bool:
        """Check if file should be scanned for references."""
        ext = Path(file_path).suffix.lower()
        return ext in self.config["scan_extensions"]
    
    def _extract_references(self, file_path: str, content: str) -> Set[str]:
        """Extract file references from file content."""
        references = set()
        
        # Extract import/include references
        for pattern in self.config["reference_patterns"]["import"]:
            matches = re.findall(pattern, content, re.MULTILINE)
            references.update(matches)
        
        # Extract file path references
        for pattern in self.config["reference_patterns"]["file_path"]:
            matches = re.findall(pattern, content, re.MULTILINE)
            references.update(matches)
        
        return references
    
    def _resolve_reference(self, reference: str, base_path: str) -> List[str]:
        """Resolve a reference to actual file paths."""
        resolved = []
        base_dir = os.path.dirname(base_path)
        
        # Try relative to current file
        rel_path = os.path.join(base_dir, reference)
        if os.path.exists(rel_path):
            resolved.append(os.path.normpath(rel_path))
        
        # Try relative to project root
        root_path = os.path.join(self.root_dir, reference)
        if os.path.exists(root_path):
            resolved.append(os.path.normpath(root_path))
        
        # Try with common extensions if no extension provided
        if not Path(reference).suffix:
            for ext in ['.py', '.js', '.ts', '.java', '.cpp']:
                test_path = f"{reference}{ext}"
                rel_test = os.path.join(base_dir, test_path)
                root_test = os.path.join(self.root_dir, test_path)
                
                if os.path.exists(rel_test):
                    resolved.append(os.path.normpath(rel_test))
                elif os.path.exists(root_test):
                    resolved.append(os.path.normpath(root_test))
        
        return resolved
    
    def scan_repository(self, root_path: str) -> Tuple[Set[str], Dict[str, Set[str]]]:
        """
        Scan repository for all files and their references.
        
        Returns:
            Tuple of (all_files, file_references)
        """
        self.root_dir = os.path.abspath(root_path)
        logger.info(f"Scanning repository: {self.root_dir}")
        
        # Collect all files
        for root, dirs, files in os.walk(self.root_dir):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore_file(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.root_dir)
                
                if self._should_ignore_file(rel_path):
                    continue
                
                # Check file size constraints
                try:
                    size = os.path.getsize(file_path)
                    if size < self.config["min_file_size"] or size > self.config["max_file_size"]:
                        continue
                except OSError:
                    continue
                
                self.all_files.add(file_path)
                
                # Scan for references if it's a scannable file
                if self._is_scannable_file(rel_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            references = self._extract_references(file_path, content)
                            
                            # Resolve references to actual files
                            for ref in references:
                                resolved_files = self._resolve_reference(ref, file_path)
                                for resolved in resolved_files:
                                    if resolved in self.all_files:
                                        self.file_references[resolved].add(file_path)
                    
                    except Exception as e:
                        logger.debug(f"Failed to scan {file_path}: {e}")
        
        logger.info(f"Found {len(self.all_files)} files total")
        logger.info(f"Found {len(self.file_references)} files with references")
        
        return self.all_files, dict(self.file_references)
    
    def find_dead_files(self) -> Dict[str, List[str]]:
        """
        Identify potentially dead files.
        
        Returns:
            Dictionary categorizing dead files by type
        """
        if not self.all_files:
            raise ValueError("Repository not scanned yet. Call scan_repository() first.")
        
        dead_files = {
            "unreferenced": [],
            "orphaned": [],
            "suspicious": []
        }
        
        # Find unreferenced files
        for file_path in self.all_files:
            rel_path = os.path.relpath(file_path, self.root_dir)
            
            # Skip special files
            if os.path.basename(file_path) in self.config["special_files"]:
                continue
            
            # Check if file has any references
            if file_path not in self.file_references:
                # Additional checks for potentially important files
                if self._is_potentially_important(file_path):
                    dead_files["suspicious"].append(rel_path)
                else:
                    dead_files["unreferenced"].append(rel_path)
        
        # Find orphaned files (files in directories with no other files)
        dir_file_count = defaultdict(int)
        for file_path in self.all_files:
            dir_path = os.path.dirname(file_path)
            dir_file_count[dir_path] += 1
        
        for file_path in self.all_files:
            dir_path = os.path.dirname(file_path)
            rel_path = os.path.relpath(file_path, self.root_dir)
            
            if (dir_file_count[dir_path] == 1 and 
                rel_path in dead_files["unreferenced"] and
                not self._is_potentially_important(file_path)):
                dead_files["orphaned"].append(rel_path)
                dead_files["unreferenced"].remove(rel_path)
        
        return dead_files
    
    def _is_potentially_important(self, file_path: str) -> bool:
        """Check if file might be important despite having no references."""
        filename = os.path.basename(file_path).lower()
        
        # Entry points and main files
        entry_point_patterns = [
            r'main\.',
            r'index\.',
            r'app\.',
            r'server\.',
            r'start\.',
            r'run\.',
            r'__init__\.',
            r'setup\.',
            r'config\.',
            r'settings\.'
        ]
        
        for pattern in entry_point_patterns:
            if re.match(pattern, filename):
                return True
        
        return False
    
    def generate_report(self, dead_files: Dict[str, List[str]], output_format: str = "text") -> str:
        """Generate a formatted report of dead files."""
        if output_format == "json":
            return json.dumps(dead_files, indent=2)
        
        # Text report
        report = []
        report.append("=" * 60)
        report.append("DEAD FILE DETECTION REPORT")
        report.append("=" * 60)
        report.append(f"Repository: {self.root_dir}")
        report.append(f"Total files scanned: {len(self.all_files)}")
        report.append(f"Files with references: {len(self.file_references)}")
        report.append("")
        
        total_dead = sum(len(files) for files in dead_files.values())
        report.append(f"Total potentially dead files: {total_dead}")
        report.append("")
        
        for category, files in dead_files.items():
            if files:
                report.append(f"{category.upper()} FILES ({len(files)}):")
                report.append("-" * 40)
                for file_path in sorted(files):
                    report.append(f"  • {file_path}")
                report.append("")
        
        if total_dead == 0:
            report.append("🎉 No dead files detected! Repository looks clean.")
        else:
            report.append("RECOMMENDATIONS:")
            report.append("-" * 15)
            report.append("• Review unreferenced files - they may be safe to remove")
            report.append("• Check orphaned files - they might be leftover from refactoring")
            report.append("• Investigate suspicious files - they may need explicit references")
        
        return "\n".join(report)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Detect unused code and dead files in repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/repo                    # Scan repository with defaults
  %(prog)s . --config config.json          # Use custom configuration
  %(prog)s . --format json > report.json   # Generate JSON report
  %(prog)s . --verbose                     # Enable verbose logging
        """
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to repository to scan (default: current directory)"
    )
    
    parser.add_argument(
        "--config",
        help="Path to configuration file (JSON format)"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Dead File Detector 1.0.0"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize detector
        detector = DeadFileDetector(config_path=args.config)
        
        # Scan repository
        detector.scan_repository(args.path)
        
        # Find dead files
        dead_files = detector.find_dead_files()
        
        # Generate and print report
        report = detector.generate_report(dead_files, output_format=args.format)
        print(report)
        
        # Exit with appropriate code
        total_dead = sum(len(files) for files in dead_files.values())
        sys.exit(0 if total_dead == 0 else 1)
        
    except KeyboardInterrupt:
        logger.info("Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()