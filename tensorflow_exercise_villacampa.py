# -*- coding: utf-8 -*-
"""TensorFlow Exercise_Villacampa

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18guWggCf4MdeG4-PZNSz2RQ_iinsqC9m

# Abalone Dataset Training

> **Loading Dataset**
"""

import pandas as pd #importing pandas library 
import numpy as np #importing numpy library 

# Make numpy values easier to read.
np.set_printoptions(precision=3, suppress=True)

import tensorflow as tf #importing tensor flow library 
from tensorflow.keras import layers #importing function layers from tensor flow

#reading abalone dataset using Pandas Dataframe
abalone_train = pd.read_csv(
    "https://storage.googleapis.com/download.tensorflow.org/data/abalone_train.csv",
    names=["Length", "Diameter", "Height", "Whole weight", "Shucked weight",
           "Viscera weight", "Shell weight", "Age"])

abalone_train.head() #displaying abalone dataset limiting to first 5 rows

abalone_features = abalone_train.copy() #assigning abalone dataset features
abalone_labels = abalone_features.pop('Age') #assigning abalone dataset age

abalone_features = np.array(abalone_features) #putting abalone features in a numpy array
abalone_features #displaying abalone features array

# sequantial model groups the linear stack of abalone's dense layers and is then assign to "abalone_model" variable
abalone_model = tf.keras.Sequential([
  layers.Dense(64),
  layers.Dense(1)
])

#compile and use loss function from tf.Keras to compute the quantity that a model should seek to minimize during training
abalone_model.compile(loss = tf.keras.losses.MeanSquaredError(),
                      optimizer = tf.keras.optimizers.Adam())

# Use Model.fit for mapping class indices to the weight
abalone_model.fit(abalone_features, abalone_labels, epochs=10) #trains the model and passes the abalone features and labels to Model.fit

"""> **Data Preprocessing**




"""

normalize = layers.Normalization() #creating layer model normalization 

normalize.adapt(abalone_features) #Adapts normalization layer to abalone features data

#applies the created normalization layer to the model 
norm_abalone_model = tf.keras.Sequential([ #includes normalization layer in the abalone model and assign to variable "norm_abalone_model"
  normalize,
  layers.Dense(64),
  layers.Dense(1)
])

norm_abalone_model.compile(loss = tf.keras.losses.MeanSquaredError(),
                           optimizer = tf.keras.optimizers.Adam())

norm_abalone_model.fit(abalone_features, abalone_labels, epochs=10)

"""# Titanic Dataset Forescasting

```
The code shows an example how to handle mixed data types in using TensorFlow
```
"""

titanic = pd.read_csv("https://storage.googleapis.com/tf-datasets/titanic/train.csv") #importing titanic dataset using Pandas dataframe
titanic.head() #displaying titanic dataframe with limit to 5 rows only

titanic_features = titanic.copy() #creates titanic data copy and assigns to variable "titanic_features"
titanic_labels = titanic_features.pop('survived') #removes the 'survived' column from the features dataframe and assigns the new df to "titanic_labels"

# Create a symbolic input
input = tf.keras.Input(shape=(), dtype=tf.float32)

# Perform a calculation using the input
result = 2*input + 1

# the result doesn't have a value
result

calc = tf.keras.Model(inputs=input, outputs=result)

print(calc(1).numpy())
print(calc(2).numpy())

#creating a set of symbolic tf.Keras.Input objects for building the preprocessing model
inputs = {}

for name, column in titanic_features.items():
  dtype = column.dtype
  if dtype == object:
    dtype = tf.string
  else:
    dtype = tf.float32

  inputs[name] = tf.keras.Input(shape=(1,), name=name, dtype=dtype)

inputs #displaying inputs

#concatenating numeric inputs and run them with a normalization layer
numeric_inputs = {name:input for name,input in inputs.items()
                  if input.dtype==tf.float32}

x = layers.Concatenate()(list(numeric_inputs.values()))
norm = layers.Normalization()
norm.adapt(np.array(titanic[numeric_inputs.keys()]))
all_numeric_inputs = norm(x)

all_numeric_inputs #displaying all numeric inputs

preprocessed_inputs = [all_numeric_inputs] #collecting all symbolic preprocessing results for later use

for name, input in inputs.items():
  if input.dtype == tf.float32:
    continue
  
  lookup = layers.StringLookup(vocabulary=np.unique(titanic_features[name])) #maps strings to integer indices in a vocalbulary
  one_hot = layers.CategoryEncoding(num_tokens=lookup.vocabulary_size()) #converts the indices into float32 data that is approrpiate for the model

  x = lookup(input)
  x = one_hot(x)
  preprocessed_inputs.append(x)

preprocessed_inputs_cat = layers.Concatenate()(preprocessed_inputs) #concatenated layers of preprocessed inputs that are assigned to the "preprocessed_inputs_cat" variable

titanic_preprocessing = tf.keras.Model(inputs, preprocessed_inputs_cat) #created the model for preprocessing using the inputs and preprocessed inputs

tf.keras.utils.plot_model(model = titanic_preprocessing , rankdir="LR", dpi=72, show_shapes=True) #plots the titanic_preprocessing model 
# with the digraphs direction set to LR (a --> b --> c;)

#converting titanic_features dataframe into a dictionary of tensors and assigning it to the "titanic_features_dict" variable
titanic_features_dict = {name: np.array(value) 
                         for name, value in titanic_features.items()}

features_dict = {name:values[:1] for name, values in titanic_features_dict.items()} #slices the first training example and assigns it to the "features_dict" var
titanic_preprocessing(features_dict) #passes the example to the preprocessing model

#creating the model
def titanic_model(preprocessing_head, inputs): #defining titanic_models function with parameters: preprocessing_head and inputs
  body = tf.keras.Sequential([
    layers.Dense(64),
    layers.Dense(1)
  ])

  preprocessed_inputs = preprocessing_head(inputs)
  result = body(preprocessed_inputs)
  model = tf.keras.Model(inputs, result)

  model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                optimizer=tf.keras.optimizers.Adam())
  return model

titanic_model = titanic_model(titanic_preprocessing, inputs)

titanic_model.fit(x=titanic_features_dict, y=titanic_labels, epochs=10)

titanic_model.save('test')
reloaded = tf.keras.models.load_model('test')

features_dict = {name:values[:1] for name, values in titanic_features_dict.items()}

before = titanic_model(features_dict)
after = reloaded(features_dict)
assert (before-after)<1e-3
print(before)
print(after)

"""# Using tf.data function

```
This code shows how to control or use a data that does not fit into memory using the tf.data by TensorFlow
```
"""

import itertools #imports itertools

def slices(features): #defing slices function with features paramater
  for i in itertools.count(): 
    # For each feature take index `i`
    example = {name:values[i] for name, values in features.items()}
    yield example

for example in slices(titanic_features_dict): #runs through every example in sliced titanic_features
  for name, value in example.items(): 
    print(f"{name:19s}: {value}")
  break

features_ds = tf.data.Dataset.from_tensor_slices(titanic_features_dict) #returns a a tf.data.Dataset that implements a generalized version of the titanic features dictionary

for example in features_ds: #runs through every example in features_ds
  for name, value in example.items():
    print(f"{name:19s}: {value}")
  break

#uses from_tensor_slices function for the code to handle nested dictionaries
titanic_ds = tf.data.Dataset.from_tensor_slices((titanic_features_dict, titanic_labels)) #creates a dataset of (features_dict, labels) in pair

titanic_batches = titanic_ds.shuffle(len(titanic_labels)).batch(32) #batch/shuffle the titanic_ds

titanic_model.fit(titanic_batches, epochs=5) #pass the entire dataset to Model.fit and display epochs

"""# From a Single File"""

#downloads data from file path
titanic_file_path = tf.keras.utils.get_file("train.csv", "https://storage.googleapis.com/tf-datasets/titanic/train.csv")

titanic_csv_ds = tf.data.experimental.make_csv_dataset( #creates a tf.data.Dataset from experimental.make_csv_dataset
    titanic_file_path,
    batch_size=5, # Artificially small to make examples easier to show.
    label_name='survived',
    num_epochs=1, #set number of epochs to 1 to avoid endless looping
    ignore_errors=True,)

for batch, label in titanic_csv_ds.take(1):
  for key, value in batch.items():
    print(f"{key:20s}: {value}")
  print()
  print(f"{'label':20s}: {label}")

""">**Using the Traffic Volume Data to Test a Decompressed Data**"""

#downloading the traffic volume data
traffic_volume_csv_gz = tf.keras.utils.get_file(
    'Metro_Interstate_Traffic_Volume.csv.gz', 
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00492/Metro_Interstate_Traffic_Volume.csv.gz",
    cache_dir='.', cache_subdir='traffic')

traffic_volume_csv_gz_ds = tf.data.experimental.make_csv_dataset(
    traffic_volume_csv_gz,
    batch_size=256,
    label_name='traffic_volume',
    num_epochs=1,
    compression_type="GZIP")

for batch, label in traffic_volume_csv_gz_ds.take(1):
  for key, value in batch.items():
    print(f"{key:20s}: {value[:5]}")
  print()
  print(f"{'label':20s}: {label[:5]}")

"""# Caching

```
Using Dataset.cache or tf.data.Dataset.snapshot to parsed CSV data only on the first epoch
```
"""

# Commented out IPython magic to ensure Python compatibility.
# #use %%time for displaying the CPU and Wall time of the entire cell
# %%time 
# for i, (batch, label) in enumerate(traffic_volume_csv_gz_ds.repeat(20)):
#   if i % 40 == 0:
#     print('.', end='')
# print()

# Commented out IPython magic to ensure Python compatibility.
# #displaying the CPU and Wall time with the use of Dataset.cache
# #Cache disables any shuffles from any earlier pipeline, also results to faster run time
# %%time
# caching = traffic_volume_csv_gz_ds.cache().shuffle(1000)
# 
# for i, (batch, label) in enumerate(caching.shuffle(1000).repeat(20)):
#   if i % 40 == 0:
#     print('.', end='')
# print()

# Commented out IPython magic to ensure Python compatibility.
# #use snapshot for temporary storage of dataset while in use, not a format of long term storage
# %%time
# snapshotting = traffic_volume_csv_gz_ds.snapshot('titanic.tfsnap').shuffle(1000)
# 
# for i, (batch, label) in enumerate(snapshotting.shuffle(1000).repeat(20)):
#   if i % 40 == 0:
#     print('.', end='')
# print()

"""# Multiple Files"""

fonts_zip = tf.keras.utils.get_file( #downloading the dataset
    'fonts.zip',  "https://archive.ics.uci.edu/ml/machine-learning-databases/00417/fonts.zip",
    cache_dir='.', cache_subdir='fonts',
    extract=True)

import pathlib #importing pathlib 
font_csvs =  sorted(str(p) for p in pathlib.Path('fonts').glob("*.csv")) #sorts out fonts

font_csvs[:10] #displays the fonts with a limit of 10

len(font_csvs) #displays the count of all the fonts in font_csvs

fonts_ds = tf.data.experimental.make_csv_dataset(
    file_pattern = "fonts/*.csv",
    batch_size=10, num_epochs=1,
    num_parallel_reads=20,
    shuffle_buffer_size=10000)

for features in fonts_ds.take(1):
  for i, (name, value) in enumerate(features.items()):
    if i>15:
      break
    print(f"{name:20s}: {value}")
print('...')
print(f"[total: {len(features)} features]")

#Packing Feilds for packing the pixels into an image-tensor
import re

def make_images(features):
  image = [None]*400
  new_feats = {}

  for name, value in features.items():
    match = re.match('r(\d+)c(\d+)', name)
    if match:
      image[int(match.group(1))*20+int(match.group(2))] = value
    else:
      new_feats[name] = value

  image = tf.stack(image, axis=0)
  image = tf.reshape(image, [20, 20, -1])
  new_feats['image'] = image

  return new_feats

#apply the function to each batch in the dataset
fonts_image_ds = fonts_ds.map(make_images)

for features in fonts_image_ds.take(1):
  break

#plots the resulting images
from matplotlib import pyplot as plt

plt.figure(figsize=(6,6), dpi=120)

for n in range(9):
  plt.subplot(3,3,n+1)
  plt.imshow(features['image'][..., n])
  plt.title(chr(features['m_label'][n]))
  plt.axis('off')

"""# Lower Level Functions

```
This code intruduces 2 APIs to help deal with use-cases that does not fit the basic patterns

*   tf.io.decode_csv
*   tf.data.experimental.CsvDataset
```

> **tf.io.decode_csv**
"""

text = pathlib.Path(titanic_file_path).read_text()
lines = text.split('\n')[1:-1]

all_strings = [str()]*10
all_strings

features = tf.io.decode_csv(lines, record_defaults=all_strings) 

for f in features:
  print(f"type: {f.dtype.name}, shape: {f.shape}")

print(lines[0])

titanic_types = [int(), str(), float(), int(), int(), float(), str(), str(), str(), str()]
titanic_types

features = tf.io.decode_csv(lines, record_defaults=titanic_types) 

for f in features:
  print(f"type: {f.dtype.name}, shape: {f.shape}")

"""> **tf.data.experimental.CsvDataset**"""

simple_titanic = tf.data.experimental.CsvDataset(titanic_file_path, record_defaults=titanic_types, header=True)

for example in simple_titanic.take(1):
  print([e.numpy() for e in example])

def decode_titanic_line(line):
  return tf.io.decode_csv(line, titanic_types)

manual_titanic = (
    # Load the lines of text
    tf.data.TextLineDataset(titanic_file_path)
    # Skip the header row.
    .skip(1)
    # Decode the line.
    .map(decode_titanic_line)
)

for example in manual_titanic.take(1):
  print([e.numpy() for e in example])

"""> **Multiple Files**"""

font_line = pathlib.Path(font_csvs[0]).read_text().splitlines()[1] #Inspecting the first row
print(font_line) #displaying font_line

num_font_features = font_line.count(',')+1 #counts the commas 
font_column_types = [str(), str()] + [float()]*(num_font_features-2) #gets the total number of features

font_csvs[0] #displays the first file in the CSVs

#test run for passing list of files to CsvDataset
simple_font_ds = tf.data.experimental.CsvDataset(
    font_csvs, 
    record_defaults=font_column_types, 
    header=True)

for row in simple_font_ds.take(10): #takes 10 displays
  print(row[0].numpy()) #set row to 0 for 'AGENCY' to be read first

#to interleave multiple files
font_files = tf.data.Dataset.list_files("fonts/*.csv")

#shuffles the file name for each epoch
print('Epoch 1:')
for f in list(font_files)[:5]:
  print("    ", f.numpy())
print('    ...')
print()

print('Epoch 2:')
for f in list(font_files)[:5]:
  print("    ", f.numpy())
print('    ...')

# creates a tf.data.experimental.CsvDataset from each element of the dataset of files
def make_font_csv_ds(path):
  return tf.data.experimental.CsvDataset(
    path, 
    record_defaults=font_column_types, 
    header=True)
  
font_rows = font_files.interleave(make_font_csv_ds, #returns elements by cycling over a number of the child-Datasets
                                  cycle_length=3)

fonts_dict = {'font_name':[], 'character':[]}

for row in font_rows.take(10):
  fonts_dict['font_name'].append(row[0].numpy().decode())
  fonts_dict['character'].append(chr(row[2].numpy()))

pd.DataFrame(fonts_dict)

"""> **Performance**"""

#testing the run time of 2048-batches example
BATCH_SIZE=2048
fonts_ds = tf.data.experimental.make_csv_dataset(
    file_pattern = "fonts/*.csv",
    batch_size=BATCH_SIZE, num_epochs=1,
    num_parallel_reads=100)

# Commented out IPython magic to ensure Python compatibility.
# %%time
# for i,batch in enumerate(fonts_ds.take(20)):
#   print('.',end='')
# 
# print() #display the resulting CPU and Wall time

#passing batches of text lines using decode_csv
fonts_files = tf.data.Dataset.list_files("fonts/*.csv")
fonts_lines = fonts_files.interleave(
    lambda fname:tf.data.TextLineDataset(fname).skip(1), 
    cycle_length=100).batch(BATCH_SIZE)

fonts_fast = fonts_lines.map(lambda x: tf.io.decode_csv(x, record_defaults=font_column_types))

# Commented out IPython magic to ensure Python compatibility.
# %%time
# for i,batch in enumerate(fonts_fast.take(20)):
#   print('.',end='')
# 
# print()