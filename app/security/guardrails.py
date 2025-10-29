"""
Guardrails manager for RAG security.

Coordinates input validation, prompt injection detection,
and output filtering for secure RAG operations.
"""

from dataclasses import dataclass
from trace import codes
from typing import Any, Dict

import constants
from app.security.validators import (
    InputValidator,
    OutputValidator,
    PromptInjectionDetector,
    ValidationResult,
)
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class GuardrailsConfig:
    """Configuration for guardrails"""

    enable_input_validation: bool = True
    enable_injection_detection: bool = True
    enable_output_validation: bool = True
    strict_mode: bool = True
    log_violations: bool = True


class GuardrailsManager:
    """
    Manages security guardrails for RAG system.

    Provides unified interface for input validation, injection detection,
    and output filtering.
    """

    def __init__(self, config: GuardrailsConfig = None):
        """Initialize guardrails manager."""
        self.config = config or GuardrailsConfig()

        self.input_validator = InputValidator()
        self.injection_detector = PromptInjectionDetector()
        self.output_validator = OutputValidator()

        logger.info(
            codes.GUARDRAILS_INITIALIZED,
            message=constants.MSG_GUARDRAILS_INITIALIZED,
            input_validation=self.config.enable_input_validation,
            injection_detection=self.config.enable_injection_detection,
            output_validation=self.config.enable_output_validation,
            strict_mode=self.config.strict_mode,
        )

    def validate_input(self, user_query: str) -> Dict[str, Any]:
        """Validate user input against all security checks."""
        violations = []
        threat_level = constants.THREAT_LEVEL_NONE
        sanitized_query = user_query

        if self.config.enable_input_validation:
            validation_result = self.input_validator.validate(user_query)

            if not validation_result.is_valid:
                violations.append(f"Input validation: {validation_result.reason}")
                threat_level = self._max_threat_level(
                    threat_level, validation_result.threat_level
                )

                if self.config.strict_mode:
                    self._log_violation(
                        constants.ERROR_INVALID_INPUT, validation_result, threat_level
                    )
                    raise ValueError(constants.ERROR_INVALID_INPUT)
            else:
                sanitized_query = validation_result.sanitized_input

        if self.config.enable_injection_detection:
            injection_result = self.injection_detector.detect(sanitized_query)

            if not injection_result.is_valid:
                violations.append(f"Injection detection: {injection_result.reason}")
                threat_level = self._max_threat_level(
                    threat_level, injection_result.threat_level
                )

                if self.config.strict_mode:
                    self._log_violation(
                        constants.ERROR_PROMPT_INJECTION, injection_result, threat_level
                    )
                    raise ValueError(constants.ERROR_PROMPT_INJECTION)

        if self.config.log_violations and violations:
            logger.warning(
                codes.SECURITY_VIOLATION_DETECTED,
                message=constants.MSG_SECURITY_VIOLATIONS_DETECTED,
                violations=violations,
                threat_level=threat_level,
            )

        is_safe = len(violations) == 0

        if is_safe:
            logger.info(
                codes.INPUT_VALIDATION_PASSED,
                message=constants.MSG_INPUT_VALIDATION_PASSED,
                threat_level=threat_level,
            )

        return {
            constants.VALIDATION_KEY_IS_SAFE: is_safe,
            constants.VALIDATION_KEY_SANITIZED_QUERY: (
                sanitized_query if is_safe else ""
            ),
            constants.VALIDATION_KEY_VIOLATIONS: violations,
            constants.VALIDATION_KEY_THREAT_LEVEL: threat_level,
            constants.VALIDATION_KEY_ERROR_MESSAGE: (
                constants.ERROR_BLOCKED_BY_GUARDRAILS if not is_safe else ""
            ),
        }

    def validate_output(self, llm_output: str) -> Dict[str, Any]:
        """Validate LLM output for safety."""
        violations = []
        threat_level = constants.THREAT_LEVEL_NONE

        if self.config.enable_output_validation:
            validation_result = self.output_validator.validate(llm_output)

            if not validation_result.is_valid:
                violations.append(f"Output validation: {validation_result.reason}")
                threat_level = self._max_threat_level(
                    threat_level, validation_result.threat_level
                )

                if self.config.strict_mode:
                    self._log_violation(
                        constants.ERROR_UNSAFE_OUTPUT, validation_result, threat_level
                    )
                    raise ValueError(constants.ERROR_UNSAFE_OUTPUT)

        if self.config.log_violations and violations:
            logger.error(
                codes.SECURITY_VIOLATION_DETECTED,
                message=constants.MSG_OUTPUT_VIOLATIONS_DETECTED,
                violations=violations,
                threat_level=threat_level,
            )

        is_safe = len(violations) == 0

        if is_safe:
            logger.debug(
                codes.OUTPUT_VALIDATION_PASSED,
                message=constants.MSG_OUTPUT_VALIDATION_PASSED,
            )

        return {
            constants.VALIDATION_KEY_IS_SAFE: is_safe,
            constants.VALIDATION_KEY_VALIDATED_OUTPUT: llm_output if is_safe else "",
            constants.VALIDATION_KEY_VIOLATIONS: violations,
            constants.VALIDATION_KEY_THREAT_LEVEL: threat_level,
            constants.VALIDATION_KEY_ERROR_MESSAGE: (
                constants.ERROR_UNSAFE_OUTPUT if not is_safe else ""
            ),
        }

    def _max_threat_level(self, level1: str, level2: str) -> str:
        """Return the maximum threat level between two levels."""
        levels = [
            constants.THREAT_LEVEL_NONE,
            constants.THREAT_LEVEL_LOW,
            constants.THREAT_LEVEL_MEDIUM,
            constants.THREAT_LEVEL_HIGH,
            constants.THREAT_LEVEL_CRITICAL,
        ]

        try:
            idx1 = levels.index(level1)
            idx2 = levels.index(level2)
            return levels[max(idx1, idx2)]
        except ValueError:
            return constants.THREAT_LEVEL_MEDIUM

    def _log_violation(
        self, error_msg: str, result: ValidationResult, threat_level: str
    ) -> None:
        """Log security violation."""
        logger.error(
            codes.SECURITY_VIOLATION_DETECTED,
            message=error_msg,
            reason=result.reason,
            threat_level=threat_level,
        )

    def get_security_report(self) -> Dict[str, Any]:
        """Get current security configuration and status."""
        return {
            constants.GUARDRAILS_KEY_ENABLED: True,
            constants.GUARDRAILS_KEY_CONFIGURATION: {
                "input_validation": self.config.enable_input_validation,
                "injection_detection": self.config.enable_injection_detection,
                "output_validation": self.config.enable_output_validation,
                "strict_mode": self.config.strict_mode,
            },
            constants.GUARDRAILS_KEY_VALIDATORS: {
                "input_validator": (
                    constants.GUARDRAILS_STATUS_ACTIVE
                    if self.config.enable_input_validation
                    else constants.GUARDRAILS_STATUS_DISABLED
                ),
                "injection_detector": (
                    constants.GUARDRAILS_STATUS_ACTIVE
                    if self.config.enable_injection_detection
                    else constants.GUARDRAILS_STATUS_DISABLED
                ),
                "output_validator": (
                    constants.GUARDRAILS_STATUS_ACTIVE
                    if self.config.enable_output_validation
                    else constants.GUARDRAILS_STATUS_DISABLED
                ),
            },
        }
