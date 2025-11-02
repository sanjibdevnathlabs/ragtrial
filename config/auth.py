"""
Authentication configuration classes.

Contains configuration for JWT tokens, OAuth providers (Google, GitHub),
and email verification settings.
"""


class OAuthGoogleConfig:
    """Google OAuth 2.0 configuration"""

    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8000/api/v1/auth/oauth/google/callback"


class OAuthGitHubConfig:
    """GitHub OAuth 2.0 configuration"""

    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8000/api/v1/auth/oauth/github/callback"


class OAuthConfig:
    """OAuth configuration for all providers"""

    google: OAuthGoogleConfig = None
    github: OAuthGitHubConfig = None


class EmailConfig:
    """Email verification and SMTP configuration"""

    enabled: bool = True
    verification_required: bool = True
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@ragtrial.com"
    from_name: str = "RAG Trial"


class AuthConfig:
    """
    Authentication configuration.

    Includes:
    - JWT token settings (secret, algorithm, expiration)
    - OAuth provider configurations (Google, GitHub)
    - Email verification settings (SMTP)
    """

    # JWT Configuration
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    password_reset_expire_minutes: int = 30

    # OAuth Configuration
    oauth: OAuthConfig = None

    # Email Configuration
    email: EmailConfig = None

