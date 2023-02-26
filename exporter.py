import requests
import json
from prometheus_client import Gauge, start_http_server
import threading
from time import sleep
from dotenv import dotenv_values


class regularlyGetInfo(threading.Thread):
    def __init__(self):
        super(regularlyGetInfo, self).__init__()
        self.event = threading.Event()
        config = dotenv_values(".env")
        self.players = player(**config)

    def run(self):
        while True:
            try:
                self.players.getInfo()
            except Exception as e:
                print(e)

            sleep(300)


class player:
    g = Gauge(
        "valo_rating",
        "",
        ["playername"],
    )

    def __init__(self, **kwargs):
        self.dict = kwargs

    def getInfo(self):
        for playername, puuid in self.dict.items():
            rating = 0
            MMRDataResponseRaw = requests.get(
                "https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/ap/" + puuid,
                timeout=(3.0),
            )

            if "json" not in MMRDataResponseRaw.headers.get("content-type"):
                print(
                    "response header content-type is %s",
                    MMRDataResponseRaw.headers.get("content-type"),
                )
                raise ContentTypeMismatchError(
                    "response header content-type is not json"
                )

            if MMRDataResponseRaw.status_code != 200:
                MMRDataResponseRaw.raise_for_status()

            MMRDataResponse = json.loads(MMRDataResponseRaw.text)
            if MMRDataResponse["status"] != 200:
                print("request json '.status' is %s", MMRDataResponse["status"])
                raise JsonBodyNotSuccessfulError("response json '.status' is not 200")

            rating = MMRDataResponse["data"]["current_data"]["elo"]
            self.g.labels(playername).set(rating)
            print(playername + "'s rating is " + str(rating))


class JsonBodyNotSuccessfulError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


class ContentTypeMismatchError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


if __name__ == "__main__":
    t = regularlyGetInfo()
    t.start()
    start_http_server(8888)
