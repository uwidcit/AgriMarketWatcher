import logging
import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

is_production = True if "ENV" in os.environ else False
environment = "production" if is_production else "development"
logging.info('Environment is {0}'.format(environment))

logging.info('Enabling Sentry Integration')
sentry_sdk.init(
    dsn="https://7761c2f9313245b496cbbd07ccecceb0@sentry.io/1295927",
    integrations=[
        FlaskIntegration(),
        SqlalchemyIntegration(),
        sentry_logging
    ],
    traces_sample_rate=1.0,
    environment=environment,
    attach_stacktrace=True
)
