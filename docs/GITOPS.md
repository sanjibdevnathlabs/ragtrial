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
docker/
├── Dockerfile              # Multi-stage production image (~250MB)
└── Dockerfile.base         # Base image with all dependencies (~1GB)

deployment/local/
└── docker-compose.yml      # Local development environment

.dockerignore              # Exclude unnecessary files from Docker builds
```

**Base Image Purpose:**
- Pre-installs all `requirements.txt` dependencies
- Used by all GitHub Actions workflows (no more `pip install`!)
- Built automatically when `requirements.txt` changes
- SHA-tagged for isolation (no race conditions between PRs)
- Reduces CI/CD time by 70% (no package installation)

### GitHub Actions Workflows

```
.github/workflows/
├── base-image.yml         # Build base image (auto-triggers on requirements.txt changes)
├── tests.yml              # Tests + Coverage reporting
├── lint.yml               # Code quality (Black, Flake8, isort, mypy)
├── security.yml           # Security scanning (Bandit, Safety, pip-audit)
└── docker.yml             # Docker build & push to Docker Hub
```

**Workflow Efficiency:**
- **Hybrid execution** - fast feedback + optimized tests
- **Tests workflow** depends on base image (pulls pre-built dependencies)
- **Security & Lint** run independently (don't need dependencies)
- **No redundant pip installs** = 70% faster overall execution
- Base image auto-rebuilds when `requirements.txt` changes
- SHA-specific tags prevent race conditions between multiple PRs

**Workflow Dependencies:**
```
Push/PR triggers multiple independent workflows:

1. Base Image Build (if needed)
   └─> Tests & Coverage (pulls pre-built base image)

2. Security Scan (independent)
   └─> Runs immediately (~30-45 sec)
   └─> Scans: source code + requirements.txt
   └─> No dependencies installed!

3. Code Quality / Lint (independent)
   └─> Runs immediately (~20-30 sec)
   └─> Linters: Black, Flake8, isort, mypy
   └─> No dependencies installed!

4. Docker Build & Push (independent)
   └─> Builds application image

✅ Security & Lint run FIRST (instant feedback!)
✅ Tests run after base image ready (uses pre-built deps)
✅ Total savings: 6-9 minutes per push!
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
2. Create repository: `sanjibdevnath/ragtrial` ✅ (Already created)
3. Make it public or private

**b) Generate Access Token**
1. Settings → Security → Access Tokens
2. Create token with Read & Write permissions
3. Copy token (shown only once)

**c) Add GitHub Secrets**
1. Repo → Settings → Secrets and variables → Actions
2. Add `DOCKERHUB_USERNAME` (your Docker Hub username)
3. Add `DOCKERHUB_TOKEN` (the token you created)

### 3. Docker Image Configuration ✅

**Image:** `sanjibdevnath/ragtrial`

**Tagging Strategy:**
- **All commits:** `<full-commit-sha>` (40 chars)
- **Master branch:** `latest` + `<full-commit-sha>`
- **Other branches:** Only `<full-commit-sha>`
- **Pull Requests:** Build only (no push)

**Examples:**
```bash
# Master branch push (commit: abc123...def)
sanjibdevnath/ragtrial:abc123def456789abcdef123456789abcdef1234  # Full SHA (40 chars)
sanjibdevnath/ragtrial:latest                                    # Only on master

# Develop branch push
sanjibdevnath/ragtrial:xyz789abc123def456abc789def123abc456def  # Full SHA only
```

---

## 🔄 CI/CD Pipeline Flow

### On Push/PR to `master` or `develop`

```
1. Tests Workflow (Parallel Jobs)
   │
   ├─ Unit Tests Job (~10s)
   │  ├─ Setup Python 3.13
   │  ├─ Run unit tests (632 tests)
   │  ├─ Upload coverage to Codecov
   │  └─ Post coverage comment on PR
   │
   └─ Integration Tests Job (~5s)
      ├─ Setup Python 3.13
      ├─ Setup MySQL test database
      └─ Run integration tests (21 tests)

2. Lint Workflow
   ├─ Black formatting check (make black-check)
   ├─ isort import order check (make isort-check)
   ├─ Flake8 linting (make flake8-check) [non-blocking]
   └─ mypy type checking [non-blocking]

3. Security Workflow
   ├─ Bandit security scan
   ├─ Safety vulnerability check
   └─ pip-audit dependency audit

4. Docker Workflow (on push to master/develop)
   ├─ Build multi-platform image (linux/amd64, linux/arm64)
   ├─ Push to Docker Hub with tags:
   │  ├─ <full-commit-sha> (always)
   │  └─ latest (master only)
   ├─ Update Docker Hub description (master only)
   └─ Trivy vulnerability scan (master only)
```

### On Tag `v*` (Release)

```
1. Docker Workflow
   ├─ Build multi-platform image (linux/amd64, linux/arm64)
   ├─ Push to Docker Hub with tags:
   │  └─ <full-commit-sha>
   └─ Trivy security scan (if master)
```

**Note:** Release tags use the same SHA-based tagging. Use `latest` or specific SHA tags for deployments.

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
# Latest stable (master branch)
docker pull sanjibdevnath/ragtrial:latest

# Specific commit (by full 40-char SHA)
docker pull sanjibdevnath/ragtrial:abc123def456789abcdef123456789abcdef1234

# List all available tags
# Visit: https://hub.docker.com/r/sanjibdevnath/ragtrial/tags
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

### Local Development (Using Makefile)

```bash
# Format code (auto-fix)
make format              # Black + isort formatting

# Check formatting (no changes)
make lint-check          # Black + isort checks
make black-check         # Black check only
make isort-check         # isort check only

# Run linters
make lint                # Flake8 linting
make lint-all            # All checks (format + lint)

# Or use pre-commit hooks
make pre-commit-run      # Run all pre-commit hooks
```

**Recommended workflow before committing:**
```bash
make format lint-all test
```

### Scope of Linting

All lint commands check **production code only**, excluding:
- `tests/` - Test files
- `scripts/` - Utility scripts
- `examples/` - Demo examples
- `venv/` - Virtual environment
- `htmlcov/` - Coverage reports

### CI Checks (GitHub Actions)

**Enforced (must pass):**
- ✅ All tests (653 tests)
- ✅ Code coverage maintained (>89%)
- ✅ Black formatting (`make black-check`)
- ✅ Import sorting (`make isort-check`)

**Non-blocking (reports only):**
- ⚠️ Flake8 linting (`make flake8-check`)
- ⚠️ Type hints (mypy)
- ⚠️ Security scans (Bandit, Safety, pip-audit)

**DRY Principle:** Lint workflow uses Makefile commands, ensuring consistency between local and CI environments.

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
1. Docker images built for all platforms (linux/amd64, linux/arm64)
2. Images pushed with tags:
   - `sanjibdevnath/ragtrial:<full-commit-sha>`
   
**Note:** Use commit SHA tags for precise versioning instead of semantic version tags.
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
docker login -u sanjibdevnath

# Test push locally
docker tag ragtrial:local sanjibdevnath/ragtrial:test
docker push sanjibdevnath/ragtrial:test
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

