"""
Sentry Error Tracking and Performance Monitoring Integration.
"""
import os
import sentry_sdk
try:
    from sentry_sdk.integrations.fastapi import FastApiIntegration
except ImportError:
    try:
        from sentry_sdk.integrations.fastapi import FastAPIIntegration as FastApiIntegration
    except ImportError:
        FastApiIntegration = None

try:
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
except ImportError:
    SqlalchemyIntegration = None


def init_sentry():
    """Initialize Sentry SDK if SENTRY_DSN is provided in environment variables."""
    sentry_dsn = os.getenv("SENTRY_DSN", "").strip()
    if not sentry_dsn:
        return False

    environment = os.getenv("ENVIRONMENT", "development").lower()
    traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    release = os.getenv("RELEASE_VERSION", "v2.3-transportation-suite")

    integrations = []
    if FastApiIntegration:
        integrations.append(FastApiIntegration(transaction_style="endpoint"))
    if SqlalchemyIntegration:
        integrations.append(SqlalchemyIntegration())

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=release,
        traces_sample_rate=traces_sample_rate,
        integrations=integrations,
        send_default_pii=False,
    )
    return True
