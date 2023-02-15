import requests
import json
from prometheus_client import Gauge, start_http_server
import threading
from time import sleep

kasazumi_puuid = "871615b0-686a-58b6-8cb5-8ccfd97ca98a"


class regularlyGetInfo(threading.Thread):
    def __init__(self):
        super(regularlyGetInfo, self).__init__()
        self.event = threading.Event()
        self.kasazumi = player(kasazumi_puuid, "kasazumi")
        # 他のプレイヤーも同様に追加

    def run(self):
        while True:
            self.kasazumi.getInfo()
            sleep(300)


class player:
    def __init__(self, puuid, playername):
        self.puuid = puuid
        self.playername = playername
        self.gauge = Gauge(self.playername + "_rating", self.playername + "'s rating")

    def getInfo(self):
        rating = 0
        MMRDataResponseRaw = requests.get(
            "https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/ap/" + self.puuid
        )
        if "json" not in MMRDataResponseRaw.headers.get("content-type"):
            print("Response is not content-type:json")
            return
        MMRDataResponse = json.loads(MMRDataResponseRaw.text)
        if MMRDataResponse["status"] != 200:
            print("Error occurer while getting a request")
        else:
            rating = MMRDataResponse["data"]["current_data"]["elo"]
            self.gauge.set(rating)
            print(self.playername + "'s rating is " + str(rating))


if __name__ == "__main__":
    t = regularlyGetInfo()
    t.start()
    start_http_server(8888)
