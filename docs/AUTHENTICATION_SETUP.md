# Authentication Setup Guide

**Last Updated:** November 2, 2025  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [JWT Secret Generation](#jwt-secret-generation)
3. [OAuth Setup](#oauth-setup)
   - [Google OAuth](#google-oauth)
   - [GitHub OAuth](#github-oauth)
4. [SMTP Configuration](#smtp-configuration)
5. [Environment Variables](#environment-variables)
6. [Testing Authentication](#testing-authentication)
7. [Security Best Practices](#security-best-practices)

---

## Overview

The RAG Trial application uses a comprehensive authentication system with:

- ✅ **JWT-based authentication** (Access Token + Refresh Token)
- ✅ **OAuth 2.0** (Google, GitHub)
- ✅ **Email verification** (required before any action)
- ✅ **Password reset** with expiring tokens
- ✅ **Multi-provider login** (local auth + social auth)

---

## JWT Secret Generation

### Why Do You Need This?

JWT (JSON Web Token) secrets are used to sign and verify authentication tokens. **Never use a weak or predictable secret in production!**

### Generate JWT Secret

#### **Option 1: Using OpenSSL (Recommended)**

```bash
# Generate a 256-bit (32 bytes) random hex string
openssl rand -hex 32
```

**Output example:**
```
a3f2c8b9e1d4f6a7b2c9d8e3f1a4b7c2d9e8f3a1b6c4d7e2f9a3b8c1d6e4f7a2
```

#### **Option 2: Using Python**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### **Option 3: Using Node.js**

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Set Environment Variable

**Linux/macOS:**
```bash
export JWT_SECRET="your-generated-secret-here"
```

**Windows (PowerShell):**
```powershell
$env:JWT_SECRET="your-generated-secret-here"
```

**Persistent (Add to `~/.bashrc` or `~/.zshrc`):**
```bash
echo 'export JWT_SECRET="your-generated-secret-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## OAuth Setup

### Google OAuth

#### **Step 1: Create Google Cloud Project**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `RAG Trial` (or your preferred name)
4. Click **"Create"**
5. Wait for project creation (~30 seconds)

#### **Step 2: Enable Google+ API**

1. In Google Cloud Console, ensure your new project is selected
2. Go to **APIs & Services** → **Library**
3. Search for **"Google+ API"** (or **"People API"**)
4. Click on it and click **"Enable"**

#### **Step 3: Configure OAuth Consent Screen**

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **"External"** (unless you have Google Workspace)
3. Click **"Create"**
4. Fill in required fields:
   - **App name:** `RAG Trial`
   - **User support email:** Your email
   - **Developer contact email:** Your email
5. Click **"Save and Continue"**
6. **Scopes:** Click **"Add or Remove Scopes"**
   - Select: `openid`
   - Select: `email`
   - Select: `profile`
7. Click **"Save and Continue"**
8. **Test users (optional):** Add your email for testing
9. Click **"Save and Continue"**

#### **Step 4: Create OAuth Credentials**

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Application type: **"Web application"**
4. Name: `RAG Trial Web Client`
5. **Authorized redirect URIs:** Click **"Add URI"**
   - Development: `http://localhost:8000/api/v1/auth/oauth/google/callback`
   - Production: `https://yourdomain.com/api/v1/auth/oauth/google/callback`
6. Click **"Create"**
7. **Copy and Save:**
   - **Client ID:** `840295341867-xxxxxxxxxxxxxxxx.apps.googleusercontent.com`
   - **Client Secret:** `GOCSPX-xxxxxxxxxxxxxxxx`

#### **Step 5: Set Environment Variables**

```bash
export GOOGLE_CLIENT_ID="your-client-id-here"
export GOOGLE_CLIENT_SECRET="your-client-secret-here"
```

#### **Step 6: Test Google OAuth**

**Test URL (Development):**
```
https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8000/api/v1/auth/oauth/google/callback&response_type=code&scope=openid%20email%20profile
```

Replace `YOUR_CLIENT_ID` with your actual client ID.

**Expected Behavior:**
1. Opens Google login page
2. Sign in with Google account
3. Consent screen (if first time)
4. Redirects to: `http://localhost:8000/api/v1/auth/oauth/google/callback?code=...`
5. You'll see "connection refused" if server isn't running ← **This is expected and means OAuth is configured correctly!**

---

### GitHub OAuth

#### **Step 1: Register OAuth App**

1. Go to [GitHub Settings](https://github.com/settings/profile)
2. Scroll down → Click **"Developer settings"** (left sidebar)
3. Click **"OAuth Apps"** → **"New OAuth App"**

#### **Step 2: Fill OAuth App Details**

- **Application name:** `RAG Trial`
- **Homepage URL:** 
  - Development: `http://localhost:8000`
  - Production: `https://yourdomain.com`
- **Application description:** (optional) `RAG Document Chat Application`
- **Authorization callback URL:**
  - Development: `http://localhost:8000/api/v1/auth/oauth/github/callback`
  - Production: `https://yourdomain.com/api/v1/auth/oauth/github/callback`

#### **Step 3: Register Application**

1. Click **"Register application"**
2. **Copy Client ID** (shown immediately)
3. Click **"Generate a new client secret"**
4. **Copy Client Secret** (only shown once!)

#### **Step 4: Set Environment Variables**

```bash
export GITHUB_CLIENT_ID="your-github-client-id"
export GITHUB_CLIENT_SECRET="your-github-client-secret"
```

#### **Step 5: Test GitHub OAuth**

**Test URL (Development):**
```
https://github.com/login/oauth/authorize?client_id=YOUR_GITHUB_CLIENT_ID&redirect_uri=http://localhost:8000/api/v1/auth/oauth/github/callback&scope=user:email
```

Replace `YOUR_GITHUB_CLIENT_ID` with your actual client ID.

**Expected Behavior:**
1. Opens GitHub authorization page
2. Click **"Authorize [Your App Name]"**
3. Redirects to: `http://localhost:8000/api/v1/auth/oauth/github/callback?code=...`
4. You'll see "connection refused" if server isn't running ← **This is expected and means OAuth is configured correctly!**

---

## SMTP Configuration

### Why SMTP?

SMTP is required for:
- ✅ Email verification (required before using the app)
- ✅ Password reset emails
- ✅ Account notifications

### Option 1: Gmail SMTP (Free, Easy for Development)

#### **Step 1: Enable 2-Factor Authentication**

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **"2-Step Verification"** if not already enabled

#### **Step 2: Generate App Password**

1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select app: **"Mail"**
3. Select device: **"Other (Custom name)"**
4. Enter name: `RAG Trial`
5. Click **"Generate"**
6. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

#### **Step 3: Configure Environment Variables**

```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password-here"  # 16-char password from Step 2
```

#### **Step 4: Test SMTP (Python)**

```bash
python -c "
import smtplib
from email.mime.text import MIMEText

# Configuration
smtp_host = 'smtp.gmail.com'
smtp_port = 587
username = 'your-email@gmail.com'
password = 'your-app-password'

# Test connection
server = smtplib.SMTP(smtp_host, smtp_port)
server.starttls()
server.login(username, password)
print('✅ SMTP connection successful!')
server.quit()
"
```

### Option 2: SendGrid (Free Tier, Production-Ready)

#### **Step 1: Create SendGrid Account**

1. Go to [SendGrid](https://signup.sendgrid.com/)
2. Sign up for free account (100 emails/day free)

#### **Step 2: Create API Key**

1. Go to **Settings** → **API Keys**
2. Click **"Create API Key"**
3. Name: `RAG Trial`
4. Permissions: **"Full Access"** (or **"Mail Send"** only)
5. Click **"Create & View"**
6. **Copy API Key** (only shown once!)

#### **Step 3: Configure Environment Variables**

```bash
export SMTP_HOST="smtp.sendgrid.net"
export SMTP_PORT="587"
export SMTP_USERNAME="apikey"  # Literally the word "apikey"
export SMTP_PASSWORD="your-sendgrid-api-key"
```

### Option 3: Mailtrap (Development/Testing Only)

**Perfect for development - catches all emails without sending them!**

1. Go to [Mailtrap](https://mailtrap.io/)
2. Sign up for free account
3. Go to **Inboxes** → **My Inbox**
4. Copy SMTP credentials from **"Integrations"** tab

```bash
export SMTP_HOST="smtp.mailtrap.io"
export SMTP_PORT="2525"
export SMTP_USERNAME="your-mailtrap-username"
export SMTP_PASSWORD="your-mailtrap-password"
```

---

## Environment Variables

### Complete `.env` Example

Create a `.env` file in project root (or set system environment variables):

```bash
# JWT Configuration
JWT_SECRET="a3f2c8b9e1d4f6a7b2c9d8e3f1a4b7c2d9e8f3a1b6c4d7e2f9a3b8c1d6e4f7a2"

# Google OAuth
GOOGLE_CLIENT_ID="840295341867-xxxxxxxxxxxxxxxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="GOCSPX-xxxxxxxxxxxxxxxx"

# GitHub OAuth
GITHUB_CLIENT_ID="Iv1.xxxxxxxxxxxxxxxx"
GITHUB_CLIENT_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# SMTP (Gmail example)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USERNAME="your-email@gmail.com"
SMTP_PASSWORD="your-gmail-app-password"
```

### Load Environment Variables (Python)

If using `.env` file, install `python-dotenv`:

```bash
pip install python-dotenv
```

Add to your startup code:

```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file
```

---

## Testing Authentication

### 1. Test JWT Token Generation (Python)

```python
import jwt
import os
from datetime import datetime, timedelta

secret = os.getenv("JWT_SECRET")
payload = {
    "user_id": "test-user-123",
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(minutes=30)
}

token = jwt.encode(payload, secret, algorithm="HS256")
print(f"Generated Token: {token}")

# Verify
decoded = jwt.decode(token, secret, algorithms=["HS256"])
print(f"Decoded Payload: {decoded}")
```

### 2. Test Google OAuth Flow

```bash
# 1. Start your FastAPI server
make run

# 2. Visit test URL in browser
open "https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8000/api/v1/auth/oauth/google/callback&response_type=code&scope=openid%20email%20profile"

# 3. Expected: Login → Consent → Redirect to callback
```

### 3. Test GitHub OAuth Flow

```bash
# 1. Start your FastAPI server
make run

# 2. Visit test URL in browser
open "https://github.com/login/oauth/authorize?client_id=YOUR_GITHUB_CLIENT_ID&redirect_uri=http://localhost:8000/api/v1/auth/oauth/github/callback&scope=user:email"

# 3. Expected: Authorize → Redirect to callback
```

### 4. Test SMTP Connection

```bash
# Test SMTP using Python
python -c "
import smtplib
import os

server = smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT')))
server.starttls()
server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
print('✅ SMTP working!')
server.quit()
"
```

---

## Security Best Practices

### Production Checklist

- [ ] **JWT Secret:** Use strong random secret (32+ bytes)
- [ ] **Environment Variables:** Never commit secrets to Git
- [ ] **HTTPS Only:** Use HTTPS in production (OAuth requires it)
- [ ] **Token Expiry:** Keep access tokens short-lived (15-30 min)
- [ ] **Refresh Tokens:** Rotate refresh tokens on use
- [ ] **Password Hashing:** Use bcrypt with cost factor 12+
- [ ] **Rate Limiting:** Implement rate limiting on auth endpoints
- [ ] **CORS:** Restrict CORS origins in production
- [ ] **OAuth Redirects:** Whitelist exact redirect URIs
- [ ] **Email Verification:** Enforce email verification before any action
- [ ] **Audit Logging:** Log all authentication events with IP/user-agent

### Environment-Specific Settings

**Development:**
```toml
[auth]
access_token_expire_minutes = 60        # Longer for convenience
refresh_token_expire_days = 90          # Longer for convenience
```

**Production:**
```toml
[auth]
access_token_expire_minutes = 15        # Shorter for security
refresh_token_expire_days = 30          # Standard
```

### Secret Rotation

**Rotate secrets regularly (every 90 days):**

1. Generate new JWT secret
2. Keep old secret for 24 hours (grace period)
3. Update all environments
4. Invalidate old refresh tokens (force re-login)

### Monitoring

**Track these metrics:**
- Failed login attempts (detect brute force)
- Token refresh frequency (detect token theft)
- OAuth failures (detect misconfiguration)
- Email delivery failures (detect SMTP issues)

---

## Troubleshooting

### Issue: "Invalid JWT Secret"

**Cause:** Secret not set or contains special characters  
**Fix:** Regenerate secret using `openssl rand -hex 32`, ensure no quotes/spaces

### Issue: "Google OAuth redirect_uri_mismatch"

**Cause:** Redirect URI in code doesn't match Google Console  
**Fix:** Ensure exact match (including http vs https, port, path)

### Issue: "GitHub OAuth callback failed"

**Cause:** Client secret expired or incorrect  
**Fix:** Regenerate client secret in GitHub settings

### Issue: "SMTP authentication failed"

**Cause:** Wrong credentials or 2FA not enabled (Gmail)  
**Fix:** For Gmail, enable 2FA and use App Password, not account password

### Issue: "Email verification not working"

**Cause:** SMTP not configured or emails going to spam  
**Fix:** Use Mailtrap for dev, configure SPF/DKIM for production

---

## Next Steps

After completing this setup:

1. ✅ Run database migrations: `python -m migration up`
2. ✅ Test authentication endpoints: See [API.md](API.md)
3. ✅ Implement auth middleware: See Phase 1 implementation plan
4. ✅ Add request context logging: user_id, request_id, ip_address

---

## References

- [JWT.io](https://jwt.io/) - JWT debugger and documentation
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Apps](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [SendGrid SMTP](https://docs.sendgrid.com/for-developers/sending-email/integrating-with-the-smtp-api)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

