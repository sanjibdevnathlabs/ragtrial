# Test Suite Documentation

## Database Isolation Strategy

### Separate Databases per Environment

**IMPORTANT:** Tests use a **dedicated test database** that is completely separate from development data.

| Environment | Database Name | Usage | Safe to Wipe? |
|-------------|---------------|-------|---------------|
| **Test** | `test_ragtrial` | Automated tests only | ✅ YES |
| **Development** | `ragtrial` | Developer data | ❌ NO |
| **Production** | `ragtrial` | Production data | ❌ NO |

### How It Works

#### Environment Configuration

```toml
# environment/test.toml
[database.mysql.write]
database = "test_ragtrial"    # ← Dedicated test database

# environment/dev.toml
[database.mysql.write]
database = "ragtrial"          # ← Development database
```

#### Test Execution

```bash
# Integration tests automatically use test database
APP_ENV=test make test-integration

# This connects to: test_ragtrial (NOT ragtrial)
```

#### Cleanup After Each Test

```python
@pytest.fixture(autouse=True)
def clean_test_database():
    """
    Delete all data from test_ragtrial after each test.
    
    SAFE because:
    - test_ragtrial is ONLY for automated tests
    - Developers NEVER store data in test_ragtrial
    - Development data in ragtrial is NEVER touched
    """
    yield  # Run test
    
    # Delete all test data (safe - test database only)
    conn.execute(text("DELETE FROM files"))
    conn.commit()
```

---

## Safety Guarantees

### ✅ What's Safe

- Running `make test-integration` - uses `test_ragtrial`
- Deleting all data from `test_ragtrial` - it's test-only
- Running tests in parallel - each has own transaction/connection

### ❌ What's Protected

- Developer data in `ragtrial` database - NEVER touched by tests
- Production data - completely separate
- Manual data you create with `APP_ENV=dev`

---

## Test Database Setup

### Initial Setup

```bash
# Create test database and run migrations
make setup-test-db

# This creates: test_ragtrial
# And runs: migrations on test_ragtrial
```

### What Gets Created

```sql
-- MySQL command executed:
CREATE DATABASE IF NOT EXISTS test_ragtrial 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- Then migrations run:
CREATE TABLE files (...);
-- ... other tables
```

---

## Cleanup Strategy

### After Each Test

```python
# Automatic cleanup fixture runs after every integration test
DELETE FROM files;  -- Remove test data
```

**Why DELETE and not TRUNCATE?**
- ✅ Faster for small datasets
- ✅ Works with foreign keys
- ✅ Doesn't reset auto-increment counters (cleaner for parallel tests)

### After Test Session

```bash
# Storage directories cleaned automatically
rm -rf storage/chroma_test/
rm -rf storage/test_documents/
```

**Database is NOT wiped** - schema remains for next test run.

---

## Parallel Test Execution

### MySQL vs SQLite

| Database | Parallel Tests | Why? |
|----------|----------------|------|
| **MySQL** | ✅ YES | No locking issues, proper concurrency |
| **SQLite** | ❌ NO | File-based, locks on writes |

### How Parallel Works

```bash
# Each test worker gets its own connection
pytest -n auto  # Creates 8-12 workers (CPU cores)

Worker 1 → Connection 1 → Transaction 1
Worker 2 → Connection 2 → Transaction 2
...
Worker N → Connection N → Transaction N
```

Each worker:
1. Connects to `test_ragtrial`
2. Runs test in isolation
3. Commits data
4. Cleanup fixture deletes data
5. Next test starts clean

### Preventing Race Conditions

**Problem:** Multiple workers inserting files with same checksum → deadlocks

**Solution:** UUID-based uniqueness for test data

```python
# ❌ BAD - Same checksum in parallel tests
files = {"file": ("test.pdf", b"test content", "application/pdf")}
# → All workers get same SHA-256 → UNIQUE constraint conflict

# ✅ GOOD - Unique content per test
import uuid
content = f"test content {uuid.uuid4()}".encode()
files = {"file": ("test.pdf", content, "application/pdf")}
# → Each worker gets different SHA-256 → No conflicts
```

**Key Points:**
- `uuid.uuid4()` guarantees uniqueness (collision probability: ~1 in 10³⁶)
- Test fixtures generate unique checksums per test run
- Upload tests generate unique content per request
- No SELECT FOR UPDATE needed - UNIQUE constraint handles atomicity

### Performance Impact

| Execution Mode | Time | Tests | Speed |
|----------------|------|-------|-------|
| Sequential | ~15s | 21 | 1x |
| Parallel (-n auto) | ~5s | 21 | **3x faster** |

---

## Developer Workflow

### Running Tests Locally

```bash
# Unit tests (parallel, no DB) - 630 tests, ~10s
make test

# Integration tests (parallel, MySQL) - 21 tests, ~5s
make test-integration

# All tests with coverage reports
make test           # Terminal coverage report
make test-html      # HTML coverage report (htmlcov/index.html)
```

**Total test time: ~15 seconds for 651 tests** ⚡

### Checking Which Database You're Using

```bash
# Development (your data is here)
APP_ENV=dev python scripts/some_script.py
# → Uses: ragtrial

# Testing (safe to wipe)
APP_ENV=test pytest tests/
# → Uses: test_ragtrial
```

---

## FAQ

### Q: Will tests delete my development data?

**A: No.** Tests use `test_ragtrial` database. Your development data is in `ragtrial` database.

```bash
# Your data (safe)
APP_ENV=dev → ragtrial

# Test data (wiped after tests)
APP_ENV=test → test_ragtrial
```

### Q: What if I accidentally run tests with APP_ENV=dev?

**A: Tests check environment** and will fail if `APP_ENV != test`:

```python
# In conftest.py
assert os.getenv("APP_ENV") == "test", "Tests must run with APP_ENV=test"
```

### Q: Can I manually inspect test database?

**A: Yes!**

```bash
# Connect to test database
mysql -h localhost -u root test_ragtrial

# View test data (if tests are running)
SELECT * FROM files;

# But remember: data is wiped after each test
```

### Q: How do I reset test database completely?

```bash
# Drop and recreate test database
mysql -h localhost -u root -e "DROP DATABASE test_ragtrial;"
make setup-test-db

# Or just re-run migrations
APP_ENV=test make migrate-reset
```

---

## Best Practices

### ✅ Do

- Always run tests with `APP_ENV=test`
- Use `make test-integration` (sets APP_ENV automatically)
- Trust the cleanup fixtures
- Run tests in parallel for speed

### ❌ Don't

- Manually create data in `test_ragtrial` (it gets wiped)
- Run tests with `APP_ENV=dev` (your data is at risk)
- Modify test database schema manually (use migrations)
- Commit test data to production database

---

## Troubleshooting

### Tests Fail with "Connection Refused"

```bash
# MySQL not running
brew services start mysql

# Or check status
brew services list | grep mysql
```

### Tests Fail with "Database doesn't exist"

```bash
# Create test database
make setup-test-db
```

### Tests Leave Orphaned Data

```bash
# Cleanup manually
APP_ENV=test make test-clean-db

# Or re-create database
mysql -h localhost -u root -e "DROP DATABASE test_ragtrial;"
make setup-test-db
```

### Parallel Tests Fail with Deadlocks

**Symptom:** `OperationalError: (1213, 'Deadlock found when trying to get lock')`

**Cause:** Test data has duplicate checksums causing UNIQUE constraint conflicts.

**Solution:**

```python
# ✅ Fix: Use uuid4() for unique test data
import uuid

# In fixtures
unique_id = str(uuid.uuid4())
checksum = f"test_checksum_{unique_id}"

# In test methods
content = f"test content {uuid.uuid4()}".encode()
```

**Verify fix:**
```bash
# Run integration tests 10 times - should all pass
for i in {1..10}; do make test-integration; done
```

### Parallel Tests Too Slow

```bash
# Check MySQL connection pool size
# In environment/test.toml:
pool_size = 10        # Increase for more workers
max_overflow = 20     # Increase for burst capacity
```

---

## Summary

✅ **Dedicated test database** (`test_ragtrial`)  
✅ **Automatic cleanup** after each test  
✅ **Developer data protected** (in `ragtrial`)  
✅ **Parallel execution** enabled (8-12 workers)  
✅ **UUID-based uniqueness** prevents race conditions  
✅ **Fast test runs** (~15s total for 651 tests)  
✅ **Zero flaky tests** - 100% deterministic  

**Your development data is safe!** 🎉

