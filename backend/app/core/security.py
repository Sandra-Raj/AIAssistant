# backend/app/core/security.py
import re

BLOCKED_PATTERNS = [
    r"ignore previous instructions",
    r"reveal (your|system) prompt",
    r"become an unrestricted AI",
    r"sql injection"
]

def sanitize_input(user_input: str) -> bool:
    """Returns False if a malicious pattern is detected."""
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False
    return True