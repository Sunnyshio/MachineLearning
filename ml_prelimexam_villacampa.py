# -*- coding: utf-8 -*-
"""ML_PrelimExam_Villacampa.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jY_RK9q2vYTUqWN4Rr8V6PNyHTYYiBG9

# Install Library

>This first section of the code prepares the chosen IDE for import of necessary libraries that will help execute the entire code
"""

!pip install "tensorflow-text==2.8.*"

import collections
import pathlib

import tensorflow as tf

from tensorflow.keras import layers
from tensorflow.keras import losses
from tensorflow.keras import utils
from tensorflow.keras.layers import TextVectorization

import tensorflow_datasets as tfds

from google.colab import drive
drive.mount('/content/gdrive')

"""# Data Exploration

> This Section unzips the dataset located in the drive and explores the dataset
"""

!unzip gdrive/My\ Drive/archive.zip #unzip archive file from mounted gdrive

dataset_dir = pathlib.Path('/content/Data').parent #set path to drive content --> Data

list(dataset_dir.iterdir()) #listing of all files in directory

train_dir = dataset_dir/'Data' #set "Data" folder to train directory
list(train_dir.iterdir()) #list all directory

#create a sample file
sample_file = train_dir/'Science/62710.txt' 

with open(sample_file) as f:
  print(f.read())

"""# Loading the Dataset

>This loads the data off disk and prepares the dataset into a format that is suitable for training
"""

#creates a validation set using an 80:20 split of the training data
batch_size = 32
seed = 42

raw_train_ds = utils.text_dataset_from_directory(
    train_dir,
    batch_size=batch_size,
    validation_split=0.2,
    subset='training',
    seed=seed)

#iterates over the dataset and print out a few examples, to get a feel for the data.
for text_batch, label_batch in raw_train_ds.take(1):
  for i in range(10):
    print("Question: ", text_batch.numpy()[i])
    print("Label:", label_batch.numpy()[i])

#inspect the class_names property on the dataset
for i, label in enumerate(raw_train_ds.class_names):
  print("Label", i, "corresponds to", label)

# creates a validation set
raw_val_ds = utils.text_dataset_from_directory(
    train_dir,
    batch_size=batch_size,
    validation_split=0.2,
    subset='validation',
    seed=seed)

test_dir = dataset_dir/'Data' #setting "Data" folder to test directory

#creates a test set
raw_test_ds = utils.text_dataset_from_directory(
    test_dir,
    batch_size=batch_size)

"""# Dataset Preparation

>This section of the code will standardize, tokenize, and vectorize the data
"""

#setting the vocab size and tokenize
VOCAB_SIZE = 10000

binary_vectorize_layer = TextVectorization(
    max_tokens=VOCAB_SIZE,
    output_mode='binary')

#setting the explicit maximum sequence length
MAX_SEQUENCE_LENGTH = 250

int_vectorize_layer = TextVectorization(
    max_tokens=VOCAB_SIZE,
    output_mode='int',
    output_sequence_length=MAX_SEQUENCE_LENGTH)

# Make a text-only dataset (without labels), then call `TextVectorization.adapt`.
train_text = raw_train_ds.map(lambda text, labels: text)
binary_vectorize_layer.adapt(train_text)
int_vectorize_layer.adapt(train_text)

#prints the result of using the layers
def binary_vectorize_text(text, label):
  text = tf.expand_dims(text, -1)
  return binary_vectorize_layer(text), label

#prints the result again of using the layer
def int_vectorize_text(text, label):
  text = tf.expand_dims(text, -1)
  return int_vectorize_layer(text), label

# Retrieve a batch (of 32 reviews and labels) from the dataset.
text_batch, label_batch = next(iter(raw_train_ds))
first_question, first_label = text_batch[0], label_batch[0]
print("Question", first_question)
print("Label", first_label)

#prints the vecotorized question 
print("'binary' vectorized question:",
      binary_vectorize_text(first_question, first_label)[0])

#prints the vectorized questions in int type
print("'int' vectorized question:",
      int_vectorize_text(first_question, first_label)[0])

#sample print of the corresponding strings to integers
print("1289 ---> ", int_vectorize_layer.get_vocabulary()[1289])
print("313 ---> ", int_vectorize_layer.get_vocabulary()[313])
print("Vocabulary size: {}".format(len(int_vectorize_layer.get_vocabulary())))

#applies TextVectorization to create layers training, validation, and test sets
binary_train_ds = raw_train_ds.map(binary_vectorize_text)
binary_val_ds = raw_val_ds.map(binary_vectorize_text)
binary_test_ds = raw_test_ds.map(binary_vectorize_text)

int_train_ds = raw_train_ds.map(int_vectorize_text)
int_val_ds = raw_val_ds.map(int_vectorize_text)
int_test_ds = raw_test_ds.map(int_vectorize_text)

"""# Dataset Configuration

>This section performs two steps to make sure the I/O does not become blocking. It performs data caching and prefetch. Caching is necessary for keeping the memory.
"""

#this keeps data in memory after it's loaded off disk
AUTOTUNE = tf.data.AUTOTUNE

def configure_dataset(dataset):
  return dataset.cache().prefetch(buffer_size=AUTOTUNE)

#data prefetch for model execution
binary_train_ds = configure_dataset(binary_train_ds)
binary_val_ds = configure_dataset(binary_val_ds)
binary_test_ds = configure_dataset(binary_test_ds)

int_train_ds = configure_dataset(int_train_ds)
int_val_ds = configure_dataset(int_val_ds)
int_test_ds = configure_dataset(int_test_ds)

"""# Model Training

>This part basically creates the neural network and trains the entire model with the dataset
"""

binary_model = tf.keras.Sequential([layers.Dense(4)]) #defining binary model using sequential by Keras

binary_model.compile( #compiling the model layers
    loss=losses.SparseCategoricalCrossentropy(from_logits=True),
    optimizer='adam',
    metrics=['accuracy'])

history = binary_model.fit( #fitting the model
    binary_train_ds, validation_data=binary_val_ds, epochs=10)

#vectorized layer to build a 1D ConvNet using int
def create_model(vocab_size, num_labels):
  model = tf.keras.Sequential([
      layers.Embedding(vocab_size, 64, mask_zero=True),
      layers.Conv1D(64, 5, padding="valid", activation="relu", strides=2),
      layers.GlobalMaxPooling1D(),
      layers.Dense(num_labels)
  ])
  return model

# `vocab_size` is `VOCAB_SIZE + 1` since `0` is used additionally for padding.
int_model = create_model(vocab_size=VOCAB_SIZE + 1, num_labels=4)
int_model.compile(
    loss=losses.SparseCategoricalCrossentropy(from_logits=True),
    optimizer='adam',
    metrics=['accuracy'])
history = int_model.fit(int_train_ds, validation_data=int_val_ds, epochs=5)

#prints linear model summary
print("Linear model on binary vectorized data:")
print(binary_model.summary())

#prints covnet model summary 
print("ConvNet model on int vectorized data:")
print(int_model.summary())

#evaluate both models on test data
binary_loss, binary_accuracy = binary_model.evaluate(binary_test_ds)
int_loss, int_accuracy = int_model.evaluate(int_test_ds)

print("Binary model accuracy: {:2.2%}".format(binary_accuracy))
print("Int model accuracy: {:2.2%}".format(int_accuracy))

"""# Export the Model

>This section exports the trained model and creates a new model from the previous one by using the weights.
"""

export_model = tf.keras.Sequential( #defining exportation of model function using sequential
    [binary_vectorize_layer, binary_model,
     layers.Activation('sigmoid')])

export_model.compile( #compling export fucntion layers
    loss=losses.SparseCategoricalCrossentropy(from_logits=False),
    optimizer='adam',
    metrics=['accuracy'])

# Test it with `raw_test_ds`, which yields raw strings
loss, accuracy = export_model.evaluate(raw_test_ds)
print("Accuracy: {:2.2%}".format(binary_accuracy))

#creates a function to find the label with the maximum score
def get_string_labels(predicted_scores_batch):
  predicted_int_labels = tf.math.argmax(predicted_scores_batch, axis=1)
  predicted_labels = tf.gather(raw_train_ds.class_names, predicted_int_labels)
  return predicted_labels

"""# Run Inference on New Data"""

inputs = [
    "Will Bruce argue that their existence can be inferred from theory alone?",  # 'Science'
    "I believe that this orbiting space junk will be FAR brighter still",  # 'Science'
]
predicted_scores = export_model.predict(inputs)
predicted_labels = get_string_labels(predicted_scores)
for input, label in zip(inputs, predicted_labels):
  print("Question: ", input)
  print("Predicted label: ", label.numpy())