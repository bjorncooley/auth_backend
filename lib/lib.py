import json
import os

from flask import make_response
from raven import Client
import requests

RAVEN_CLIENT='<CLIENT_KEY>'


def get_endpoint(endpoint):
    SANDBOX_MAILGUN_KEY = "<SANDBOX_KEY>"
    SANDBOX_MAILGUN_URL = "<SANDBOX_URL>"
    if endpoint == "email":
        return os.getenv("EMAIL_ENDPOINT", "https://api:%s@%s" % (
                          SANDBOX_MAILGUN_KEY, SANDBOX_MAILGUN_URL))


def get_request_data(request, required_params):
    
    data = {}
    if request.method == 'GET':
        for param in required_params:
            if param not in request.args:
                raise ValueError("%s must be included in request " % param)
            data[param] = request.args.get(param)

    elif request.method == 'POST':            
        if not request.data:
            raise ValueError("Request body must contain data")
        try:
            data = json.loads(request.data.decode("utf-8"))
        except TypeError:
            raise TypeError("Data must be compatible with JSON")

        for param in required_params:
            if param not in data:
                raise ValueError("%s must be included in request" % param)
            if data[param] == "":
                raise ValueError("%s must not be empty" % param)

    return data


def handle_error(message, logger, status_code=500):
    env = os.getenv("ENV", "test")
    if env is not "test":
        client = Client(RAVEN_CLIENT)
        client.captureMessage(
            "%s in authorizer %s: %s" % (
            status_code, os.getenv("ENV", "test"), message)
        )
    logger.error(message)
    return make_response(message, status_code)


def send_reset_link(email, token, url):

    reset_link = "%s%s" % (url, token)
    mailgun_link = get_endpoint("email")
    data = {
        "from": "<FROM_EMAIL>",
        "to": email,
        "subject": "Password reset link",
        "text": "Please use this link to reset your password: %s" % reset_link,
    }
    return requests.post(mailgun_link, data=data)
    