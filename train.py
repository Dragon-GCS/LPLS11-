import os
import argparse
import pandas as pd
import numpy as np
import tensorflow as tf

from matplotlib import pyplot as plt
from model import *

AUTO = tf.data.experimental.AUTOTUNE
BATCH = 64
VAL_SPLIT = 0.05
EPOCH = 80

optimizer = keras.optimizers.Adam()
loss = keras.losses.SparseCategoricalCrossentropy()
metric = "accuracy"

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

def train_val_spilt(df):
    val_data = df.sample(frac=VAL_SPLIT)
    train_data = df.drop(val_data.index)
    return train_data, val_data

def processData(data, include_hero = False):
    if include_hero:
        data = tf.data.Dataset.from_tensor_slices(((data[:,1:]),data[:,0]))
    else:
        data = tf.data.Dataset.from_tensor_slices(((data[:,1:11]),data[:,0]))
    data = data.shuffle(2000).batch(BATCH).prefetch(AUTO)
    return data

def generateTrainData(matchfile, player_file, hero_file = None):
    data = pd.read_csv(matchfile, index_col="result_id")

    player_info = pd.read_csv(player_file, index_col="player_id")
    player_info = normalize(player_info)
    player_encoder, player_decoder = getEDcoder(player_info.index)

    if hero_file:
        hero_info = pd.read_csv(hero_file, index_col="hero_id")
        hero_info = normalize(hero_info)
        hero_encoder, hero_decoder = getEDcoder(hero_info.index)


    # expand train data
    columns = list(data.columns)
    for i, col in enumerate(columns):
        if col.startswith("red") and col != "red_result":
            columns[i] = col.replace("red", "blue")
        elif col.startswith("blue"):
            columns[i] = col.replace("blue", "red")
        if 'hero' in col and hero_file:
            data[col] = data[col].map(lambda x: hero_encoder.get(x, None)  )
        elif 'player' in col:
            data[col] = data[col].map(lambda x: player_encoder.get(x, None))

    data = data.dropna().astype("int32")
    data2 = data[columns]
    data2.columns = data.columns
    data2["red_result"] = 1 - data["red_result"]
    data = pd.concat([data,data2])
    
    train_data, val_data = train_val_spilt(data)
    val_data = processData(val_data.values, hero_file)
    train_data = processData(train_data.values, hero_file)

    return train_data, val_data

def plot_history(history):
    plt.figure(figsize=(15,7))
    plt.subplot(1,2,1)
    plt.title("Loss")
    plt.plot(history.history['loss'][2:])
    plt.plot(history.history['val_loss'][2:])
    plt.legend(['train', 'val'])       
    plt.subplot(1,2,2)
    plt.title("Accuracy")
    plt.plot(history.history[metric][2:])
    plt.plot(history.history['val_' + metric][2:])
    plt.legend(['train', 'val']) 

def train(model, train_data, val_data, epoch, plot=True, save_name="",):
    model.compile(optimizer = optimizer,
                  loss = loss,
                  metrics = metric)
    history = model.fit(train_data, validation_data=val_data,epochs=epoch)

    if save_name:
        filename = os.path.join(MODEL_DIR, save_name) + \
                f"loss-{history.history['loss'][-1]:.4f}_" \
                f"{metric}-{history.history[f'{metric}'][-1]:.4f}_"\
                f"valLoss-{history.history['val_loss'][-1]:.4f}_"\
                f"val{metric}-{history.history[f'val_{metric}'][-1]:.4f}.h5"
        model.save_weights(filename)

    if plot:
        plot_history(history)
        plt.show()

    
if __name__ == '__main__':
    from data_spider_process.config import ROOT
    MODEL_DIR = os.path.join(ROOT, "model")
    if not os.path.isdir(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    parser = argparse.ArgumentParser()
    parser.add_argument("-hero",  action="store_true", help="use hero info")
    parser.add_argument("-save",  default=None, help="save the model")
    parser.add_argument("-epoch",  default=EPOCH, help="epochs to train", type=int)
    args = parser.parse_args()
    
    match_file = "./data/data.csv"
    playerInfo_file = "./data/Player_Info.csv"
    heroInfo_file = ""
    model = PlayerOnlyModel()
    if args.hero:
        heroInfo_file = "./data/Hero_Info.csv"
        model = PlayerHeroModel()

    train_data, val_data = generateTrainData(match_file,playerInfo_file, hero_file=heroInfo_file)

    train(model, train_data, val_data, args.epoch, save_name=args.save)
