# 🔐 Security Guide

This document outlines the security features and best practices implemented in Project CUA.

## 🚨 Automatic Secret Detection

Project CUA includes comprehensive secret detection to prevent accidental exposure of sensitive information.

### Features

- **Pre-commit hooks** - Automatically scan for secrets before each commit
- **CI/CD integration** - GitHub Actions validate security on every push
- **Auto-fix capability** - Automatically replace hardcoded secrets with environment variables
- **Comprehensive patterns** - Detects common secret types:
  - API keys (OpenAI, GitHub, AWS, etc.)
  - Database URLs (PostgreSQL, MySQL, MongoDB, Redis)
  - Authentication tokens and JWT secrets
  - Webhook URLs (Slack, Discord)
  - Generic API keys and secrets

### Usage

#### Scan for secrets manually:
```bash
python scripts/secret_scanner.py
```

#### Auto-fix detected secrets:
```bash
python scripts/secret_scanner.py --fix
```

#### Check-only mode (for CI):
```bash
python scripts/secret_scanner.py --check-only
```

### How it works

1. **Detection**: Scans all source files using regex patterns for common secret formats
2. **Classification**: Identifies the type of secret (API key, database URL, etc.)
3. **Auto-fix**: Replaces hardcoded secrets with environment variable references
4. **Template generation**: Updates `.env.example` with required variables

### Detected Secret Types

| Type | Pattern | Environment Variable |
|------|---------|---------------------|
| OpenAI API Key | `sk-...` | `OPENAI_API_KEY` |
| GitHub Token | `ghp_...`, `gho_...` | `GITHUB_TOKEN` |
| AWS Access Key | `AKIA...` | `AWS_ACCESS_KEY_ID` |
| AWS Secret Key | Base64-like string | `AWS_SECRET_ACCESS_KEY` |
| Database URL | `postgresql://...` | `DATABASE_URL` |
| Redis URL | `redis://...` | `REDIS_URL` |
| MongoDB URL | `mongodb://...` | `MONGODB_URL` |
| JWT Secret | Long random string | `JWT_SECRET` |
| Slack Webhook | `https://hooks.slack.com/...` | `SLACK_WEBHOOK_URL` |
| Discord Webhook | `https://discord.com/api/webhooks/...` | `DISCORD_WEBHOOK_URL` |

## 🛡️ Project Readiness Validation

Prevents CI/CD workflows from running when the project isn't ready for meaningful testing.

### Validation Levels

#### Frontend Readiness (Score: 0-100)
- ✅ `package.json` exists (+10)
- ✅ Source files present (+20)
- ✅ Next.js configuration (+15)
- ✅ TypeScript configuration (+10)
- ✅ Test files exist (+15)
- ✅ Essential config files (+5 each)

**Minimum threshold: 40 points + source files**

#### Backend Readiness (Score: 0-100)
- ✅ `requirements.txt` exists (+10)
- ✅ Source files present (+25)
- ✅ Main application file (+15)
- ✅ FastAPI usage detected (+10)
- ✅ Test files exist (+15)
- ✅ Configuration files (+5 each)

**Minimum threshold: 45 points + source files + main file**

#### Integration Readiness
- ✅ Frontend and backend ready
- ✅ Docker Compose configuration
- ✅ E2E test files
- ✅ Playwright configuration

#### Deployment Readiness
- ✅ Integration tests ready
- ✅ Dockerfiles present
- ✅ Production configurations
- ✅ Deployment scripts

### Workflow Behavior

- **Ready components**: Full CI/CD workflows run
- **Not ready**: Workflows skip with guidance
- **Mixed state**: Only ready components are tested

## 🔧 Development Environment Setup

### Quick Setup
```bash
# Setup development environment
python scripts/setup_dev_env.py --install-hooks

# Validate project structure
python scripts/setup_dev_env.py --validate-only
```

### Manual Hook Installation
```bash
# Link pre-commit hook
ln -s ../../scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 📋 Security Best Practices

### Environment Variables
1. **Never commit secrets** to version control
2. **Use `.env` files** for local development
3. **Configure secrets** in deployment environments
4. **Rotate secrets** regularly
5. **Use least privilege** principle

### Example `.env` structure:
```bash
# API Keys
OPENAI_API_KEY=sk-your-actual-key-here
GITHUB_TOKEN=ghp_your-actual-token-here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/cua_db
REDIS_URL=redis://localhost:6379

# Application
JWT_SECRET=your-long-random-secret-here
```

### CI/CD Secrets
Configure in GitHub repository settings:
- `OPENAI_API_KEY`
- `GCP_SA_KEY_STAGING`
- `GCP_SA_KEY_PRODUCTION`
- `CLOUDFLARE_API_TOKEN`
- `SLACK_WEBHOOK_URL`

### File Exclusions
The secret scanner automatically excludes:
- Binary files
- `node_modules/`
- Build artifacts (`dist/`, `build/`, `.next/`)
- Lock files (`package-lock.json`, `yarn.lock`)
- Cache directories (`.pytest_cache/`, `__pycache__/`)

## 🚨 Incident Response

### If secrets are accidentally committed:

1. **Immediate action**:
   ```bash
   # Fix current files
   python scripts/secret_scanner.py --fix
   
   # Commit fixes
   git add .
   git commit -m "🔐 fix: replace hardcoded secrets with environment variables"
   ```

2. **Rotate compromised secrets**:
   - Generate new API keys
   - Update deployment configurations
   - Invalidate old credentials

3. **Clean git history** (if needed):
   ```bash
   # For sensitive repositories, consider:
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/file' \
     --prune-empty --tag-name-filter cat -- --all
   ```

## 📊 Monitoring

### GitHub Actions Integration
- **Security scan** workflow runs on every push
- **Project readiness** validation prevents wasteful builds
- **Automated PR comments** with security status
- **Artifacts** contain detailed security reports

### Local Development
- **Pre-commit hooks** prevent secret commits
- **Development setup** script validates environment
- **Secret scanner** provides detailed reports

## 🔍 Troubleshooting

### Common Issues

**False positives in secret detection:**
```bash
# Review detected patterns
python scripts/secret_scanner.py --check-only

# Manual review and fix
# Edit files to use proper environment variables
```

**CI workflows not running:**
- Check project readiness validation results
- Ensure source files are present
- Review workflow conditions

**Git hooks not working:**
```bash
# Reinstall hooks
python scripts/setup_dev_env.py --install-hooks

# Check hook permissions
ls -la .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 📚 Additional Resources

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Docker Security](https://docs.docker.com/engine/security/)