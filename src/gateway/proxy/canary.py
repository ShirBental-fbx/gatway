"""Canary routing configuration and logic."""

from __future__ import annotations

import json
import logging
import os
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class CanaryRule:
    """A single canary routing rule."""

    partner: str | None = None
    endpoint_pattern: str | None = None
    method: str | None = None
    percentage: int = 0
    # Note: require_idempotency removed - upstream has no idempotency mechanism

    def matches(
        self,
        partner: str | None,
        path: str,
        method: str,
        has_idempotency_key: bool,  # Ignored but kept for API compatibility
    ) -> bool:
        """
        Check if this rule matches the request.

        Args:
            partner: Partner ID from URL path or None
            path: Request path
            method: HTTP method
            has_idempotency_key: Ignored (upstream has no idempotency mechanism)

        Returns:
            True if rule matches
        """
        # Partner match
        if self.partner is not None:
            if partner is None or partner.lower() != self.partner.lower():
                return False

        # Method match
        if self.method is not None:
            if method.upper() != self.method.upper():
                return False

        # Endpoint pattern match
        if self.endpoint_pattern is not None:
            # Support both prefix and regex patterns
            if self.endpoint_pattern.startswith("^") or ".*" in self.endpoint_pattern:
                # Regex pattern
                try:
                    pattern = re.compile(self.endpoint_pattern)
                    if not pattern.search(path):
                        return False
                except re.error:
                    logger.warning(f"Invalid regex pattern: {self.endpoint_pattern}")
                    return False
            else:
                # Prefix pattern
                if not path.startswith(self.endpoint_pattern):
                    return False

        return True


class CanaryRouter:
    """Router for canary traffic selection."""

    def __init__(self, rules: list[CanaryRule], canary_enabled: bool = True):
        """
        Initialize canary router.

        Args:
            rules: List of canary rules
            canary_enabled: Whether canary routing is enabled
        """
        self.rules = rules
        self.canary_enabled = canary_enabled

    def should_use_canary(
        self,
        partner: str | None,
        path: str,
        method: str,
        has_idempotency_key: bool = False,
    ) -> tuple[bool, str]:
        """
        Determine if request should go to canary upstream.
        
        SAFETY: Upstream has NO idempotency mechanism (per UPSTREAM_EXPECTATIONS.md).
        Therefore, canary routing for POST/PUT/PATCH/DELETE is BLOCKED.

        Args:
            partner: Partner ID from URL path or None
            path: Request path
            method: HTTP method
            has_idempotency_key: Ignored (upstream has no idempotency mechanism)

        Returns:
            Tuple of (use_canary, reason)
        """
        if not self.canary_enabled:
            return False, "canary_disabled"

        # Safety: Upstream has NO idempotency mechanism
        # BLOCK canary routing for all non-idempotent methods
        is_idempotent_method = method.upper() in ("GET", "HEAD")
        
        if not is_idempotent_method:
            # Upstream has no idempotency mechanism - BLOCK canary for POST/PUT/PATCH/DELETE
            return False, "non_get_blocked_no_idempotency"

        # For GET/HEAD only: find matching rules
        matching_rules = [
            rule
            for rule in self.rules
            if rule.matches(partner, path, method, has_idempotency_key=False)
        ]

        if not matching_rules:
            return False, "no_matching_rule"

        # For GET/HEAD: apply percentage if specified
        for rule in matching_rules:
            if rule.percentage > 0:
                # Apply percentage-based routing
                roll = random.randint(1, 100)
                if roll <= rule.percentage:
                    return True, f"percentage:{rule.percentage}%"
            elif rule.percentage == 0:
                # Explicit rule without percentage = always route
                return True, f"explicit_rule:{rule.partner or 'any'}"

        return False, "percentage_not_met"


def load_canary_config(config_path: str | None = None) -> CanaryRouter:
    """
    Load canary configuration from file.

    Config file format (JSON):
    {
        "enabled": true,
        "rules": [
            {
                "partner": "nav",
                "endpoint_pattern": "/api/v1/leads",
                "method": "GET",
                "percentage": 10
            },
            {
                "partner": "intuit",
                "endpoint_pattern": "^/api/v1/.*",
                "method": "GET",
                "percentage": 5
            },
            {
                "partner": "nav",
                "endpoint_pattern": "/api/v1/webhooks",
                "method": "POST",
                "require_idempotency": true
            }
        ]
    }

    Args:
        config_path: Path to config file. If None, uses CANARY_CONFIG_PATH env var
                     or defaults to "canary_config.json" in current directory.

    Returns:
        CanaryRouter instance
    """
    if config_path is None:
        config_path = os.getenv("CANARY_CONFIG_PATH", "canary_config.json")

    config_file = Path(config_path)

    if not config_file.exists():
        logger.info(f"Canary config file not found, using defaults: {config_path}")
        return CanaryRouter(rules=[], canary_enabled=False)

    try:
        with open(config_file, "r") as f:
            config = json.load(f)

        enabled = config.get("enabled", True)
        rules_data = config.get("rules", [])

        rules = []
        for rule_data in rules_data:
            # Ignore require_idempotency if present (upstream has no idempotency mechanism)
            rule = CanaryRule(
                partner=rule_data.get("partner"),
                endpoint_pattern=rule_data.get("endpoint_pattern"),
                method=rule_data.get("method"),
                percentage=rule_data.get("percentage", 0),
            )
            rules.append(rule)

        logger.info(f"Loaded canary config: {config_path} rules_count={len(rules)}")
        return CanaryRouter(rules=rules, canary_enabled=enabled)

    except Exception as e:
        logger.error(f"Failed to load canary config: {config_path} error={str(e)}")
        return CanaryRouter(rules=[], canary_enabled=False)
