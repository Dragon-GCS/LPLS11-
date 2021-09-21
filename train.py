from model import *
import os, json
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from matplotlib import pyplot as plt

AUTO = tf.data.experimental.AUTOTUNE

np.random.seed(1001)
tf.random.set_seed(1001)



def getEDcoder(data):
    encoder = {value: i for i, value in enumerate(data)}
    decoder = {i: value for i, value in enumerate(data)}
    return encoder, decoder

def normalize(df):
    for col in df:
        df[col] = df[col] / df[col].max()
    return df

data = pd.read_csv("./data/data.csv", index_col="result_id")
player_info = pd.read_csv('./data/Player_Info.csv', index_col="player_id")
hero_info = pd.read_csv('./data/Hero_Info.csv', index_col="hero_id")

player_info = normalize(player_info)
hero_info = normalize(hero_info)

player_encoder, player_decoder = getEDcoder(player_info.index)
hero_encoder, hero_decoder = getEDcoder(hero_info.index)

columns = list(data.columns)
for i, col in enumerate(columns):
    if col.startswith("red") and col != "red_result":
        columns[i] = col.replace("red", "blue")
    elif col.startswith("blue"):
        columns[i] = col.replace("blue", "red")
    if 'hero' in col:
        data[col] = data[col].map(lambda x: hero_encoder.get(x, None)  )
    elif 'player' in col:
        data[col] = data[col].map(lambda x: player_encoder.get(x, None))

data = data.dropna().astype("int")
data2 = data[columns]
data2.columns = data.columns
data2["red_result"] = 1 - data["red_result"]
data = pd.concat([data,data2])