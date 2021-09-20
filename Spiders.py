# coding = utf-8
# Dragon's Python3.8 code
# Created at 2021/09/12 10:03
# Edit with VS Code
# Fetch data for predict S11 World Final's Champion

from abc import ABC, abstractclassmethod
from urllib import request, parse
from functools import wraps
from pprint import pprint
import pandas as pd
import json
import os


TEMP_DIR = "./data/temp"
if not os.path.isdir(TEMP_DIR):
    os.makedirs(TEMP_DIR)

JSON_DIR = "./data/json/"
if not os.path.isdir(JSON_DIR):
    os.makedirs(JSON_DIR)

DATA_DIR = "./data"
if not os.path.isdir(DATA_DIR):
    os.makedirs(DATA_DIR)

HEADER = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "cookie": "cookie: Hm_lvt_7d06c05f2674b5f5fffa6500f4e9da89=1631376039; tgw_l7_route=44a8ecb0130e9cd4b0b2316b71c7a866; PHPSESSID=5ebelmq7p4mbtm9pn71bsvl6j6; Hm_lpvt_7d06c05f2674b5f5fffa6500f4e9da89=1631376664",
}

SAVE_TEMP = True

TOUR_ID = {
    '103': ['2019LPL春季赛', 20190114],
    '104': ['2019LCK春季赛', 20190116],
    '105': ['2019LCS春季赛', 20190126],
    '106': ['2019LEC春季赛', 20190118],
    
    '120': ['2019LPL夏季赛', 20190601],
    '122': ['2019LCS夏季赛', 20190601],
    '123': ['2019LCK夏季赛', 20190605],
    '126': ['2019LEC夏季赛', 20190607],
    
    '152': ['2020LPL春季赛', 20200113],
    '153': ['2020LCK春季赛', 20200205],
    '157': ['2020LCS春季赛', 20200126],
    '158': ['2020LEC春季赛', 20200124],

    '170': ['2020LCS夏季赛', 20200612],
    '171': ['2020LEC夏季赛', 20200612],
    '172': ['2020LPL夏季赛', 20200605],
    '173': ['2020LCK夏季赛', 20200617],
    '177': ['S10LPL资格赛', 20200828],
    '179': ['S10LCK资格赛', 20200907],

    '189': ['2021LCS春季赛', 20210205],
    '190': ['2021LEC春季赛', 20210122],
    '191': ['2021LPL春季赛', 20210109],
    '192': ['2021LCK春季赛', 20210113],

    '200': ['2021LPL夏季赛', 20210607],
    '201': ['2021LCK夏季赛', 20210609],
    '202': ['2021LCS夏季赛', 20210605],
    '203': ['2021LEC夏季赛', 20210611],
    '208': ['S11LPL资格赛', 20210903],
    '209': ['S11LCK资格赛', 20210831]}

def processTip(func, arg=""):
    print(arg) if arg else None
    @wraps(func)
    def process(*args, **kwargs):
        spider_name = args[0].__class__.__name__
        print("{:=^100}".format(f"Spider: {spider_name} Task: {func.__name__} start"))
        result = func(*args, **kwargs)
        print("{:=^100}\n".format(f"Spider: {spider_name} Task: {func.__name__} end=="))
        return result
    return process


class Spider(ABC):
    url: str
    post_data: dict

    def __init__(self, filename: str = None, autorun: bool = True) -> None:
        self.filename = filename
        if autorun:
            self.run()
    
    @abstractclassmethod
    def run(self):
        pass

    @property
    def temp_dir(self):
        return os.path.join(TEMP_DIR, "_".join([self.__class__.__name__, self.temp_name]))

    @property
    def _post_data(self):
        if self.post_data:
            return parse.urlencode(self.post_data).encode()

    def fetchJson(self, method: str = 'post', temp_name:str = "temp.json", save_temp: bool = SAVE_TEMP) -> None:
        """
        Connet the url and get the json data
        """
        self.temp_name = temp_name
        if not os.path.isfile(temp:=self.temp_dir):
            req = request.Request(self.url, headers=HEADER)
            try:
                if method == "post":
                    self.response = request.urlopen(req, self._post_data).read()
                elif method == "get":
                    self.response = request.urlopen(req).read()
            except Exception as e:
                print(e)
                print("Error url:", self.url)
                self.data = None
                return

            if save_temp:
                with open(temp, "wb") as f:
                    f.write(self.response)
            self.data = json.loads(self.response) if self.response else None
        else:
            print(f"Using temp file: {os.path.abspath(temp)}")
            with open(temp, "rb") as f:
                self.data = json.load(f)

    @abstractclassmethod
    def processData(self):
        pass

    def saveData(self) -> None:
        with open(file:=os.path.join(JSON_DIR, self.filename), "w") as f:
            json.dump(self.data, f)
        print(f"Result file saved to '{os.path.abspath(file)}'\n")


class TourIDSpider(Spider):
    url = "https://www.scoregg.com/services/api_url.php"
    post_data = {
        "api_path":"/services/match/tournament_list.php",
        "method":"post",
        "platform":"web",
        "api_version": "9.9.9",}
    
    def __init__(self, filename = "result.json", deadline = 20200101, autorun = True) -> None:
        self.deadline = deadline
        super().__init__(filename, autorun)

    def run(self):
        self.fetchJson()
        self.processData()
        self.saveData()

    @processTip
    def processData(self) -> None:
        self.data = self.data["data"]["list"]
        result = {}
        for id in self.data:
            if (start := id.get("start_date", None)) and (date:=int(start.replace("-", ""))) > self.deadline:
                result[id["tournamentID"]] = (id["name"].replace(" ", ""), date)
        self.data = result


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
    
    def __init__(self, filename: str, autorun: bool=True) -> None:
        self.result_list = []
        self.exlude_item = ("country_id","country_image","player_image","team_image","update_time")
        super().__init__(filename=filename, autorun=autorun)

    def processData(self):
        print(f"Processing file {self.temp_name}")
        self.data = self.data["data"]["data"]["list"]
        for player in self.data:
            for item in self.exlude_item:
                del player[item]
        self.result_list += self.data

    @processTip
    def fetchData(self):
        self.post_data["page"] = "1"
        self.fetchJson(temp_name = f"{self.post_data['tournament_id']}_{self.post_data['type']}_1.json")
        total_num = int(self.data["data"]["data"]["count"])
        data_per_page = len(self.data["data"]["data"]["list"])
        pages = total_num // data_per_page + 1
        print(f"Totol items num: {total_num}")
        self.processData()

        for page in range(2, pages + 1):
            self.post_data["page"] = str(page)
            self.fetchJson(temp_name=f"{self.post_data['tournament_id']}_{self.post_data['type']}_{page}.json")
            self.processData()

        self.data = self.result_list

    def run(self):
        filename = "{}_" + self.filename
        for game_id in TOUR_ID:
            self.post_data["tournament_id"] = game_id
            print(f"{TOUR_ID[game_id][0]} info is fetching")
            self.fetchData()
            self.filename = filename.format(game_id)
            self.saveData()


class HeroSpider(PlayerSpider):
    def run(self):
        self.post_data['type'] = "hero"
        self.exlude_item = ("hero_image", "hero_name_en", "hero_name_tw", "update_time")
        super().run()


class MatchSpider(Spider):
    url_list = (
        "https://img.scoregg.com/tr/{tour_Id}.json",                # GET: RoundId list
        "https://img.scoregg.com/tr_round/{round_sonID}.json",      # GET: matchID list 
        "https://img.scoregg.com/match/resultlist/{matchID}.json",  # GET: result list of a match
        "https://img.scoregg.com/match/result/{resultID}.json",     # GET: result detail
    )
    post_data = None
    
    @processTip
    def fetchData(self):
        # 获取赛程轮次列表
        self.url = self.url_list[0].format(tour_Id=self.tour_id)
        self.fetchJson("get", f"{self.tour_id}_Round_list.json")
        if not self.data:
            return
        print("Start fetch Round_ID\n")
        for item in self.data:
            if round_son := item.get("round_son"):
                for round in round_son:
                    self.round_list.append(round["id"])
            else:
                self.round_list.append("p_" + item["roundID"])
        # 获取所有比赛ID
        print("Start fetch Match_ID\n")
        for round in self.round_list:
            self.url = self.url_list[1].format(round_sonID = round)
            self.fetchJson("get", f"{self.tour_id}_{round}_Match_list.json")
            if not self.data:
                return
            for match in self.data:
                self.match_list.append(match["matchID"])
        # 根据比赛ID获取所有比赛的结果ID
        print("Start fetch Result_ID\n")
        for match in self.match_list:
            self.url = self.url_list[2].format(matchID=match)
            self.fetchJson("get", f"{self.tour_id}_{match}_Match_detail.json")
            if not self.data:
                return
            for result in self.data["data"]:
                self.result_list.append(result["resultID"])
        # 获取比赛结果详细信息
        print("Start fetch Detail_ID\n")
        for result in self.result_list:
            self.url = self.url_list[3].format(resultID=result)
            self.fetchJson("get", f"{self.tour_id}_{result}_Result_detail.json")
            if not self.data:
                return
            self.data["data"]["result_list"]["result_id"] = result
            self.detail.append(self.data["data"]["result_list"])

        self.data = self.detail
        return self.data

    def processData(self):
        for i, data in enumerate(self.data):
            self.data[i] = {k:v for (k,v) in data.items() 
                                if (k.endswith("heroID") 
                                 or k.endswith("playerID") 
                                 or k.endswith("result") 
                                 or k == "result_id")}


    def run(self):
        filename = "{tour_ID}_" + self.filename

        for id in TOUR_ID:
            self.tour_id = id
            self.round_list = []
            self.match_list = []
            self.result_list = []
            self.detail = []
            if self.fetchData():
                self.processData()
                self.filename = filename.format(tour_ID=id)
                self.saveData()
        

if __name__ == '__main__':
    #TourIDSpider("TourID.json", deadline=20190101)
    PlayerSpider("Player_Info.json")
    HeroSpider("Hero_Info.json")
    MatchSpider("Match_Pick.json")
