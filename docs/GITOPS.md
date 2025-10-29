# GitOps Setup Guide

This document explains the complete GitOps setup for the RAG Trial project, including CI/CD pipelines, Docker deployment, and development workflows.

## 🎯 Overview

**Complete CI/CD pipeline with:**
- ✅ Automated testing (unit + integration)
- ✅ Code quality checks (Black, Flake8, isort, mypy)
- ✅ Security scanning (Bandit, Safety, pip-audit)
- ✅ Docker builds (multi-platform)
- ✅ Coverage reporting (PR comments + Codecov)
- ✅ Automated dependency updates (Dependabot)
- ✅ Pre-commit hooks (local validation)

---

## 📦 What Was Created

### Docker Files

```
Dockerfile                  # Multi-stage production image (~250MB)
docker-compose.yml          # Development environment (API + MySQL + ChromaDB)
.dockerignore              # Exclude unnecessary files from image
```

### GitHub Actions Workflows

```
.github/workflows/
├── tests.yml              # Tests + Coverage reporting
├── lint.yml               # Code quality (Black, Flake8, isort, mypy)
├── security.yml           # Security scanning (Bandit, Safety, pip-audit)
└── docker.yml             # Docker build & push to Docker Hub
```

### GitHub Templates

```
.github/
├── pull_request_template.md           # PR template with checklist
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml                # Structured bug reports
│   └── feature_request.yml           # Structured feature requests
└── dependabot.yml                    # Auto dependency updates
```

### Pre-commit Configuration

```
.pre-commit-config.yaml    # Local code quality hooks
```

---

## 🚀 Getting Started

### 1. Install Pre-commit Hooks

```bash
# Install pre-commit
make pre-commit-install

# Run manually on all files
make pre-commit-run

# Update hooks
make pre-commit-update
```

**What pre-commit checks:**
- Trailing whitespace
- End-of-file fixer
- YAML/JSON/TOML validation
- Large file detection
- Merge conflict detection
- Black formatting
- Flake8 linting
- isort import sorting

### 2. Setup Docker Hub (For Image Pushes)

**a) Create Docker Hub Repository**
1. Go to https://hub.docker.com
2. Create repository: `yourusername/ragtrial`
3. Make it public or private

**b) Generate Access Token**
1. Settings → Security → Access Tokens
2. Create token with Read & Write permissions
3. Copy token (shown only once)

**c) Add GitHub Secrets**
1. Repo → Settings → Secrets and variables → Actions
2. Add `DOCKERHUB_USERNAME` (your Docker Hub username)
3. Add `DOCKERHUB_TOKEN` (the token you created)

### 3. Update Repository URLs

Replace `yourusername` with your actual username in:
- `.github/workflows/docker.yml` (line 15: `DOCKER_IMAGE`)
- `Makefile` (line 304: `docker-push` command)
- `README.md` (badges and Docker pull commands)

---

## 🔄 CI/CD Pipeline Flow

### On Push/PR to `master` or `develop`

```
1. Tests Workflow
   ├─ Setup Python 3.13
   ├─ Setup MySQL test database
   ├─ Run unit tests (parallel, ~10s)
   ├─ Run integration tests (parallel, ~5s)
   ├─ Upload coverage to Codecov
   └─ Post coverage comment on PR

2. Lint Workflow
   ├─ Black formatting check
   ├─ isort import order check
   ├─ Flake8 linting
   └─ mypy type checking

3. Security Workflow
   ├─ Bandit security scan
   ├─ Safety vulnerability check
   └─ pip-audit dependency audit

4. Docker Workflow (if merged to master)
   ├─ Build multi-platform image
   ├─ Push to Docker Hub (latest, master, master-{sha})
   ├─ Update Docker Hub description
   └─ Trivy vulnerability scan
```

### On Tag `v*` (Release)

```
1. Docker Workflow
   ├─ Build multi-platform image
   ├─ Push versioned tags (v1.2.3, 1.2.3, 1.2, 1)
   └─ Trivy security scan
```

---

## 🐳 Docker Usage

### Local Development

```bash
# Build image
make docker-build

# Start all services
make docker-run

# View logs
make docker-logs        # API logs only
make docker-logs-all    # All services

# Restart services
make docker-restart

# Open shell in container
make docker-shell

# Run tests in Docker
make docker-test

# Stop services
make docker-stop

# Clean up
make docker-clean
```

### Pull from Docker Hub

```bash
# Latest stable
docker pull yourusername/ragtrial:latest

# Specific version
docker pull yourusername/ragtrial:1.2.3

# Development branch
docker pull yourusername/ragtrial:develop
```

### Production Deployment

```bash
# Run with custom config
docker run -d \
  -p 8000:8000 \
  -e APP_ENV=production \
  -e DATABASE_HOST=mysql.example.com \
  -e DATABASE_PASSWORD=secure_password \
  -e DATABASE_NAME=ragtrial_prod \
  yourusername/ragtrial:1.2.3
```

---

## 📝 Commit Message Convention

**Format:** `<gitmoji> <type>(<scope>): <description>`

**Examples:**
```bash
✨ feat(api): add batch file upload endpoint
🐛 fix(database): resolve deadlock in parallel tests
♻️ refactor(upload): remove unnecessary comments
✅ test(integration): add UUID-based uniqueness
📝 docs(readme): update test execution guide
🚀 deploy(docker): add production Dockerfile
⬆️ chore(deps): update pytest to 8.0.0
🔒 security(api): add rate limiting
```

**Common types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code refactoring
- `test` - Test changes
- `docs` - Documentation
- `chore` - Maintenance
- `perf` - Performance improvement
- `security` - Security fix

---

## 🔍 Code Quality Checks

### Local Checks (Pre-commit)

```bash
# Run all pre-commit hooks
make pre-commit-run

# Or manually
black .
isort .
flake8 .
mypy .
```

### CI Checks

All pull requests must pass:
- ✅ All tests (653 tests)
- ✅ Code coverage maintained (>89%)
- ✅ Black formatting
- ✅ Import sorting (isort)
- ✅ Linting (Flake8)
- ✅ Type hints (mypy)
- ✅ Security scans (Bandit, Safety)

---

## 📊 Coverage Reporting

### Automated PR Comments

Coverage changes are automatically posted as PR comments:

```markdown
## 📊 Coverage Report

| File | Coverage | Missing Lines |
|------|----------|---------------|
| app/modules/upload/service.py | 98% | 45, 67 |
| app/modules/file/core.py | 100% | - |
| **TOTAL** | **89%** | |

📈 Coverage increased by +2.3% vs base branch
```

### Codecov Integration

- Badge in README shows current coverage
- Detailed reports at https://codecov.io/gh/yourusername/ragtrial
- Coverage trends over time

---

## 🔐 Security Scanning

### Weekly Automated Scans

Every Monday at 9:00 AM:
- Bandit (Python security linter)
- Safety (dependency vulnerability check)
- pip-audit (package audit)

### Docker Image Scans

Every image pushed to Docker Hub is scanned with Trivy:
- Vulnerability detection
- Results uploaded to GitHub Security

---

## 🤖 Dependabot

### Automated Dependency Updates

**Weekly updates (Monday 9:00 AM):**
- Python packages (`requirements.txt`)
- GitHub Actions versions

**Configuration:**
- Max 10 PRs open at once
- Auto-labeled: `dependencies`, `python`/`ci`
- Commit prefix: `⬆️`

### Reviewing Dependabot PRs

```bash
# Check what changed
git diff main..dependabot/pip/pytest-8.0.0

# Ensure tests pass in CI
# Merge if all checks pass
```

---

## 🎯 Release Process

### Creating a Release

```bash
# 1. Update version in code
git checkout -b release/v1.2.3

# 2. Update CHANGELOG (if exists)
# 3. Commit and push
git commit -am "🚀 release: v1.2.3"
git push origin release/v1.2.3

# 4. Create PR and merge to master

# 5. Tag the release
git checkout master
git pull origin master
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

### Automatic Actions on Tag

When `v1.2.3` tag is pushed:
1. Docker images built for all platforms
2. Images pushed with tags:
   - `yourusername/ragtrial:1.2.3`
   - `yourusername/ragtrial:1.2`
   - `yourusername/ragtrial:1`
   - `yourusername/ragtrial:v1.2.3`
3. Trivy security scan
4. GitHub Release created (manually or via workflow)

---

## 📚 Additional Resources

### Documentation

- [tests/README.md](../tests/README.md) - Test infrastructure
- [README.md](../README.md) - Main project documentation
- [PROVIDERS.md](PROVIDERS.md) - Provider switching guide

### External Links

- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com)
- [pre-commit](https://pre-commit.com)
- [Codecov](https://codecov.io)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)

---

## ❓ Troubleshooting

### Pre-commit Hooks Failing

```bash
# Update hooks
make pre-commit-update

# Run manually to see errors
make pre-commit-run

# Fix formatting issues
black .
isort .
```

### Docker Build Fails

```bash
# Clean Docker cache
make docker-clean

# Rebuild without cache
docker build --no-cache -t ragtrial:local .
```

### CI Tests Failing

```bash
# Run tests locally
make test
make test-integration

# Check MySQL is running (for integration tests)
mysql -h localhost -u root -p

# View detailed test output
pytest -vvs
```

### Docker Push Authentication

```bash
# Login manually
docker login

# Verify credentials
docker logout
docker login -u yourusername
```

---

## ✅ Summary

**Complete GitOps setup includes:**
- ✅ 4 GitHub Actions workflows
- ✅ 2 issue templates
- ✅ 1 PR template
- ✅ Dependabot configuration
- ✅ Pre-commit hooks
- ✅ Docker multi-stage build
- ✅ Docker Compose development environment
- ✅ Makefile automation (16 new commands)
- ✅ Updated README with badges and Docker docs

**All tests passing:** 653 tests (632 unit + 21 integration) in ~16s

**Ready for production deployment! 🚀**

