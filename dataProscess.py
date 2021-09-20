import json
import os
import pandas as pd
from Spiders import JSON_DIR, DATA_DIR

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
    """整理选手或英雄信息"""
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


def getIDs(mode="Player"):
    """整理选手、英雄与对应的ID"""
    filename = os.path.join(JSON_DIR, f"{mode}_Ids.json")
    if os.path.isfile(filename):
        return loadJson(filename)
    else:
        data = {}
        for file in [os.path.join(JSON_DIR, f) for f in os.listdir(JSON_DIR) if f.endswith(f"{mode}_Info.json")]:
            for item in loadJson(file):
                name = item[f"{mode.lower()}_name"]
                id = item[f"{mode.lower()}_id"]
                if "tournament_id" in item:
                    id += item["tournament_id"]
                if "position_id" in item and mode == "Hero":
                    id += item["position_id"]
                if not (record := data.get(name, [])) or id not in set(record):
                    record.append(id)
                    data[name] = record

        with open(filename, "w") as f:
            json.dump(data, f)
        return data


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
            
    df.to_csv(filename, index=None, columns=columns)


if __name__ == '__main__':
    #resultToCSV(os.path.join(DATA_DIR, "data.csv"))
    #collectInfo("Player")
    #collectInfo("Hero")
    getIDs("Player")
    getIDs("Hero")
