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
- Smart tagging: branch hash for PRs, commit SHA for master
- Automatic cleanup to keep Docker Hub clean
- Reduces CI/CD time by 70% (no package installation)

### GitHub Actions Workflow (Single Unified Pipeline)

```
.github/workflows/
└── ci.yml                 # Single unified CI pipeline with job dependencies
```

**Workflow Architecture:**
- **Single workflow** with 5 stages and 7 jobs
- **Job-level dependencies** using `needs:` keyword
- **Parallel execution** where possible
- **Works on ALL branches and PRs** (no `workflow_run` limitations!)
- **SHA-specific tags** prevent race conditions between multiple PRs

**Job Dependencies (Parent-Child Pattern):**
```
Stage 1: Build Base Image
   └─> build-base-image (builds & pushes sanjibdevnath/ragtrial-base:<sha>)
       │
       ├──> Stage 2: Parallel Quality Checks (no dependencies)
       │    ├─> lint (Black, Flake8, isort)
       │    └─> security (Bandit, Safety, pip-audit)
       │
       └──> Stage 3: Tests (depends on base image)
            ├─> unit-tests (uses base image container)
            └─> integration-tests (uses base image container)
            │
            └──> Stage 4: Docker Build (depends on tests)
                 └─> docker-build (builds & pushes app image)
                     │
                     └──> Stage 5: Security Scan (depends on docker)
                          └─> docker-security-scan (Trivy scan)

✅ Lint & Security run in parallel (instant feedback!)
✅ Tests wait for base image (uses pre-built deps)
✅ Docker build waits for tests (ensures quality)
✅ Works on PRs from feature branches (no workflow_run issues!)
✅ Total time: ~8-12 minutes (with parallelization)
```

### Docker Image Tagging Strategy

**Smart Tagging for Efficient CI/CD:**

| Scenario | Base Image Tag | App Image Tag | Behavior |
|----------|----------------|---------------|----------|
| **PR Commits** | `br-abc123` (branch hash) | Not pushed (build-only) | All commits in same PR reuse same base image |
| **Master Commits** | `SHA` (full commit SHA) | `SHA` + `latest` | New image for each commit |

**Benefits:**
- ✅ **PR Efficiency**: All commits in a PR reuse the same base image (no rebuild unless deps change)
- ✅ **No Race Conditions**: Branch hashes isolate PRs from each other
- ✅ **Reproducibility**: Master builds use commit SHA for exact versioning
- ✅ **Fast CI**: Base image only builds once per PR (not per commit)

### Automated Docker Hub Cleanup

**Two cleanup workflows keep Docker Hub clean:**

#### 1. `.github/workflows/pr-cleanup.yml` - On PR Close/Merge
```yaml
Trigger: pull_request [closed]
Action:  Delete ALL branch-hash images (br-abc123) for that PR
Result:  Docker Hub cleaned immediately after PR merge
```

#### 2. `.github/workflows/ci.yml` - After Master Build
```yaml
Job:     cleanup-images (runs after docker-build on master)
Action:  Keep last 5 SHA-tagged images, delete older ones
Result:  Docker Hub maintains only recent versions
```

**Retention Policy:**
| Image Type | Tag Pattern | Keep Count | When Deleted |
|------------|-------------|------------|--------------|
| Base (PR) | `br-abc123` | 3 per branch | All deleted when PR closes |
| Base (Master) | `SHA` | 5 | After 5 newer commits |
| App (Master) | `SHA` | 5 | After 5 newer commits |
| App (Master) | `latest` | 1 | Always kept (rolling) |

**Cleanup Script:**
```bash
# Manual cleanup (dry-run by default if using dockerenv.toml)
./scripts/cleanup_docker_images.sh ragtrial-base

# Delete specific branch images
./scripts/cleanup_docker_images.sh ragtrial-base delete-branch br-abc123
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

### Single Unified Workflow (Parent-Child Jobs)

**On Push/PR to any branch:**

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Build Base Image (Foundation)                     │
├─────────────────────────────────────────────────────────────┤
│ Job: build-base-image (~2-5 min, cached if unchanged)      │
│   ├─ Check if image exists (docker manifest)               │
│   ├─ Skip build if SHA-tagged image exists                 │
│   └─ Build & push sanjibdevnath/ragtrial-base:<sha>        │
└─────────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┴──────────────┐
         ▼                               ▼
┌─────────────────────┐   ┌──────────────────────────────┐
│ Stage 2: Quality    │   │ Stage 3: Tests (needs base)  │
│ (Parallel - no deps)│   │ (Parallel within stage)      │
├─────────────────────┤   ├──────────────────────────────┤
│ Job: lint (~30s)    │   │ Job: unit-tests (~10s)       │
│  ├─ Black           │   │  ├─ Container: base:<sha>    │
│  ├─ isort           │   │  ├─ 632 tests                │
│  └─ Flake8          │   │  ├─ Coverage to Codecov      │
│                     │   │  └─ PR comment               │
│ Job: security (~45s)│   │                              │
│  ├─ Bandit          │   │ Job: integration-tests (~5s) │
│  ├─ Safety          │   │  ├─ Container: base:<sha>    │
│  └─ pip-audit       │   │  ├─ MySQL service            │
└─────────────────────┘   │  └─ 21 tests                 │
                          └──────────────────────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │ Stage 4: Docker Build        │
                          │ (needs: [unit-tests,         │
                          │          integration-tests]) │
                          ├──────────────────────────────┤
                          │ Job: docker-build (~5-8 min) │
                          │  ├─ Multi-platform (master)  │
                          │  ├─ Single platform (PRs)    │
                          │  ├─ Push (master only)       │
                          │  └─ Tags: <sha>, latest      │
                          └──────────────────────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │ Stage 5: Security Scan       │
                          │ (needs: docker-build)        │
                          │ (master only)                │
                          ├──────────────────────────────┤
                          │ Job: docker-security-scan    │
                          │  ├─ Trivy scan               │
                          │  └─ Upload to GitHub Security│
                          └──────────────────────────────┘
```

**Key Benefits:**
- ✅ **Parallel execution**: Lint & security run immediately
- ✅ **Sequential where needed**: Tests wait for base, docker waits for tests
- ✅ **Works on all branches**: No `workflow_run` limitations
- ✅ **Fast feedback**: Quality checks in <1 min
- ✅ **Safe releases**: Docker only builds after tests pass

### ⚡ Performance Optimizations

**Workflow Cancellation:**
- All workflows have `concurrency` control configured
- When a new commit is pushed, previous in-progress runs are automatically cancelled
- Saves CI/CD minutes and provides faster feedback
- Applies to: Tests, Lint, Security, Docker builds, Base image builds

**Docker Build Optimization:**
- **Pull Requests (PRs):**
  - Build only for `linux/amd64` (single platform) → **~50% faster**
  - Use cache `mode=min` (cache only final image) → **~40% faster cache export**
  - Total PR build time: **~5-8 minutes** (vs 20-25 minutes for multi-platform)
- **Master/Develop branches:**
  - Build for `linux/amd64,linux/arm64` (multi-platform)
  - Use cache `mode=max` (cache all layers for better reuse)
  - Full multi-platform build: **~15-20 minutes**

**Why this matters:**
- PRs get much faster feedback (8 min vs 25 min)
- Production builds are still multi-platform and optimized
- Reduced GitHub Actions minutes usage by ~60% for PRs

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
- ✅ Flake8 linting (`make flake8-check`)

**Non-blocking (reports only):**
- ⚠️ Security scans (Bandit, Safety, pip-audit)

**Note:** All code quality checks (Black, isort, Flake8) are now enforcing - PRs cannot merge with violations.

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
- ✅ **1 unified CI pipeline** (with parent-child job dependencies)
- ✅ 2 issue templates
- ✅ 1 PR template
- ✅ Dependabot configuration
- ✅ Pre-commit hooks
- ✅ Docker multi-stage build
- ✅ Docker Compose development environment
- ✅ Makefile automation (60+ commands)
- ✅ Updated README with badges and Docker docs

**Workflow Architecture:**
- **Single workflow, 5 stages, 7 jobs**
- **Parent-child dependencies** using `needs:` keyword
- **Works on all branches and PRs** (no `workflow_run` limitations!)
- **Total execution time:** ~8-12 minutes (with parallelization)

**All tests passing:** 653 tests (632 unit + 21 integration) in ~16s

**Ready for production deployment! 🚀**

