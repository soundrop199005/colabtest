# -*- coding: utf-8 -*-
"""Level1_TrainModel.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IojS5IFx5T0t24ZWnWHNQGLd3dSWoFh-

# Import Library & Data
"""

#General imports
from __future__ import print_function
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import progressbar

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
import gc
# Keras imports
import keras
import random
from keras.preprocessing.image import load_img
from keras.models import Sequential, Model
from keras.optimizers import *
from tensorflow.keras.utils import to_categorical
import keras.backend as K
import tensorflow as tf
# application (model) imports
from keras import applications
#from keras.applications.inception_v3 import preprocess_input
from keras.layers import Dense
import time
import math

# import data
def prepare_train_val_data(val_portion):
  # downloading cifar data
  (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
  assert x_train.shape == (50000, 32, 32, 3)
  assert x_test.shape == (10000, 32, 32, 3)
  assert y_train.shape == (50000, 1)
  assert y_test.shape == (10000, 1)
  # one hot encoding
  print("First 5 training labels: ", y_train[:5])
  y_train = to_categorical(y_train, 10)
  y_test = to_categorical(y_test, 10)
  print("First 5 training lables as one-hot encoded vectors:\n", y_train[:5])
  print(y_train.shape)
  print(y_test.shape)
  trainX, valX, trainY, valY = train_test_split(x_train, y_train, test_size=val_portion, random_state=42, shuffle = True, stratify=y_train)
  [print(each.shape) for each in [trainX, trainY, valX, valY]]
  return trainX, trainY, valX, valY



# sample to have a look

def sample_show(x,y):
  # random generate a number from 0 to length-1
  index_sa = random.randint(0, len(y)-1)
  print(index_sa)
  plt.imshow(x[index_sa])
  print(y[index_sa])

"""## Build Model"""

def asem_model(alp,weight_decay) -> keras.Sequential:
# input and preprocess
  inputs = keras.Input(shape=(32, 32, 3))
  preprocess_input = applications.mobilenet_v2.preprocess_input
  x = preprocess_input(inputs)
# use alpha to construct a mobilenetV2 model
  base_model_tune_hyp = applications.MobileNetV2(
  input_shape=(32,32,3),
  alpha=alp,
  include_top=True,
  weights= None,
  input_tensor=None,
  pooling=None,
  classes=10,
  classifier_activation="softmax")
# add weight decay
  alpha = weight_decay  # weight decay coefficient
  for layer in base_model_tune_hyp.layers:
      if isinstance(layer, keras.layers.Conv2D) or isinstance(layer, keras.layers.Dense):
          layer.add_loss(lambda: keras.regularizers.l2(alpha)(layer.kernel))
      if hasattr(layer, 'bias_regularizer') and layer.use_bias:
          layer.add_loss(lambda: keras.regularizers.l2(alpha)(layer.bias))
# assemble the model
  y = base_model_tune_hyp(inputs = x)
  model = tf.keras.Model(inputs, y)
  print(model.summary())
  return model

"""## Hyper Para Tuning"""

def plot_loss_accuracy_s(history,filename):
    historydf = pd.DataFrame(history.history, index=history.epoch)
    plt.figure(figsize=(8, 6))
    historydf.plot(ylim=(0, max(1, historydf.values.max())))
    loss = min(history.history['val_loss'])
    mylist1 = history.history['val_loss']
    ind = mylist1.index(min(mylist1))
    acc =history.history['val_accuracy'][ind]
    plt.title('Val Loss: %.3f, Val Accuracy: %.3f' % (loss, acc))
    plt.savefig(filename)

"""Define a function for hyper parameter tuning more easily"""

def hyp_tuning(alpha, learning_rate, momentum, weight_decay, n_epoch, directory,train_X, train_Y,val_X,val_Y):
  # construct model
  model = asem_model(alpha,weight_decay)
  # learning rate schedule
  lr_schedule = keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=learning_rate,
    decay_steps=50,
    decay_rate=0.98)
  # optimizer
  opt = tf.keras.optimizers.experimental.RMSprop(
      learning_rate=lr_schedule,
      rho=0.9,
      momentum=momentum,
      epsilon=1e-07,
      centered=False,
      # we used weight decay in the model by L2 norm instead
      weight_decay=0,
      clipnorm=None,
      clipvalue=None,
      global_clipnorm=None,
      use_ema=False,
      ema_momentum=0.99,
      ema_overwrite_frequency=100,
      jit_compile=True,
      name='RMSprop'
  )
  parent_dir = os.path.join(directory, 'base_model_mobileNetV2_alpha_%.3f_lr_%.7f_m_%.2f_wd_%.9f'%(alpha,learning_rate,momentum,weight_decay))
  # os.mkdir(parent_dir)
  if not os.path.exists(parent_dir):
    os.mkdir(parent_dir)
  print(parent_dir)
  checkpoint_path = os.path.join(parent_dir, 'model.h5')
  my_callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, verbose=0, mode='min'),
    tf.keras.callbacks.ModelCheckpoint(checkpoint_path, save_best_only=True, monitor='val_loss', mode='min')]
  # compile model
  model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
  # fit model
  history = model.fit(train_X, train_Y, validation_data=(val_X,val_Y), epochs=n_epoch, verbose=True, batch_size=64, shuffle=True,callbacks= my_callbacks)
  plot_loss_accuracy_s(history,os.path.join(parent_dir,'training_plot.png'))
  return min(history.history['val_loss'])

def train_best(dir,trainX, trainY, valX, valY):
  alp = 0.9
  lr = 0.0005
  m = 0.9
  wd = 0
  n_e = 50
  hyp_tuning(alpha = alp, learning_rate=lr, momentum=m, weight_decay = wd, n_epoch=n_e, directory = dir, train_X=trainX, train_Y = trainY, val_X = valX,val_Y = valY)