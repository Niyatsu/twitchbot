import os
import requests
import hmac
import hashlib
import json

eventsub_subsctiption_url = "https://api.twitch.tv/helix/eventsub/subsctiptions"

auth_body = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}