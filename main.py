import os

import pandas as pd
from dataProscess import loadJson
import tensorflow as tf
from pprint import pprint as print
from dataProscess import loadJson

tour = ['200', '201', '202', '203',]

def getTeamMember(team_name):
    members = loadJson("./data/json/Teams_member.json")
    if not (team := members.get(team_name)):
        exit(f"Not found team {team_name}")

    tour_id = list(filter(lambda x: x in tour,
                    team.keys())) 
    assert len(tour_id) == 1
    member_list = team[tour_id[0]]
    if len(member_list) > 5:
        members_id = sorted(member_list.keys(), key = lambda key:member_list[key][1], reverse=True)[:5]
    elif len(member_list) == 5:
        members_id = list(member_list.keys())
    else:
        raise ValueError(f"Team {team} Infomation Wrong!")
    names = [member_list[player_id] for player_id in members_id]
    ids = [int(player_id + tour_id[0]) for player_id in members_id]
    return ids, names

player_info = pd.read_csv('./data/Player_Info.csv', index_col="player_id")

def getEDcoder(data):
    encoder = {value: i for i, value in enumerate(data)}
    decoder = {i: value for i, value in enumerate(data)}
    return encoder, decoder
player_encoder, player_decoder = getEDcoder(player_info.index)

def encode(data, encode):
    return [encode[item] for item in data]

def predict(teamA, teamB):
    teamA_ids, teamA_names = getTeamMember(teamA)
    teamB_ids, teamB_names = getTeamMember(teamB)
    inputs = tf.constant(encode(teamA_ids, player_encoder) + encode(teamB_ids, player_encoder), dtype="int32")
    inputs = tf.reshape(inputs, [1,-1])
    model = tf.keras.models.load_model("./model/model_loss-0.5534_accu-0.7135_valLoss-0.5813_valAccu-0.6977.h5")
    result = model(inputs)
    score = tf.argmax(result,axis=1).numpy()[0]
    output = f"{teamA:^9s}: {[name[0] for name in teamA_names]}\n" \
             f"{teamB:^9s}: {[name[0] for name in teamB_names]}\n" \
             f"{'Predict':^9s}: {score}:{1-score} {result[0][score]:.2%}"

    print(output)

if __name__ == '__main__':
    getTeamMember()
    while True:
        teamA, teamB = input("请输入需要预测的两个队伍名, 用空格隔开:\n").split(" ")
        predict(teamA, teamB)