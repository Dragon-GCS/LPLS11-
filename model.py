import tensorflow as tf
import pandas as pd
from tensorflow import keras

player_info = pd.read_csv("./data/Player_Info.csv", index_col="player_id")
for col in player_info.columns:
    player_info[col] /= player_info[col].max()
player_info = player_info.values

class PlayerEmbedding(keras.layers.Embedding):
    def __init__(self):
        player_initializer = keras.initializers.Constant(value=player_info)
        input_dim = player_info.shape[0]
        output_dim = player_info.shape[1]
        super(PlayerEmbedding, self).__init__(input_dim = input_dim, output_dim = output_dim, 
                                              embeddings_initializer=player_initializer, trainable=False)
        
class BaseModel(tf.keras.Model):
    def __init__(self, dim, drop):
        super(BaseModel, self).__init__()
        self.dim = dim
        self.drop = drop
        
        self.dense1 = keras.layers.Dense(self.dim, activation="relu")
        self.dense2 = keras.layers.Dense(self.dim, activation="relu")
        self.out_dense = keras.layers.Dense(1)
    
    def call(self, inputs):
        x = inputs
        x = keras.layers.Flatten()(x)

        x = self.dense1(x)
        x = keras.layers.Dropout(self.drop)(x)

        x = self.dense2(x)
        x = keras.layers.Dropout(self.drop)(x)

        out = self.out_dense(x)
        return out

class PlayerOnlyModel(tf.keras.Model):

    def __init__(self, dim = 64, drop=0.1):
        super(PlayerOnlyModel, self).__init__()
        self.emb = PlayerEmbedding()
        self.blue_model = BaseModel(dim, drop)
        #self.red_model = BaseModel(dim, drop)
        
        
    def call(self, inputs):
        red = self.emb(inputs[:,:5])
        blue = self.emb(inputs[:,5:])
        
        red_out = self.blue_model(red)
        blue_out = self.blue_model(blue)
        
        x = tf.concat([red_out, blue_out], axis=-1)
        out = keras.layers.Softmax()(x)
        return out