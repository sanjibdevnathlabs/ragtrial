"""
OAuth service for third-party authentication.

Single responsibility: OAuth authentication flows.
"""

import trace.codes as codes
from typing import Dict, List, Optional, Tuple

import constants
from app.modules.oauth.entity import OAuthProvider
from app.modules.oauth.repository import OAuthProviderRepository
from app.modules.registration.service import RegistrationService
from app.modules.token.service import TokenService
from app.modules.user.service import UserService
from app.security.jwt_service import JWTService
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class OAuthService:
    """
    OAuth authentication service.

    Responsibilities:
    - OAuth login flow
    - Link OAuth accounts
    - Unlink OAuth accounts
    - Sync OAuth profile data
    """

    def __init__(self):
        """Initialize OAuth service."""
        self.user_service = UserService()
        self.registration_service = RegistrationService()
        self.token_service = TokenService()
        self.oauth_repository = OAuthProviderRepository()
        self.session_factory = SessionFactory()
        self.jwt_service = JWTService()

    def authenticate(
        self,
        provider: str,
        provider_user_id: str,
        email: str,
        full_name: str,
        avatar_url: Optional[str] = None,
        raw_data: Optional[Dict] = None,
        client_metadata: Optional[Dict] = None,
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Authenticate with OAuth.

        Args:
            provider: OAuth provider (google, github)
            provider_user_id: User ID from provider
            email: Email from profile
            full_name: Full name from profile
            avatar_url: Avatar URL
            raw_data: Raw profile data
            client_metadata: Client info

        Returns:
            Tuple of (tokens_dict, error_message)
        """
        try:
            logger.info("oauth_auth_started", provider=provider, email=email)

            # Validate provider
            if provider not in [
                constants.OAUTH_PROVIDER_GOOGLE,
                constants.OAUTH_PROVIDER_GITHUB,
            ]:
                return None, f"Unsupported provider: {provider}"

            # Check if OAuth account exists
            with self.session_factory.get_read_session() as session:
                oauth_account = self.oauth_repository.find_by_provider_user_id(
                    session, provider, provider_user_id
                )

            if oauth_account:
                user_id = oauth_account.user_id
                self._sync_profile(oauth_account.id, email, raw_data)
            else:
                user_id = self._handle_new_oauth_user(
                    provider, provider_user_id, email, full_name, avatar_url, raw_data
                )

            # Check user active
            user = self.user_service.get_by_id(user_id)

            if not user or not user.get("is_active"):
                return None, "Account is suspended"

            # Generate tokens
            tokens = self._generate_tokens(user, client_metadata)

            logger.info("oauth_auth_completed", provider=provider, user_id=user_id)

            return tokens, None

        except Exception as e:
            logger.error("oauth_auth_failed", error=str(e), exc_info=True)
            return None, "OAuth authentication failed"

    def _handle_new_oauth_user(
        self,
        provider: str,
        provider_user_id: str,
        email: str,
        full_name: str,
        avatar_url: Optional[str],
        raw_data: Optional[Dict],
    ) -> str:
        """Handle new OAuth user (link or create)."""
        user = self.user_service.get_by_email(email)

        if user:
            user_id = user["id"]
        else:
            # Create new user
            user = self.registration_service.register_oauth_user(
                email, full_name, avatar_url
            )
            user_id = user["id"]

        # Link OAuth account
        self._link_account(user_id, provider, provider_user_id, email, raw_data)

        return user_id

    def _link_account(
        self,
        user_id: str,
        provider: str,
        provider_user_id: str,
        email: str,
        raw_data: Optional[Dict],
    ) -> None:
        """Link OAuth account to user."""
        oauth_account = OAuthProvider(
            id=OAuthProvider.generate_id(),
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
        )

        if raw_data:
            oauth_account.set_raw_data(raw_data)

        with self.session_factory.get_write_session() as session:
            self.oauth_repository.create(session, oauth_account)

        logger.info("oauth_account_linked", user_id=user_id, provider=provider)

    def _sync_profile(
        self, oauth_id: str, email: str, raw_data: Optional[Dict]
    ) -> None:
        """Sync OAuth profile data."""
        try:
            with self.session_factory.get_write_session() as session:
                account = self.oauth_repository.find_by_id(session, oauth_id)

                if account:
                    account.email = email
                    if raw_data:
                        account.set_raw_data(raw_data)
                    self.oauth_repository.update(session, account)

        except Exception as e:
            logger.error("oauth_sync_failed", error=str(e), exc_info=True)

    def _generate_tokens(self, user: Dict, metadata: Optional[Dict]) -> Dict:
        """Generate JWT token pair."""
        tokens = self.jwt_service.generate_token_pair(user["id"], user["email"])

        token_hash = JWTService.hash_token(tokens["refresh_token"])
        self.token_service.create_refresh_token(
            user["id"], token_hash, tokens["refresh_expires_at"], metadata
        )

        return tokens

    def get_providers(self, user_id: str) -> List[Dict]:
        """Get user's OAuth providers."""
        with self.session_factory.get_read_session() as session:
            providers = self.oauth_repository.find_by_user_id(session, user_id)
            return [p.to_dict() for p in providers]

    def unlink(self, user_id: str, provider: str) -> Tuple[bool, Optional[str]]:
        """
        Unlink OAuth provider.

        Args:
            user_id: User ID
            provider: OAuth provider

        Returns:
            Tuple of (success, error_message)
        """
        try:
            user = self.user_service.get_by_id(user_id)

            if not user:
                return False, "User not found"

            # Check can remove
            if not user.get("has_password"):
                providers = self.get_providers(user_id)
                if len(providers) <= 1:
                    return False, "Cannot remove only login method"

            # Unlink
            with self.session_factory.get_write_session() as session:
                account = self.oauth_repository.find_user_provider(
                    session, user_id, provider
                )

                if not account:
                    return False, "Provider not linked"

                self.oauth_repository.soft_delete(session, account.id)

            return True, None

        except Exception as e:
            logger.error("oauth_unlink_failed", error=str(e), exc_info=True)
            return False, "Failed to unlink provider"

    def has_provider(self, user_id: str, provider: str) -> bool:
        """Check if user has provider linked."""
        with self.session_factory.get_read_session() as session:
            return self.oauth_repository.user_has_provider(session, user_id, provider)

