from matplotlib.pyplot import axis
import tensorflow as tf
import pandas as pd
from tensorflow import keras


class PlayerEmbedding(keras.layers.Embedding):
    def __init__(self):
        init_weight = self.get_default_weight()
        player_initializer = keras.initializers.Constant(value=init_weight)
        input_dim = init_weight.shape[0]
        output_dim = init_weight.shape[1]
        super(PlayerEmbedding, self).__init__(input_dim = input_dim, output_dim = output_dim, 
                                              embeddings_initializer=player_initializer, trainable=False)


    def get_default_weight(self):
        data = self.raw_data()
        for col in data.columns:
            data[col] /= data[col].max()
        return data.values


    def raw_data(self):
        return pd.read_csv("./data/Player_Info.csv", index_col="player_id")


class HeroEmbedding(PlayerEmbedding):
    def raw_data(self):
        return pd.read_csv("./data/Hero_Info.csv", index_col="hero_id")


class Attention(keras.layers.Layer):
    def __init__(self) -> None:
        super(Attention, self).__init__()
        self.atten_k = keras.layers.Dense(32, activation="tanh")
        self.atten_q = keras.layers.Dense(32, activation="tanh")
        self.atten_v = keras.layers.Dense(32, activation="tanh")


    def call(self, q, k ,v):
        q = self.atten_q(q)
        k = self.atten_k(k)
        v = self.atten_v(v)
        atten = tf.nn.softmax(tf.matmul(q, k, transpose_b=True), axis=-1)
        atten =tf.expand_dims(tf.transpose(atten, [0,2,1]),-1)
        v = tf.expand_dims(v, -2)
        return tf.reduce_sum(v * atten,axis=-3)


class BaseModel(keras.Model):
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


class PlayerOnlyModel(keras.Model):
    def __init__(self, dim = 64, drop=0.2):
        super(PlayerOnlyModel, self).__init__()
        self.emb = PlayerEmbedding()
        self.base_model = BaseModel(dim, drop)
        self.attention = Attention()


    def call(self, inputs):
        red = self.emb(inputs[:,:5])
        blue = self.emb(inputs[:,5:])
        
        red_ = self.attention(red, red, red)
        blue_ = self.attention(blue, blue, blue)

        red_out = self.base_model(red_)
        blue_out = self.base_model(blue_)
        
        x = tf.concat([red_out, blue_out], axis=-1)
        out = keras.layers.Softmax()(x)
        return out


class PlayerHeroModel(keras.Model):
    def __init__(self, dim = 64, drop=0.1):
        super(PlayerHeroModel, self).__init__()
        self.dim = dim
        self.player_emb = PlayerEmbedding()
        self.hero_emb = HeroEmbedding()
        self.base_model = BaseModel(dim, drop)
        self.play_attention = Attention()
        self.hero_attention = Attention()

    def call(self, inputs):
        red_player = self.player_emb(inputs[:,:5])
        blue_player = self.player_emb(inputs[:,5:10])
        red_heros = self.hero_emb(inputs[:,10:15])
        blue_heros = self.hero_emb(inputs[:,15:20])

        red_player_ = self.play_attention(red_player, red_player, red_player)
        blue_player_ = self.play_attention(blue_player, blue_player, blue_player)

        red_heros_ = self.hero_attention(red_heros, red_heros, red_heros)
        blue_heros_ = self.hero_attention(blue_heros, blue_heros, blue_heros)
    
        red = tf.concat([red_player_, red_heros_], axis=-1)
        blue = tf.concat([blue_player_, blue_heros_], axis=-1)

        red_out = self.base_model(red)
        blue_out = self.base_model(blue)
        
        x = tf.concat([red_out, blue_out], axis=-1)
        out = keras.layers.Softmax()(x)
        return out
