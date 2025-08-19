#!/usr/bin/env python3
"""
Secret Detection and Auto-Fix Script

This script can be run locally to detect and fix secrets before committing.
It's also integrated into the GitHub Actions workflow for automatic enforcement.

Usage:
  python scripts/secret_scanner.py [--fix] [--check-only]
  
Options:
  --fix         Automatically fix detected secrets
  --check-only  Only scan and report, don't fix
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Enhanced secret patterns with more comprehensive detection
SECRET_PATTERNS = {
    'openai_api_key': {
        'pattern': r'(?i)(openai[_-]?api[_-]?key\s*[=:]\s*["\']?)(sk-[a-zA-Z0-9]{20,})["\']?',
        'replacement': r'\1${OPENAI_API_KEY}',
        'env_var': 'OPENAI_API_KEY',
        'description': 'OpenAI API Key'
    },
    'github_token': {
        'pattern': r'(?i)(github[_-]?token\s*[=:]\s*["\']?)(ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|ghu_[a-zA-Z0-9]{36}|ghs_[a-zA-Z0-9]{36}|ghr_[a-zA-Z0-9]{36})["\']?',
        'replacement': r'\1${GITHUB_TOKEN}',
        'env_var': 'GITHUB_TOKEN',
        'description': 'GitHub Personal Access Token'
    },
    'aws_access_key': {
        'pattern': r'(?i)(aws[_-]?access[_-]?key[_-]?id\s*[=:]\s*["\']?)(AKIA[0-9A-Z]{16})["\']?',
        'replacement': r'\1${AWS_ACCESS_KEY_ID}',
        'env_var': 'AWS_ACCESS_KEY_ID',
        'description': 'AWS Access Key ID'
    },
    'aws_secret_key': {
        'pattern': r'(?i)(aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']?)([A-Za-z0-9/+=]{40})["\']?',
        'replacement': r'\1${AWS_SECRET_ACCESS_KEY}',
        'env_var': 'AWS_SECRET_ACCESS_KEY',
        'description': 'AWS Secret Access Key'
    },
    'database_url_postgres': {
        'pattern': r'(?i)(database[_-]?url\s*[=:]\s*["\']?)(postgresql://[^"\'\\s]+)["\']?',
        'replacement': r'\1${DATABASE_URL}',
        'env_var': 'DATABASE_URL',
        'description': 'PostgreSQL Database URL'
    },
    'database_url_mysql': {
        'pattern': r'(?i)(database[_-]?url\s*[=:]\s*["\']?)(mysql://[^"\'\\s]+)["\']?',
        'replacement': r'\1${DATABASE_URL}',
        'env_var': 'DATABASE_URL',
        'description': 'MySQL Database URL'
    },
    'redis_url': {
        'pattern': r'(?i)(redis[_-]?url\s*[=:]\s*["\']?)(redis://[^"\'\\s]+)["\']?',
        'replacement': r'\1${REDIS_URL}',
        'env_var': 'REDIS_URL',
        'description': 'Redis URL'
    },
    'mongodb_url': {
        'pattern': r'(?i)(mongo[_-]?url|mongodb[_-]?url\s*[=:]\s*["\']?)(mongodb://[^"\'\\s]+|mongodb\+srv://[^"\'\\s]+)["\']?',
        'replacement': r'\1${MONGODB_URL}',
        'env_var': 'MONGODB_URL',
        'description': 'MongoDB URL'
    },
    'jwt_secret': {
        'pattern': r'(?i)(jwt[_-]?secret|secret[_-]?key\s*[=:]\s*["\']?)([a-zA-Z0-9+/=]{32,})["\']?',
        'replacement': r'\1${JWT_SECRET}',
        'env_var': 'JWT_SECRET',
        'description': 'JWT Secret Key'
    },
    'api_key_generic': {
        'pattern': r'(?i)(api[_-]?key\s*[=:]\s*["\']?)([a-zA-Z0-9]{32,})["\']?',
        'replacement': r'\1${API_KEY}',
        'env_var': 'API_KEY',
        'description': 'Generic API Key'
    },
    'slack_webhook': {
        'pattern': r'(https://hooks\.slack\.com/services/[A-Z0-9/]+)',
        'replacement': r'${SLACK_WEBHOOK_URL}',
        'env_var': 'SLACK_WEBHOOK_URL',
        'description': 'Slack Webhook URL'
    },
    'discord_webhook': {
        'pattern': r'(https://discord\.com/api/webhooks/[0-9]+/[a-zA-Z0-9-_]+)',
        'replacement': r'${DISCORD_WEBHOOK_URL}',
        'env_var': 'DISCORD_WEBHOOK_URL',
        'description': 'Discord Webhook URL'
    }
}

class SecretScanner:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path('.')
        self.findings = []
        self.fixed_files = []
        self.env_vars = set()
        
    def get_files_to_scan(self) -> List[Path]:
        """Get list of files to scan for secrets."""
        file_patterns = [
            '**/*.py', '**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx',
            '**/*.yml', '**/*.yaml', '**/*.json', '**/*.env*', 
            '**/*.conf', '**/*.config', '**/*.ini', '**/*.toml',
            '**/*.sh', '**/*.bash', '**/*.zsh'
        ]
        
        exclude_patterns = [
            '.git/', 'node_modules/', '__pycache__/', '.venv/', 'venv/',
            'dist/', 'build/', '.next/', 'coverage/', '.pytest_cache/',
            '*.min.js', '*.min.css', 'package-lock.json', 'yarn.lock'
        ]
        
        files_to_scan = []
        for pattern in file_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.project_root)
                    if not any(exc in str(rel_path) for exc in exclude_patterns):
                        files_to_scan.append(file_path)
        
        return files_to_scan
    
    def scan_file_for_secrets(self, file_path: Path) -> List[Tuple[str, Dict]]:
        """Scan a single file for secret patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            return []  # Skip binary files or files we can't read
        
        findings = []
        for secret_type, config in SECRET_PATTERNS.items():
            matches = re.finditer(config['pattern'], content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                findings.append((secret_type, {
                    'match': match,
                    'config': config,
                    'line_num': line_num,
                    'file_path': file_path,
                    'matched_text': match.group(2) if len(match.groups()) >= 2 else match.group()
                }))
        
        return findings
    
    def fix_secrets_in_file(self, file_path: Path, findings: List[Tuple[str, Dict]]) -> bool:
        """Fix secrets in a file by replacing with environment variables."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            return False
        
        original_content = content
        fixed_any = False
        
        # Sort findings by position (reverse order to avoid position shifts)
        findings.sort(key=lambda x: x[1]['match'].start(), reverse=True)
        
        for secret_type, finding in findings:
            match = finding['match']
            config = finding['config']
            
            # Replace the secret with environment variable reference
            replacement = config['replacement']
            content = content[:match.start()] + \
                     re.sub(config['pattern'], replacement, match.group()) + \
                     content[match.end():]
            fixed_any = True
            self.env_vars.add(config['env_var'])
        
        if fixed_any:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.fixed_files.append(file_path)
        
        return fixed_any
    
    def create_env_template(self) -> None:
        """Create .env.example with detected environment variables."""
        if not self.env_vars:
            return
            
        env_example_path = self.project_root / '.env.example'
        
        # Read existing content if file exists
        existing_vars = set()
        existing_content = ""
        if env_example_path.exists():
            try:
                with open(env_example_path, 'r') as f:
                    existing_content = f.read()
                    # Extract existing variable names
                    for line in existing_content.split('\n'):
                        if '=' in line and not line.strip().startswith('#'):
                            var_name = line.split('=')[0].strip()
                            existing_vars.add(var_name)
            except:
                pass
        
        # Add header if file is new
        if not existing_content:
            content = "# Environment Variables Template\n"
            content += "# Copy this file to .env and fill in your actual values\n"
            content += "# Generated by secret scanner\n\n"
        else:
            content = existing_content.rstrip() + "\n\n# Added by secret scanner\n"
        
        # Add new variables
        new_vars = self.env_vars - existing_vars
        for var in sorted(new_vars):
            # Find the description for this variable
            description = "Secret value"
            for config in SECRET_PATTERNS.values():
                if config['env_var'] == var:
                    description = config['description']
                    break
            
            content += f"# {description}\n"
            content += f"{var}=your_{var.lower()}_here\n\n"
        
        if new_vars:
            # Write content to file without logging sensitive information
            try:
                with open(env_example_path, 'w') as f:
                    f.write(content)
                print(f"📝 Updated {env_example_path} with {len(new_vars)} new environment variables")
            except Exception as e:
                print(f"❌ Error updating {env_example_path}: {str(e)}")
    
    def scan_project(self) -> Dict:
        """Scan the entire project for secrets."""
        print("🔍 Scanning project for secrets...")
        
        files_to_scan = self.get_files_to_scan()
        print(f"📁 Scanning {len(files_to_scan)} files...")
        
        all_findings = []
        files_with_secrets = []
        
        for file_path in files_to_scan:
            findings = self.scan_file_for_secrets(file_path)
            if findings:
                all_findings.extend(findings)
                files_with_secrets.append(file_path)
                
                rel_path = file_path.relative_to(self.project_root)
                print(f"🚨 Found {len(findings)} potential secrets in {rel_path}")
                
                for secret_type, finding in findings:
                    config = finding['config']
                    line_num = finding['line_num']
                    print(f"  - {config['description']} on line {line_num}")
        
        self.findings = all_findings
        
        return {
            'total_files_scanned': len(files_to_scan),
            'files_with_secrets': len(files_with_secrets),
            'total_secrets_found': len(all_findings),
            'secret_types': list(set(finding[0] for finding in all_findings)),
            'files_with_secrets_list': files_with_secrets
        }
    
    def fix_all_secrets(self) -> Dict:
        """Fix all detected secrets."""
        if not self.findings:
            return {'files_fixed': 0, 'secrets_fixed': 0}
        
        print("🔧 Fixing detected secrets...")
        
        # Group findings by file
        files_to_fix = {}
        for secret_type, finding in self.findings:
            file_path = finding['file_path']
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append((secret_type, finding))
        
        total_fixed = 0
        for file_path, findings in files_to_fix.items():
            rel_path = file_path.relative_to(self.project_root)
            if self.fix_secrets_in_file(file_path, findings):
                print(f"✅ Fixed {len(findings)} secrets in {rel_path}")
                total_fixed += len(findings)
        
        # Create/update .env.example
        self.create_env_template()
        
        return {
            'files_fixed': len(self.fixed_files),
            'secrets_fixed': total_fixed,
            'env_vars_added': len(self.env_vars)
        }
    
    def generate_report(self, scan_results: Dict, fix_results: Dict = None) -> None:
        """Generate a comprehensive report without logging sensitive information."""
        print(f"\n📊 Secret Scanning Report")
        print("=" * 50)
        print(f"Files scanned: {scan_results['total_files_scanned']}")
        print(f"Files with secrets: {scan_results['files_with_secrets']}")
        print(f"Total secrets found: {scan_results['total_secrets_found']}")
        
        if scan_results['secret_types']:
            print(f"\nSecret types detected:")
            for secret_type in scan_results['secret_types']:
                config = SECRET_PATTERNS.get(secret_type, {})
                description = config.get('description', 'Unknown secret type')
                # Only log the description, never the actual pattern or type
                print(f"  • {description}")
        
        if fix_results:
            print(f"\n🔧 Fix Results:")
            # Only log counts, never specific details about what was fixed
            print(f"Files fixed: {fix_results.get('files_fixed', 0)}")
            print(f"Secrets fixed: {fix_results.get('secrets_fixed', 0)}")
            print(f"Environment variables added: {fix_results.get('env_vars_added', 0)}")
        
        if scan_results['total_secrets_found'] > 0:
            print(f"\n⚠️  Security Recommendations:")
            print(f"  1. Review all fixed files to ensure correct variable substitution")
            print(f"  2. Update your .env file with actual secret values")
            print(f"  3. Ensure .env is listed in .gitignore")
            print(f"  4. Configure secrets in your deployment environment")
            print(f"  5. Consider using a secrets management service")

def main():
    parser = argparse.ArgumentParser(description='Scan and fix secrets in project files')
    parser.add_argument('--fix', action='store_true', help='Automatically fix detected secrets')
    parser.add_argument('--check-only', action='store_true', help='Only scan and report, don\'t fix')
    parser.add_argument('--path', type=str, default='.', help='Path to project root')
    
    args = parser.parse_args()
    
    project_root = Path(args.path).resolve()
    if not project_root.exists():
        print(f"Error: Path {project_root} does not exist")
        return 1
    
    scanner = SecretScanner(project_root)
    
    # Scan for secrets
    scan_results = scanner.scan_project()
    
    fix_results = None
    if scan_results['total_secrets_found'] > 0:
        if args.fix and not args.check_only:
            fix_results = scanner.fix_all_secrets()
        elif not args.check_only:
            # Interactive mode - ask user
            response = input(f"\n🔧 Fix {scan_results['total_secrets_found']} detected secrets? (y/N): ")
            if response.lower() in ['y', 'yes']:
                fix_results = scanner.fix_all_secrets()
    
    # Generate report
    scanner.generate_report(scan_results, fix_results)
    
    # Exit with error code if secrets were found and not fixed
    if scan_results['total_secrets_found'] > 0 and not fix_results:
        print(f"\n🚫 Secrets detected! Please fix them before committing.")
        return 1
    
    if fix_results and fix_results['secrets_fixed'] > 0:
        print(f"\n✅ All secrets have been fixed!")
        print(f"   Don't forget to update your .env file with actual values.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())