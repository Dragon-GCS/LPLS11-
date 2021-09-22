import json
import os

from config import *
from urllib import request, parse
from queue import Queue
from threading import Thread, Lock



def multiThread(target, num_thread, **kwargs):
    threads = []
    for _ in range(num_thread):
        threads.append(t := Thread(target=target, 
                                    kwargs=kwargs))
        t.start()
    for t in threads:
        t.join()


class Spider:
    url: str
    post_data: str
    data:dict

    @property
    def _post_data(self):
        if self.post_data:
            return parse.urlencode(self.post_data).encode()

    def fetchJson(self, url, method, temp_name):
        temp_filename = os.path.join(TEMP_DIR, "_".join([self.__class__.__name__, temp_name]))
        if not os.path.isfile(temp_filename):
            print(f"Fetching {temp_filename}")
            req = request.Request(url, headers=HEADER)
            try:
                if method == "post":
                    response = request.urlopen(req, self._post_data, timeout=10).read()
                elif method == "get":
                    response = request.urlopen(req, timeout=10).read()
            except Exception as e:
                print(e)
                print("Error url:", url)
                return

            if SAVE_TEMP:
                with open(temp_filename, "wb") as f:
                    f.write(response)
            return json.loads(response) if response else None
        else:
            print(f"Using temp file: {os.path.abspath(temp_filename)}")
            with open(temp_filename, "rb") as f:
                return json.load(f)
    
    def saveData(self, filename) -> None:
        with open(file:=os.path.join(JSON_DIR, filename), "w") as f:
            json.dump(self.data, f)
        print(f"Result file saved to '{os.path.abspath(file)}'\n")


class TourIDSpider(Spider):
    url = "https://www.scoregg.com/services/api_url.php"
    post_data = {
        "api_path":"/services/match/tournament_list.php",
        "method":"post",
        "platform":"web",
        "api_version": "9.9.9",}
    
    def __init__(self, filename = "result.json", deadline = 20200101) -> None:
        self.deadline = deadline
        self.filename = filename
        self.run()

    def processData(self):
        self.data = self.data["data"]["list"]
        result = {}
        for id in self.data:
            if (start := id.get("start_date", None)) and (date:=int(start.replace("-", ""))) > self.deadline:
                result[id["tournamentID"]] = (id["name"].replace(" ", ""), date)
        self.data = result
    
    def run(self):
        self.data = self.fetchJson(self.url, "post", "temp.json")
        self.processData()
        self.saveData(self.filename)


class PlayerSpider(Spider):
    url = "https://www.scoregg.com/services/api_url.php"
    post_data =  {
        "api_path": "/services/gamingDatabase/match_data_ssdb_list.php",
        "method": "post",
        "platform": "web",
        "api_version": "9.9.9",
        "language_id": "1",
        "tournament_id": "",
        "type": "player",
        "page": "",}
    def __init__(self, filename, num_thread = 8) -> None:
        self.result_list = []
        self.pages = Queue()
        self.exlude_item = ("country_id","country_image","player_image","team_image","update_time", "f_score")
        self.filename = "{}_" + filename
        self.num_thread = num_thread
        self.lock = Lock()
        self.run()

    def processData(self, data):
        data = data["data"]["data"]["list"]
        for player in data:
            for item in self.exlude_item:
                del player[item]
        self.result_list += data

    def fetch(self):
        
        while not self.pages.empty():
            page = self.pages.get()
            self.lock.acquire()
            try:
                self.post_data["page"] = str(page)
                data = self.fetchJson(self.url, "post", temp_name=self.temp_name.format(page))
            finally:
                self.lock.release()
            self.processData(data)

    def fetchData(self):
        self.post_data["page"] = "1"
        self.post_data["tournament_id"] = self.tour_id
        self.temp_name = f"{self.tour_id}_{self.post_data['type']}_" + "{}.json"
        print(f"Fetching {TOUR_ID[self.tour_id][0]} info")
        temp_name = self.temp_name.format(1)
        data = self.fetchJson(self.url, "post", 
                        temp_name = temp_name)

        total_num = int(data["data"]["data"]["count"])
        data_per_page = len(data["data"]["data"]["list"])
        pages = total_num // data_per_page + 1
        print(f"Totol items num: {total_num}")
        print(f"Processing file {temp_name}")

        self.processData(data)

        for page in range(2, pages + 1):
            self.pages.put(page)

        multiThread(self.fetch, self.num_thread)

        self.data = self.result_list

    def run(self):
        for self.tour_id in TOUR_ID:
            self.fetchData()
            self.saveData(self.filename.format(self.tour_id))


class HeroSpider(PlayerSpider):
    def run(self):
        self.post_data['type'] = "hero"
        self.exlude_item = ("hero_image", "hero_name_en", "hero_name_tw", "update_time", "f_score")
        super().run()


class MatchSpider(Spider):
    url_list = (
        "https://img.scoregg.com/tr/{tour_Id}.json",                # GET: RoundId list
        "https://img.scoregg.com/tr_round/{round_sonID}.json",      # GET: matchID list 
        "https://img.scoregg.com/match/resultlist/{matchID}.json",  # GET: result list of a match
        "https://img.scoregg.com/match/result/{resultID}.json",     # GET: result detail
    )

    def __init__(self, filename, num_thread = 8) -> None:
        self.filename = "{}_" + filename
        self.num_thread = num_thread
        self.round_list = Queue()
        self.match_list = Queue()
        self.result_list = Queue()
        self.detail = Queue()
        self.run()

    def fetchMatchID(self):
        while not self.round_list.empty():
            roundId = self.round_list.get()
            url = self.url_list[1].format(round_sonID = roundId)
            temp_name = f"{self.tour_id}_{roundId}_Match_list.json"
            data = self.fetchJson(url, "get", temp_name)
            if not data:
                continue
            for match in data:
                self.match_list.put(match["matchID"])

    def fetchResultID(self):
        while not self.match_list.empty():
            match = self.match_list.get()
            url = self.url_list[2].format(matchID=match)
            temp_name = f"{self.tour_id}_{match}_Match_detail.json"
            results = self.fetchJson(url, "get", temp_name)
            if not results:
                continue
            for result in results["data"]:
                self.result_list.put(result["resultID"])

    def fetchDetail(self):
        while not self.result_list.empty():
            result = self.result_list.get()
            url = self.url_list[3].format(resultID=result)
            temp_name = f"{self.tour_id}_{result}_Result_detail.json"
            detail = self.fetchJson(url, "get", temp_name)
            if not detail:
                continue
            detail["data"]["result_list"]["result_id"] = result
            self.detail.put(detail["data"]["result_list"])

    def fetchData(self):
        url = self.url_list[0].format(tour_Id = self.tour_id)
        rounds = self.fetchJson(url, "get", f"{self.tour_id}_Round_list.json")
        if not rounds:
            return
        # 获取所有比赛轮次
        for round in rounds:
            if round_son := round.get("round_son"):
                for round in round_son:
                    self.round_list.put(round["id"])
            else:
                self.round_list.put("p_" + round["roundID"])
        # 根据比赛轮次获取所有比赛场次ID
        multiThread(self.fetchMatchID, self.num_thread)
        # 根据比赛场次ID获取所有比赛结果ID
        multiThread(self.fetchResultID, self.num_thread)
        # 根据比赛结果ID获取结果详细信息
        multiThread(self.fetchDetail, self.num_thread)
 
    def processData(self):
        self.data = []
        while not self.detail.empty():
            detail = self.detail.get()
            self.data.append({k:v for (k,v) in detail.items() 
                                if (k.endswith("heroID") 
                                or k.endswith("playerID") 
                                or k.endswith("result") 
                                or k == "result_id")})

    def run(self):
        for self.tour_id in TOUR_ID:
            self.fetchData()
            self.processData()
            self.saveData(self.filename.format(self.tour_id))


if __name__ == '__main__':
    #TourIDSpider("TourID.json", deadline=20190101)
    PlayerSpider("Player_Info.json")
    HeroSpider("Hero_Info.json")
    MatchSpider("Match_Pick.json", num_thread=32)