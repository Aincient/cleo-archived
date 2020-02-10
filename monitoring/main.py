import os
import requests
import messagebird


def cron_pubsub(event, context):
    username = os.environ["CLEO_USERNAME"]
    password = os.environ["CLEO_PASSWORD"]
    messagebird_key = os.environ["MESSAGEBIRD_KEY"]
    client = messagebird.Client(messagebird_key)
    try:
        res = requests.post(
            "https://cleo.aincient.org/rest-auth/login/",
            json={"username": username, "password": password},
        )
        res.raise_for_status()
        session_id = res.cookies["sessionid"]
        params = dict(search="blaat")
        res = requests.get(
            "https://cleo.aincient.org/api/collectionitemfacetsonly/",
            cookies={"sessionid": session_id},
            params=params,
        )
        res.raise_for_status()
    except Exception:
        client.message_create("+31629513980", "+31629513980,+31612335651", "Cleo search failed.")
