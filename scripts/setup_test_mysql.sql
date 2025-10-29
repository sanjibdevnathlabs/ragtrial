-- ============================================================================
-- MySQL Test Database Setup Script
-- ============================================================================
-- Purpose: Create dedicated test database and user for automated tests
-- 
-- What this script does:
--   1. Creates test_ragtrial database (UTF-8 support)
--   2. Creates test_ragtrial user with password 'test_ragtrial'
--   3. Grants full privileges on test_ragtrial database to test user
--   4. Verifies setup with status queries
--
-- Usage:
--   mysql -u root -p < scripts/setup_test_mysql.sql
--   
--   Or with sudo (if MySQL configured that way):
--   sudo mysql < scripts/setup_test_mysql.sql
--
-- Security Note:
--   This user ONLY has access to test_ragtrial database
--   Your development database (ragtrial) remains protected
-- ============================================================================

-- Create test database with UTF-8 support
CREATE DATABASE IF NOT EXISTS test_ragtrial
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Create dedicated test user
CREATE USER IF NOT EXISTS 'test_ragtrial'@'localhost' 
  IDENTIFIED BY 'test_ragtrial';

-- Grant ALL privileges on test database ONLY
GRANT ALL PRIVILEGES ON test_ragtrial.* TO 'test_ragtrial'@'localhost';

-- Apply privilege changes immediately
FLUSH PRIVILEGES;

-- ============================================================================
-- Verification Queries
-- ============================================================================

SELECT '============================================' AS '';
SELECT 'Database Created Successfully' AS Status;
SELECT '============================================' AS '';
SHOW DATABASES LIKE 'test_ragtrial';

SELECT '' AS '';
SELECT '============================================' AS '';
SELECT 'User Created and Privileges Granted' AS Status;
SELECT '============================================' AS '';
SHOW GRANTS FOR 'test_ragtrial'@'localhost';

SELECT '' AS '';
SELECT '============================================' AS '';
SELECT 'Setup Complete!' AS Status;
SELECT '============================================' AS '';
SELECT 'Database: test_ragtrial' AS Info;
SELECT 'Username: test_ragtrial' AS Info;
SELECT 'Password: test_ragtrial' AS Info;
SELECT '============================================' AS '';

-- ============================================================================
-- Test Connection (Optional - uncomment to test)
-- ============================================================================
-- USE test_ragtrial;
-- SELECT 'Successfully connected to test_ragtrial!' AS Test;

