#!/usr/bin/env python3
"""
Project CUA Development Environment Setup

This script automates the setup of the development environment,
including secret detection, pre-commit hooks, and project validation.

Usage:
    python scripts/setup_dev_env.py [--install-hooks] [--validate-only]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

class DevEnvironmentSetup:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path('.')
        self.hooks_installed = False
        self.validation_passed = False
        
    def check_prerequisites(self) -> bool:
        """Check if required tools are available."""
        print("🔍 Checking prerequisites...")
        
        required_tools = {
            'python3': 'Python 3.7+',
            'node': 'Node.js 18+',
            'npm': 'npm package manager',
            'git': 'Git version control'
        }
        
        missing_tools = []
        for tool, description in required_tools.items():
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {description}")
                else:
                    missing_tools.append((tool, description))
            except FileNotFoundError:
                missing_tools.append((tool, description))
        
        if missing_tools:
            print(f"\n❌ Missing required tools:")
            for tool, description in missing_tools:
                print(f"  • {description} ({tool})")
            return False
        
        print("✅ All prerequisites met!")
        return True
    
    def install_git_hooks(self) -> bool:
        """Install git hooks for secret detection."""
        print("\n🔧 Installing git hooks...")
        
        hooks_dir = self.project_root / '.git' / 'hooks'
        if not hooks_dir.exists():
            print("❌ Git repository not found (.git/hooks directory missing)")
            return False
        
        # Install pre-commit hook
        pre_commit_source = self.project_root / 'scripts' / 'pre-commit-hook.sh'
        pre_commit_target = hooks_dir / 'pre-commit'
        
        if pre_commit_source.exists():
            # Create symbolic link or copy
            try:
                if pre_commit_target.exists():
                    pre_commit_target.unlink()
                
                # Try to create symbolic link first
                try:
                    pre_commit_target.symlink_to(pre_commit_source.resolve())
                    print("  ✅ Pre-commit hook installed (symlinked)")
                except OSError:
                    # Fallback to copying
                    import shutil
                    shutil.copy2(pre_commit_source, pre_commit_target)
                    pre_commit_target.chmod(0o755)
                    print("  ✅ Pre-commit hook installed (copied)")
                
                self.hooks_installed = True
                return True
                
            except Exception as e:
                print(f"  ❌ Failed to install pre-commit hook: {e}")
                return False
        else:
            print("  ❌ Pre-commit hook source not found")
            return False
    
    def setup_environment_files(self) -> bool:
        """Setup environment configuration files."""
        print("\n📝 Setting up environment files...")
        
        # Create .env.example if it doesn't exist
        env_example = self.project_root / '.env.example'
        if not env_example.exists():
            content = """# Project CUA Environment Variables
# Copy this file to .env and fill in your actual values

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here

# Database URLs
DATABASE_URL=postgresql://user:password@localhost:5432/cua_db
REDIS_URL=redis://localhost:6379

# Application Configuration
APP_API_URL=http://localhost:8000
APP_FRONTEND_URL=http://localhost:3000
NODE_ENV=development
ENVIRONMENT=development

# Security
JWT_SECRET=your_jwt_secret_here
SECRET_KEY=your_secret_key_here

# External Services
QDRANT_URL=http://localhost:6333
NEO4J_URL=bolt://localhost:7687
E2B_ENDPOINT=https://api.e2b.dev

# CI/CD (for GitHub Actions)
GCP_PROJECT_ID=your_gcp_project_id
CLOUDFLARE_API_TOKEN=your_cloudflare_token
SLACK_WEBHOOK_URL=your_slack_webhook_url
"""
            
            with open(env_example, 'w') as f:
                f.write(content)
            print("  ✅ Created .env.example")
        else:
            print("  ✅ .env.example already exists")
        
        # Ensure .env is in .gitignore
        gitignore = self.project_root / '.gitignore'
        env_ignored = False
        
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
                if '.env' in content:
                    env_ignored = True
        
        if not env_ignored:
            with open(gitignore, 'a') as f:
                f.write('\n# Environment files\n.env\n.env.local\n')
            print("  ✅ Added .env to .gitignore")
        else:
            print("  ✅ .env already in .gitignore")
        
        return True
    
    def validate_project_structure(self) -> bool:
        """Validate basic project structure."""
        print("\n🎯 Validating project structure...")
        
        required_dirs = [
            'frontend',
            'backend', 
            'scripts',
            '.github/workflows'
        ]
        
        required_files = [
            'README.md',
            'docker-compose.yml',
            'frontend/package.json',
            'backend/requirements.txt'
        ]
        
        issues = []
        
        # Check directories
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                print(f"  ✅ {dir_path}/")
            else:
                print(f"  ❌ {dir_path}/")
                issues.append(f"Missing directory: {dir_path}")
        
        # Check files
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.is_file():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}")
                issues.append(f"Missing file: {file_path}")
        
        if issues:
            print(f"\n⚠️  Project structure issues found:")
            for issue in issues:
                print(f"    • {issue}")
            self.validation_passed = False
            return False
        else:
            print("✅ Project structure looks good!")
            self.validation_passed = True
            return True
    
    def run_secret_scan(self) -> bool:
        """Run initial secret scan."""
        print("\n🔍 Running initial secret scan...")
        
        scanner_script = self.project_root / 'scripts' / 'secret_scanner.py'
        if not scanner_script.exists():
            print("  ❌ Secret scanner script not found")
            return False
        
        try:
            result = subprocess.run([
                sys.executable, str(scanner_script), '--check-only'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("  ✅ No secrets detected")
                return True
            else:
                print("  ⚠️  Potential secrets detected:")
                print(result.stdout)
                print("\n  🔧 Run 'python scripts/secret_scanner.py --fix' to fix them")
                return False
                
        except Exception as e:
            print(f"  ❌ Failed to run secret scanner: {e}")
            return False
    
    def setup_complete(self) -> None:
        """Display setup completion summary."""
        print("\n" + "="*60)
        print("🎉 Development Environment Setup Complete!")
        print("="*60)
        
        print(f"\n📊 Setup Summary:")
        print(f"  Git hooks installed: {'✅' if self.hooks_installed else '❌'}")
        print(f"  Project validation: {'✅' if self.validation_passed else '⚠️'}")
        print(f"  Environment files: ✅")
        
        print(f"\n📋 Next Steps:")
        print(f"  1. Copy .env.example to .env and fill in your values")
        print(f"  2. Install dependencies:")
        print(f"     cd frontend && npm install")
        print(f"     cd backend && pip install -r requirements.txt")
        print(f"  3. Start development:")
        print(f"     docker-compose up  # or")
        print(f"     npm run dev (frontend) & python backend/main.py")
        
        if not self.validation_passed:
            print(f"\n⚠️  Project structure issues need attention:")
            print(f"     Check missing directories and files above")
        
        print(f"\n🔒 Security Features:")
        print(f"  • Pre-commit hooks will scan for secrets")
        print(f"  • GitHub Actions will validate project readiness")
        print(f"  • Automatic secret detection and fixing available")
        
        print(f"\n📚 Documentation:")
        print(f"  • README.md - Project overview and setup")
        print(f"  • docs/ARCHITECTURE.md - Technical architecture")
        print(f"  • .env.example - Environment variables template")

def main():
    parser = argparse.ArgumentParser(description='Setup Project CUA development environment')
    parser.add_argument('--install-hooks', action='store_true', 
                       help='Install git hooks for secret detection')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate project structure')
    parser.add_argument('--path', type=str, default='.',
                       help='Path to project root')
    
    args = parser.parse_args()
    
    project_root = Path(args.path).resolve()
    if not project_root.exists():
        print(f"❌ Error: Path {project_root} does not exist")
        return 1
    
    setup = DevEnvironmentSetup(project_root)
    
    # Check prerequisites
    if not setup.check_prerequisites():
        return 1
    
    success = True
    
    if args.validate_only:
        # Only run validation
        if not setup.validate_project_structure():
            success = False
    else:
        # Full setup
        if not setup.setup_environment_files():
            success = False
        
        if args.install_hooks or not args.validate_only:
            if not setup.install_git_hooks():
                success = False
        
        if not setup.validate_project_structure():
            success = False
        
        if not setup.run_secret_scan():
            # Don't fail on secret scan issues, just warn
            pass
    
    setup.setup_complete()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())