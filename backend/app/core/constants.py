APP_NAME = "Exodia"
APP_VERSION = "0.1.0"

ALLOWED_TARGET_PROTOCOLS = {"http", "https"}
TARGET_TYPES = {"web", "api", "host"}
SCAN_STATUSES = {"pending", "running", "completed", "failed", "canceled"}
REPORT_FORMATS = {"html", "markdown", "json"}

SEVERITY_SCORES = {
    "info": 0,
    "low": 1,
    "medium": 3,
    "high": 6,
    "critical": 10,
}

DEFAULT_SAFE_PORTS = [22, 80, 443, 5432, 6379, 8080, 8443]
DEFAULT_HTTP_TIMEOUT_SECONDS = 8.0
MAX_SCAN_MODULES = 12
MAX_TAGS = 12

AUTHORIZED_USE_DISCLAIMER = (
    "Exodia is intended only for owned, authorized, or lab environments. "
    "It performs defensive checks and does not include exploit, evasion, "
    "persistence, credential theft, or destructive capabilities."
)

