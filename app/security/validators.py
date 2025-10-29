"""
Input and output validators for RAG security.

Provides validation, sanitization, and prompt injection detection.
"""

import re
from dataclasses import dataclass
from trace import codes

import constants
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check"""

    is_valid: bool
    reason: str = ""
    sanitized_input: str = ""
    threat_level: str = constants.THREAT_LEVEL_NONE


class InputValidator:
    """
    Validates and sanitizes user input.

    Checks for:
    - Maximum length limits
    - Forbidden characters/patterns
    - Excessive special characters
    - Null bytes and control characters
    """

    # Forbidden patterns (aggressive sanitization)
    FORBIDDEN_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"eval\s*\(",
    ]

    def __init__(self):
        """Initialize input validator"""
        self.forbidden_regex = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for pattern in self.FORBIDDEN_PATTERNS
        ]

    def validate(self, user_input: str) -> ValidationResult:
        """Validate user input for safety."""
        if not user_input:
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_EMPTY_INPUT,
                threat_level=constants.THREAT_LEVEL_NONE,
            )

        sanitized = user_input.strip()

        if not self._check_length(sanitized):
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_INPUT_TOO_LONG,
                threat_level=constants.THREAT_LEVEL_LOW,
            )

        if not self._check_control_chars(sanitized):
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_FORBIDDEN_CHARS,
                threat_level=constants.THREAT_LEVEL_MEDIUM,
            )

        if not self._check_forbidden_patterns(sanitized):
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_FORBIDDEN_PATTERNS,
                threat_level=constants.THREAT_LEVEL_HIGH,
            )

        if not self._check_special_char_ratio(sanitized):
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_TOO_MANY_SPECIAL_CHARS,
                threat_level=constants.THREAT_LEVEL_MEDIUM,
            )

        logger.debug(
            codes.INPUT_VALIDATION_PASSED, message=constants.MSG_INPUT_VALIDATION_PASSED
        )

        return ValidationResult(
            is_valid=True,
            sanitized_input=sanitized,
            threat_level=constants.THREAT_LEVEL_NONE,
        )

    def _check_length(self, text: str) -> bool:
        """Check if text exceeds maximum length."""
        if len(text) > constants.MAX_QUERY_LENGTH:
            logger.warning(
                codes.INPUT_VALIDATION_FAILED,
                message=constants.VALIDATION_REASON_INPUT_TOO_LONG,
                length=len(text),
                max_length=constants.MAX_QUERY_LENGTH,
            )
            return False
        return True

    def _check_control_chars(self, text: str) -> bool:
        """Check for null bytes and control characters."""
        if "\x00" in text or any(ord(c) < 32 and c not in "\n\r\t" for c in text):
            logger.warning(
                codes.INPUT_VALIDATION_FAILED,
                message=constants.VALIDATION_REASON_FORBIDDEN_CHARS,
            )
            return False
        return True

    def _check_forbidden_patterns(self, text: str) -> bool:
        """Check for forbidden patterns."""
        for pattern in self.forbidden_regex:
            if pattern.search(text):
                logger.warning(
                    codes.INPUT_VALIDATION_FAILED,
                    message=constants.VALIDATION_REASON_FORBIDDEN_PATTERNS,
                    pattern=pattern.pattern,
                )
                return False
        return True

    def _check_special_char_ratio(self, text: str) -> bool:
        """Check special character ratio."""
        if not text:
            return True

        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        ratio = special_chars / len(text)

        if ratio > constants.MAX_SPECIAL_CHAR_RATIO:
            logger.warning(
                codes.INPUT_VALIDATION_FAILED,
                message=constants.VALIDATION_REASON_TOO_MANY_SPECIAL_CHARS,
                ratio=ratio,
            )
            return False
        return True


class PromptInjectionDetector:
    """Detects potential prompt injection attempts."""

    INJECTION_PATTERNS = [
        r"ignore\s+(?:all\s+)?(?:previous|above|prior)?\s*"
        r"(?:instructions|prompts?|rules|context)",
        r"disregard\s+(?:all\s+)?(?:previous|above|prior)",
        r"forget\s+(?:everything|all|previous)",
        r"show\s+(me\s+)?(your|the)\s+(system\s+)?(prompt|instructions)",
        r"what\s+(is|are)\s+your\s+(instructions|rules|prompts?)",
        r"repeat\s+(your|the)\s+(system\s+)?(prompt|instructions)",
        r"you\s+are\s+now",
        r"act\s+as\s+(a|an)\s+\w+",
        r"pretend\s+(you\s+are|to\s+be)",
        r"roleplay\s+as",
        r"developer\s+mode",
        r"god\s+mode",
        r"admin\s+mode",
        r"jailbreak",
        r"DAN\s+mode",
        r"ignore\s+(the\s+)?context",
        r"without\s+(using|consulting)\s+(the\s+)?context",
        r"respond\s+(only\s+)?with\s+code",
        r"output\s+raw\s+(sql|python|javascript)",
    ]

    def __init__(self):
        """Initialize prompt injection detector"""
        self.injection_regex = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.INJECTION_PATTERNS
        ]

    def detect(self, user_input: str) -> ValidationResult:
        """Detect potential prompt injection attempts."""
        if not user_input:
            return ValidationResult(
                is_valid=True, threat_level=constants.THREAT_LEVEL_NONE
            )

        if not self._check_injection_patterns(user_input):
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_PROMPT_INJECTION,
                threat_level=constants.THREAT_LEVEL_CRITICAL,
            )

        if not self._check_excessive_newlines(user_input):
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_EXCESSIVE_NEWLINES,
                threat_level=constants.THREAT_LEVEL_MEDIUM,
            )

        if not self._check_code_blocks(user_input):
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_SUSPICIOUS_CODE_BLOCK,
                threat_level=constants.THREAT_LEVEL_MEDIUM,
            )

        logger.debug(
            codes.INJECTION_DETECTION_PASSED,
            message=constants.MSG_NO_INJECTION_DETECTED,
        )

        return ValidationResult(is_valid=True, threat_level=constants.THREAT_LEVEL_NONE)

    def _check_injection_patterns(self, text: str) -> bool:
        """Check for injection patterns."""
        for pattern in self.injection_regex:
            match = pattern.search(text)
            if match:
                logger.warning(
                    codes.INJECTION_DETECTED,
                    message=constants.VALIDATION_REASON_PROMPT_INJECTION,
                    pattern=pattern.pattern,
                    matched_text=match.group(0),
                )
                return False
        return True

    def _check_excessive_newlines(self, text: str) -> bool:
        """Check for excessive newlines."""
        if text.count("\n") > constants.MAX_NEWLINES_ALLOWED:
            logger.warning(
                codes.INJECTION_DETECTED,
                message=constants.VALIDATION_REASON_EXCESSIVE_NEWLINES,
            )
            return False
        return True

    def _check_code_blocks(self, text: str) -> bool:
        """Check for markdown code blocks."""
        if "```" in text or "~~~" in text:
            logger.warning(
                codes.INJECTION_DETECTED,
                message=constants.VALIDATION_REASON_SUSPICIOUS_CODE_BLOCK,
            )
            return False
        return True


class OutputValidator:
    """Validates LLM output for safety and compliance."""

    LEAK_PATTERNS = [
        r"system:",
        r"<\|system\|>",
        r"You are a helpful AI assistant",
        r"Follow these rules:",
    ]

    HARMFUL_PATTERNS = [
        r"<script",
        r"javascript:",
        r"onerror\s*=",
    ]

    def __init__(self):
        """Initialize output validator"""
        self.leak_regex = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.LEAK_PATTERNS
        ]
        self.harmful_regex = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.HARMFUL_PATTERNS
        ]

    def validate(self, llm_output: str) -> ValidationResult:
        """Validate LLM output for safety."""
        if not llm_output:
            return ValidationResult(
                is_valid=True,
                sanitized_input="",
                threat_level=constants.THREAT_LEVEL_NONE,
            )

        if not self._check_prompt_leakage(llm_output):
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_SYSTEM_PROMPT_LEAK,
                threat_level=constants.THREAT_LEVEL_HIGH,
            )

        if not self._check_harmful_content(llm_output):
            return ValidationResult(
                is_valid=False,
                reason=constants.VALIDATION_REASON_HARMFUL_CONTENT,
                threat_level=constants.THREAT_LEVEL_HIGH,
            )

        logger.debug(
            codes.OUTPUT_VALIDATION_PASSED,
            message=constants.MSG_OUTPUT_VALIDATION_PASSED,
        )

        return ValidationResult(
            is_valid=True,
            sanitized_input=llm_output,
            threat_level=constants.THREAT_LEVEL_NONE,
        )

    def _check_prompt_leakage(self, text: str) -> bool:
        """Check for system prompt leakage."""
        for pattern in self.leak_regex:
            if pattern.search(text):
                logger.error(
                    codes.OUTPUT_VALIDATION_FAILED,
                    message=constants.VALIDATION_REASON_SYSTEM_PROMPT_LEAK,
                    pattern=pattern.pattern,
                )
                return False
        return True

    def _check_harmful_content(self, text: str) -> bool:
        """Check for harmful content."""
        for pattern in self.harmful_regex:
            if pattern.search(text):
                logger.error(
                    codes.OUTPUT_VALIDATION_FAILED,
                    message=constants.VALIDATION_REASON_HARMFUL_CONTENT,
                    pattern=pattern.pattern,
                )
                return False
        return True
