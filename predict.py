from data_spider_process.config import DATA_DIR
from model import *
import json
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf



TOUR = ('200', '201', '202', '203')
PLAYER_ENCODER = os.path.join(DATA_DIR, "Player_Encoder.json")
HERO_ENCODER = os.path.join(DATA_DIR, "Hero_Encoder.json")
PRETRAINED_MODEL = "./model/playerOnlySelfAtten_loss-0.5440_accuracy-0.7169_valLoss-0.5447_valaccuracy-0.7345.h5"


def getTeamMember(team_name):
    with open("./data/Teams_member.json") as f:
        members = json.load(f)

    if not (team := members.get(team_name)):
        exit(f"Not found team {team_name}")

    member_list = None
    for tour in team:
        if tour in TOUR:
            member_list = team[tour]
            break
    if not member_list:
        exit(f"Not found team {team_name}")

    if len(member_list) > 5:
        members_id = sorted(member_list.keys(), key = lambda key:member_list[key][1], reverse=True)[:5]
    elif len(member_list) == 5:
        members_id = list(member_list.keys())
    else:
        raise ValueError(f"Team {team} Infomation Wrong!")

    names = [member_list[player_id] for player_id in members_id]
    ids = [player_id + tour for player_id in members_id]
    return ids, names


def getEDcoder(file):
    with open(file) as f:
        return json.load(f)


def encode(data, encoder):
    return [encoder[item] for item in data]

def predict(teamA, teamB):
    teamA_ids, teamA_names = getTeamMember(teamA)
    teamB_ids, teamB_names = getTeamMember(teamB)

    player_encoder = getEDcoder(PLAYER_ENCODER)

    inputs = tf.constant(encode(teamA_ids, player_encoder) + encode(teamB_ids, player_encoder))

    inputs = tf.reshape(inputs, [1,-1])
    model = PlayerOnlyModel()
    model.build([None, 10])
    model.load_weights(PRETRAINED_MODEL)
    result = model(inputs)

    return teamA_names, teamB_names, result[0]

if __name__ == '__main__':
    A = ["DK", "FPX", "RGE"]
    B = ["EDG", "100", "T1"]
    C = ["FNC", "RNG"]
    D = ["MAD", "GEN", "TL"]
    
    match = {"A组":A, "B组":B, "C组":C, "D组":D}
    for group in match:
        print(group)
        for i in range(len(match[group]) - 1):
            for j in range(i+1, len(match[group])):
                teamA = match[group][i]
                teamB = match[group][j]
                _, _, result = predict(teamA, teamB)
                print(f"{teamA} vs {teamB}:\t", end="")
                if result[0] > result[1]:
                    print(f"0:1\t胜率：{result[0]:.2%}")
                else:
                    print(f"1:0\t胜率：{result[1]:.2%}")
    LPL = ["EDG", "FPX", "RNG", "LNG"]
    LCK = ["DK", "GEN", "T1","HLE"]
    LCS = ["MAD", "FNC", "RGE"]
    LEC = ["100", "TL", "C9"]
    print("    \t", end="")
    for other in LCK + LCS + LEC:
        print(f"{other:^6s}", end="\t")
    print()
    for team in LPL:
        print(team, end="\t")
        for other in LCK + LCS + LEC:
            _, _, result = predict(team, other)
            print(f"{result[1]:.2%}", end="\t")
        print()