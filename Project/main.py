#Install
!pip install nlpaug

#Declaration
import os
import gc
import time
import regex as re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import keras
import numpy as np

from sklearn import preprocessing
from sklearn.utils import class_weight
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

from numpy import asarray
from numpy import ones
from numpy import zeros
import tensorflow as tf
import tensorflow_datasets as tfds
import tensorflow.keras.backend as K
from tensorboard.plugins.hparams import api as hp
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import backend
from keras.layers import Conv1D, MaxPooling1D, Embedding, Dropout
from keras.optimizers import Adam
from keras.models import Model, Input, Sequential
from keras.layers import Dense, Input, LSTM, SimpleRNN, Embedding, Dropout, SpatialDropout1D, Activation, Conv1D,GRU, Reshape
from keras.layers import Conv1D, Bidirectional, GlobalMaxPool1D, MaxPooling1D, BatchNormalization, Add, Flatten
from keras.layers import GlobalMaxPooling1D, GlobalAveragePooling1D, concatenate, SpatialDropout1D
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.callbacks import CSVLogger

from tensorflow.python.distribute import distribution_strategy_context
from tensorflow.python.eager import context
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import ops
from tensorflow.python.framework import sparse_tensor
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import check_ops
from tensorflow.python.ops import confusion_matrix
from tensorflow.python.ops import control_flow_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import nn
from tensorflow.python.ops import sets
from tensorflow.python.ops import sparse_ops
from tensorflow.python.ops import state_ops
from tensorflow.python.ops import variable_scope
from tensorflow.python.ops import weights_broadcast_ops
from tensorflow.python.platform import tf_logging as logging
from tensorflow.python.util.deprecation import deprecated
from tensorflow.python.util.tf_export import tf_export
import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
import nlpaug.flow as nafc
import transformers
from nlpaug.util import Action

from datetime import datetime
from imblearn.over_sampling import SMOTE
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


#Setup Project Parameters
DataAugmentation = True
DataAugThreshold = 30000
DataFilePath = "/content/drive/My Drive/Multilabel/"
DataFileName = "XXX" #Replace with Project File Name
FileType = ".csv"
MAX_SEQUENCE_LENGTH = 300
EMBEDDING_DIM =100
LoadDataAugFromFile = False
Learningrate = 0.001


#Loading Data

totaldata = pd.read_csv(DataFilePath + DataFileName + FileType, error_bad_lines=False, index_col=False, dtype='unicode', encoding='latin-1',low_memory=False).sample(frac=1)
totaldata = totaldata.rename(columns = {'ï»¿RepoID': 'RepoID'}, inplace = False)
totaldata['CreatedDate']=pd.to_datetime(totaldata['CreatedDate'])
totaldata = totaldata.sort_values(by=['CreatedDate']) 


#Cross Validation in TimeSeries
totalnoofrecords = len(totaldata)
split = int(totalnoofrecords/5)
print(split)
#for i in [1, 2, 3, 4, 5]:
for i in [5]:
   currentsplit = split * i;
   data = totaldata[:int(currentsplit)]
   Cleandata(data)
   if DataAugmentation == True:
     traindata, tk_context, x_train_context,x_train_AST, dev_y_train, btype_y_train, x_test_context, x_test_AST, dev_y_test, btype_y_test, dev_labels_map, dev_inv_labels_map, btype_labels_map, btype_inv_labels_map = SplitTrainTestDataForMultiLabelWithDataAugmentation(data,str(i))
   else: 
     tk_context, x_train_context,x_train_AST, dev_y_train, btype_y_train, x_test_context, x_test_AST, dev_y_test, btype_y_test, dev_labels_map, dev_inv_labels_map, btype_labels_map, btype_inv_labels_map = SplitTrainTestData(data)
   tk_context, tk_AST, x_train_context,x_train_AST, x_test_context, x_test_AST = Tokenize(tk_context, x_train_context,x_train_AST, x_test_context, x_test_AST)
   print('finished iteration', i)