import json
import os
import pandas as pd

from .config import JSON_DIR, DATA_DIR

INCLUDE = {
    "Player": (
        "player_id",
        "tournament_id",
        "PLAYS_TIMES", 
        "MINUTE_ECONOMIC",
        "OFFERED_RATE",
        "MINUTE_HITS",
        "MINUTE_DAMAGEDEALT",
        "DAMAGEDEALT_RATE",
        "MINUTE_DAMAGETAKEN",
        "DAMAGETAKEN_RATE",
        "MINUTE_WARDSPLACED",
        "MINUTE_WARDKILLED",
        "AVERAGE_KILLS",
        "AVERAGE_ASSISTS",
        "AVERAGE_DEATHS",
        "MVP",
        "VICTORY_RATE"),
    "Hero":(
        "hero_id",
        "tournament_id",
        "position_id",
        "appear_count",
        "prohibit_count",
        "victory_count",
        "AVERAGE_KILLS",
        "AVERAGE_ASSISTS",
        "AVERAGE_DEATHS",
    )}

HERO_POS = {"a":"3","b":"4","c":"2","d":"1","e":"5",}

def loadJson(filename):
    with open(filename) as f:
        return(json.load(f))


def collectInfo(mode = "Player"):
    """整理选手或英雄数据保存至csv"""
    data = []
    for file in os.listdir(JSON_DIR):
        if file.endswith(f"{mode}_Info.json"):
            for player in loadJson(os.path.join(JSON_DIR, file)):
                temp = {k:player[k] for k in INCLUDE[mode]}
                temp[f"{mode.lower()}_id"] = temp[f"{mode.lower()}_id"] + temp["tournament_id"]
                del temp["tournament_id"]
                if mode == "Hero":
                    temp[f"{mode.lower()}_id"] = temp[f"{mode.lower()}_id"] + temp["position_id"]
                    del temp["position_id"]
                data.append(temp)
    pd.DataFrame(data).drop_duplicates().to_csv(os.path.join(DATA_DIR,f"{mode}_Info.csv"), index=False)


def resultToCSV(filename):
    """整理比赛结果数据保存至csv"""
    data = []    
    for file in [os.path.join(JSON_DIR, f) for f in os.listdir(JSON_DIR) if f.endswith("Pick.json")]:
        for item in (content := loadJson(file)):
            for key,value in item.items():
                if 'heroID' in key:
                    pfix = file.split("/")[-1].split("_")[0] + HERO_POS[key.split("_")[2]]  # 赛区ID + 位置ID    
                    item[key] = value + pfix
                if 'playerID' in key:
                    pfix = file.split("/")[-1].split("_")[0]
                    #item[key] = playerID[value + pfix] + pfix
                    item[key] += file.split("/")[-1].split("_")[0]

        data += content
    columns=["result_id","red_result"]
    df = pd.DataFrame(data)
    for i in df.columns:
        if "player" in i:
            columns.append(i)

    for i in df.columns:
        if "hero" in i:
            columns.append(i)

    df.to_csv(os.path.join(DATA_DIR, filename), index=None, columns=columns)

def getTeamMember():
    if os.path.isfile(filename:=os.path.join(DATA_DIR, f"Teams_member.json")):
        return loadJson(filename)
    data = {}
    for file in [os.path.join(JSON_DIR, f) for f in os.listdir(JSON_DIR) if f.endswith(f"Player_Info.json")]:
        for item in loadJson(file):
            # 记录队伍名
            team_name = item["team_name"]
            content = data.get(team_name, {})
            # 记录队伍id
            content["team_id"] = item.get("team_id")
            tour_id = item.get("tournament_id")
            # 记录队员信息
            content[tour_id] = content.get(tour_id, {})
            player_name = item.get("player_name")
            player_id = item.get("player_id")
            play_times = item.get("PLAYS_TIMES")
            content[tour_id][player_id] = (player_name, play_times)

            data[team_name] = content
    with open(filename, "w") as f:
        json.dump(data, f)
    return data

def nameToID(mode="Player"):
    if os.path.isfile(filename:=os.path.join(DATA_DIR, f"{mode}NameToIDs.json")):
        return loadJson(filename)
    else:
        data = {}
        for file in [os.path.join(JSON_DIR, f) for f in os.listdir(JSON_DIR) if f.endswith(f"{mode}_Info.json")]:
            for item in loadJson(file):
                name = item[f"{mode.lower()}_name"]
                ids = data.get(name, [])
                item_id = "_".join((item[f"{mode.lower()}_id"], item["tournament_id"]))

                if item_id not in ids:
                    ids.append(item_id)
                data[name] = ids
        with open(filename, "w") as f:
            json.dump(data, f)
        return data


if __name__ == '__main__':
    resultToCSV("data.csv")
    collectInfo("Player")
    collectInfo("Hero")
    getTeamMember()
    nameToID("Player")
    nameToID("Hero")
