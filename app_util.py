import os
from datetime import timedelta
from functools import update_wrapper

import requests
import six
from flask import current_app, make_response, request


def crossdomain(
    origin=None,
    methods=None,
    headers=None,
    max_age=21600,
    attach_to_all=True,
    automatic_options=True,
):
    if methods is not None:
        methods = ", ".join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, six.string_types):
        headers = ", ".join(x.upper() for x in headers)
    if not isinstance(origin, six.string_types):
        origin = ", ".join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers["allow"]

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == "OPTIONS":
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != "OPTIONS":
                return resp

            h = resp.headers
            h["Access-Control-Allow-Origin"] = origin
            h["Access-Control-Allow-Methods"] = get_methods()
            h["Access-Control-Max-Age"] = str(max_age)
            h["Access-Control-Allow-Credentials"] = "true"
            h[
                "Access-Control-Allow-Headers"
            ] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h["Access-Control-Allow-Headers"] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


def is_testing() -> bool:
    return True if os.environ.get("TESTING", "false").lower() == "true" else False


def is_production() -> bool:
    return (
        True if os.environ.get("ENV", "development").lower() == "production" else False
    )


def retrieve_crop_flag_from_env() -> bool:
    return True if os.environ.get("RETRIEVE_CROPS", "true").lower() == "true" else False


def retrieve_fish_flag_from_env() -> bool:
    return True if os.environ.get("RETRIEVE_FISH", "true").lower() == "true" else False


def check_if_url_is_valid(url: str) -> bool:
    try:
        status = requests.head(url, timeout=get_timeout_value_from_evn()).status_code
        # print(f"{url} - {status}")
        return status == 200 or status == 201 or status == 304 or status == 302
    except requests.ConnectTimeout:
        return False


def get_timeout_value_from_evn() -> int:
    try:
        return int(os.getenv("REQUEST_TIMEOUT", "10"))
    except Exception:
        return 10
