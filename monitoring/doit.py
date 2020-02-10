import os
import requests
import json

def main():
    username = os.environ["CLEO_USERNAME"]
    password = os.environ["CLEO_PASSWORD"]
    res = requests.post(
        "https://cleo.aincient.org/rest-auth/login/",
        json={"username": username, "password": password},
    )
    res.raise_for_status()
    session_id = res.cookies["sessionid"]
    params = dict(
        search="blaat",
    )
    res = requests.get(
        "https://cleo.aincient.org/api/collectionitemfacetsonly/",
        cookies={"sessionid": session_id},
        params=params,
    )
    res.raise_for_status()
    print(json.dumps(res.json()))


if __name__ == "__main__":
    main()
