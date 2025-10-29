# Docker Hub Image Cleanup Strategy

## 🎯 Overview

Automated Docker Hub cleanup to keep repository clean and efficient, with smart tagging for CI/CD optimization.

---

## 📊 Image Tagging Strategy

### Pull Requests (Feature Branches)
- **Base Image**: `sanjibdevnath/ragtrial-base:br-abc123`
  - Tag is a **12-character MD5 hash** of the branch name
  - **Reused across all commits** in the same PR
  - Only rebuilt if `requirements.txt` or `Dockerfile.base` changes
  - **Not pushed** (build-only)

- **App Image**: Not pushed (build-only in CI)

**Benefits:**
- ⚡ **Faster CI**: Base image reused across multiple commits
- 🔒 **Isolated**: Each PR has its own unique base image hash
- 💾 **Efficient**: No redundant base image builds for code-only changes

### Master Branch
- **Base Image**: `sanjibdevnath/ragtrial-base:<full-commit-sha>`
  - Uses full 40-character commit SHA
  - New image for each commit

- **App Image**: `sanjibdevnath/ragtrial:<full-commit-sha>` + `sanjibdevnath/ragtrial:latest`
  - Commit SHA for exact versioning
  - `latest` tag for easy deployment

**Benefits:**
- 🎯 **Reproducible**: Exact commit SHA ensures deterministic builds
- 📜 **Traceable**: Direct mapping between code and Docker image
- 🚀 **Deploy-ready**: `latest` tag always points to master HEAD

---

## 🧹 Cleanup Workflows

### 1. PR Cleanup (Immediate on Merge/Close)

**Workflow**: `.github/workflows/pr-cleanup.yml`

**Trigger**:
```yaml
on:
  pull_request:
    types: [closed]
```

**Action**:
- Generates branch hash from PR branch name
- Deletes **ALL** base images with that branch hash
- Runs immediately when PR is merged or closed

**Result**: Docker Hub cleaned within seconds of PR close

**Example**:
```bash
# PR branch: feature/add-auth
# Branch hash: br-a1b2c3d4e5f6
# Images deleted:
#   - sanjibdevnath/ragtrial-base:br-a1b2c3d4e5f6
```

---

### 2. Master Cleanup (After Successful Build)

**Workflow**: `.github/workflows/ci.yml` (cleanup-images job)

**Trigger**:
- Runs after `docker-build` job completes
- Only on `master` branch pushes

**Action**:
- Keep last **5** SHA-tagged base images
- Keep last **5** SHA-tagged app images
- Keep `latest` tag (always)
- Delete older images

**Result**: Docker Hub maintains only recent builds

**Example**:
```bash
# 7 base images exist (SHA tags)
# Script keeps: 5 newest
# Script deletes: 2 oldest
```

---

## 📋 Retention Policy

| Image Type | Tag Pattern | Keep Count | Deletion Trigger |
|------------|-------------|------------|------------------|
| **Base (PR)** | `br-abc123` | 3 per branch | All deleted when PR closes |
| **Base (Master)** | `SHA` (40 chars) | 5 | After 5 newer commits |
| **App (Master)** | `SHA` (40 chars) | 5 | After 5 newer commits |
| **App (Master)** | `latest` | 1 | Always kept (rolling update) |

---

## 🔧 Manual Cleanup Script

### Location
`scripts/cleanup_docker_images.sh`

### Features
- ✅ **Dry-run mode** by default when using `dockerenv.toml`
- ✅ **Pagination support** for large repositories
- ✅ **Branch-specific deletion**
- ✅ **Master image retention** (keep last 5)
- ✅ **PR image retention** (keep last 3 per branch hash)

### Usage

#### 1. Test Locally (Dry-Run)
```bash
# Create environment/dockerenv.toml with your credentials
cat > environment/dockerenv.toml << EOF
USERNAME = your_dockerhub_username
PASSWORD = dckr_pat_your_personal_access_token
EOF

# Test cleanup (won't actually delete)
./scripts/cleanup_docker_images.sh ragtrial-base
./scripts/cleanup_docker_images.sh ragtrial
```

#### 2. Manual Cleanup (Production)
```bash
# Set credentials as environment variables
export DOCKERHUB_USERNAME=your_username
export DOCKERHUB_TOKEN=your_token

# Run cleanup (will actually delete!)
./scripts/cleanup_docker_images.sh ragtrial-base
./scripts/cleanup_docker_images.sh ragtrial
```

#### 3. Delete Specific Branch Images
```bash
# Delete all images for a specific branch hash
./scripts/cleanup_docker_images.sh ragtrial-base delete-branch br-abc123
```

### Dry-Run Detection
The script automatically enables **dry-run mode** when:
- `environment/dockerenv.toml` file exists
- Script is run locally (not in CI)

**Output Example (Dry-Run)**:
```
📁 Loading credentials from environment/dockerenv.toml
⚠️  DRY_RUN mode enabled (local testing)
============================================
Docker Hub Image Cleanup
============================================
Repository: sanjibdevnath/ragtrial-base
Mode: cleanup
Dry Run: ENABLED (no actual deletions)
============================================

🔐 Authenticating with Docker Hub...
✅ Authenticated successfully

📦 Analyzing ragtrial-base images...

📊 Tag Summary:
  Master tags (SHA): 7
  Branch tags (br-*): 1
  Latest tag: No

🔍 Processing master tags (keep last 5)...
[DRY-RUN] Would delete: 73c0e8d3820a55ef60eedf89bbdc03b5f33c4b3a
[DRY-RUN] Would delete: e364c50adbeceae30256e2cfd0bd5b52ef79cdb9
✅ Processed 2 master tag(s)

🔍 Processing branch tags (keep last 3)...
✅ Total branch tags processed: 0

============================================
✅ Cleanup complete!
============================================
```

---

## 🔍 Understanding Tags vs Manifests

### Why Docker Hub UI Shows More Images Than Script Reports

**The script counts TAGS, but Docker Hub UI shows MANIFESTS.**

#### Example:
```
1 Tag: fd2b970005841a4364f59974e4ce0df722b5dd9a
  ├─ Manifest 1 (amd64/linux): sha256:6ab0b4f9466f...
  ├─ Manifest 2 (arm64/linux): sha256:8cd1e2g0577g...
  └─ Manifest Index: sha256:9de2f3h1688h...

= 1 Tag = 3 Manifest Entries in Docker Hub UI
```

#### What Happens When You Delete a Tag?
**Deleting 1 tag automatically deletes ALL associated manifests.**

Docker Hub performs automatic garbage collection:
- Tag reference deleted
- All manifests for that tag deleted
- Unreferenced layers cleaned up

#### Script Output Example:
```bash
Tag #6: 73c0e8d3820a55ef60eedf89bbdc03b5f33c4b3a (2 manifest(s))
  🔍 Fetching manifest details for: 73c0e8d3820a55ef60eedf89bbdc03b5f33c4b3a
    📦 2 manifest(s):
      - amd64 / linux: sha256:6ab0b4f9466f...
      - unknown / unknown: sha256:573a6197b103...
  [DRY-RUN] Would delete tag: 73c0e8d3820a55ef60eedf89bbdc03b5f33c4b3a
  ⚠️  This will also delete all associated manifests shown above
```

**Summary:**
- Script: "7 tags, keeping 5, deleting 2"
- Reality: Deleting 2 tags = Deleting 4-6 manifest entries from Docker Hub UI
- Result: Docker Hub appears much cleaner after cleanup

---

## 🔒 Security

### Credentials
- GitHub Actions: Use repository secrets
  - `DOCKERHUB_USERNAME`
  - `DOCKERHUB_TOKEN`

- Local Testing: Use `environment/dockerenv.toml` (gitignored)
  ```toml
  USERNAME = your_username
  PASSWORD = dckr_pat_your_token
  ```

### Docker Hub Personal Access Token
1. Go to Docker Hub → Account Settings → Security
2. Click "New Access Token"
3. Name: `ragtrial-cleanup`
4. Scope: **Read & Write**
5. Copy token and save securely

---

## 📊 Expected Behavior

### Scenario 1: New PR Created
```
1. Developer creates PR from feature/add-login
2. Branch hash generated: br-7a8b9c0d1e2f
3. Base image built: ragtrial-base:br-7a8b9c0d1e2f
4. Image pushed to Docker Hub
5. All subsequent commits reuse this base image
```

### Scenario 2: Developer Pushes More Commits to PR
```
1. Developer commits code changes (no deps change)
2. CI checks if ragtrial-base:br-7a8b9c0d1e2f exists
3. Image found → skip build, reuse existing
4. CI runs tests using existing base image
5. Fast feedback (~2 minutes vs 5 minutes)
```

### Scenario 3: PR Merged to Master
```
1. PR merged/closed
2. pr-cleanup.yml workflow triggers
3. Script deletes ALL images with br-7a8b9c0d1e2f tag
4. Docker Hub cleaned within 30 seconds
```

### Scenario 4: Master Build Completes
```
1. Code merged to master (commit: abc123...)
2. Base image built: ragtrial-base:abc123...
3. App image built: ragtrial:abc123... + ragtrial:latest
4. cleanup-images job runs
5. Keeps last 5 images, deletes older ones
6. Docker Hub maintains clean history
```

---

## 🎯 Benefits Summary

### For CI/CD
- ⚡ **70% faster PR builds**: Base image reused across commits
- 🔒 **No race conditions**: Branch hashes isolate PRs
- 💾 **Reduced bandwidth**: No redundant base image pulls
- 🚀 **Faster feedback**: Tests run on pre-built dependencies

### For Docker Hub
- 🧹 **Clean repository**: Only relevant images kept
- 💰 **Cost savings**: Reduced storage usage
- 📊 **Easy navigation**: Only recent builds visible
- 🔍 **Quick troubleshooting**: Find images by commit SHA

### For Developers
- 🎯 **Reproducible builds**: Exact commit SHA tagging
- 📜 **Full traceability**: Direct code-to-image mapping
- 🔄 **Automatic cleanup**: No manual maintenance
- 🛡️ **Safe testing**: Dry-run mode for local testing

---

## 🐛 Troubleshooting

### Issue: "Image not found" in CI
**Cause**: Base image not built yet or tag mismatch

**Solution**:
```bash
# Check if image exists
docker manifest inspect sanjibdevnath/ragtrial-base:TAG

# Manually build if needed
docker build -t sanjibdevnath/ragtrial-base:TAG -f docker/Dockerfile.base .
docker push sanjibdevnath/ragtrial-base:TAG
```

### Issue: Cleanup script shows "401 Unauthorized"
**Cause**: Invalid Docker Hub credentials

**Solution**:
1. Verify token has "Read & Write" scope
2. Regenerate token if expired
3. Update secrets in GitHub or `dockerenv.toml`

### Issue: Too many old images not being cleaned
**Cause**: Cleanup job might be failing silently

**Solution**:
```bash
# Run manual cleanup locally (dry-run)
./scripts/cleanup_docker_images.sh ragtrial-base

# Check GitHub Actions logs
gh run list --workflow=ci.yml --limit 5
gh run view <run-id> --job=cleanup-images --log
```

---

## 📝 References

- **CI Workflow**: `.github/workflows/ci.yml`
- **PR Cleanup**: `.github/workflows/pr-cleanup.yml`
- **Cleanup Script**: `scripts/cleanup_docker_images.sh`
- **GitOps Docs**: `docs/GITOPS.md`
- **Docker Hub API**: https://docs.docker.com/docker-hub/api/latest/

