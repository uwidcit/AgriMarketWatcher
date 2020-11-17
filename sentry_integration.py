import os
import logging

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send no events from log messages
)

# is_production = True if "ENV" in os.environ else False


logging.info('Enabling Sentry Integration')
sentry_sdk.init(
    dsn="https://7761c2f9313245b496cbbd07ccecceb0@sentry.io/1295927",
    integrations=[FlaskIntegration(), sentry_logging]
)
