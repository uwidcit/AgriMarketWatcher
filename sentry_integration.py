import logging
import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)

is_production = True if os.environ.get("ENV", "development") == "production" else False
environment = "production" if is_production else "development"
logging.info("Environment is {0}".format(environment))

sentry_dns = os.getenv("SENTRY_DNS")
if sentry_dns:
    logging.info("Enabling Sentry Integration")
    sentry_sdk.init(
        dsn=sentry_dns,
        integrations=[FlaskIntegration(), sentry_logging, RedisIntegration()],
        traces_sample_rate=0.25,
        sample_rate=0.25,
        environment=environment,
        attach_stacktrace=True,
    )
