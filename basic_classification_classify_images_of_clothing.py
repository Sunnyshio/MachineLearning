# -*- coding: utf-8 -*-
"""Basic classification: Classify images of clothing

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1F_rUB9NELH34j0SBq5X6chqkdLCa1ZdW

# Importing Fashion MNIST Dataset and libraries
"""

# TensorFlow and tf.keras
import tensorflow as tf

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt

print(tf.__version__)

fashion_mnist = tf.keras.datasets.fashion_mnist #assigning the dataset into the variable "fashion_mnist"

(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data() #loading the data from source

#storing class names in an array to use for plotting later
class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

"""# Data Exploration"""

train_images.shape #displaying the shape/number of data in the dataset

len(train_labels) #displaying the length of training labels

train_labels #display the train_labels array

test_images.shape #displaying the shape/number of data in the test_image dataset

len(test_labels) #length of test labels

"""# Data Preprocessing"""

plt.figure() #creates a figure
plt.imshow(train_images[0]) #creates an image for the train_image array
plt.colorbar() #adds a colorbar to imshow figure
plt.grid(False) #hides the gridlines on the plot
plt.show() #displays the created plot

train_images = train_images / 255.0 #scales train_images from 0 to 1
test_images = test_images / 255.0 #scales test_images from 0 to 1

plt.figure(figsize=(10,10)) #sets the figure size to a 10X10 dimension
for i in range(25): #picks the first 25 images from the dataset
    plt.subplot(5,5,i+1) #sets the grid in a 5X5 position
    plt.xticks([]) #showing ticks for the x-axis
    plt.yticks([]) #showing ticks for the y-axis
    plt.grid(False) #hides gridlines
    plt.imshow(train_images[i], cmap=plt.cm.binary) #sets the figure color to binary-colormap
    plt.xlabel(class_names[train_labels[i]])
plt.show() #display the figure

"""# Building the Model"""

#setting up the layers
model = tf.keras.Sequential([ #sequential groups the stack of layers 
    tf.keras.layers.Flatten(input_shape=(28, 28)), #flattens the output
    tf.keras.layers.Dense(128, activation='relu'), #creates a dense layer
    tf.keras.layers.Dense(10) #dense layer model output shape of 10
])

#compiling the model
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

#training the model
model.fit(train_images, train_labels, epochs=10) #model is trained repetitively in 10 epochs

"""# Evaluate Accuracy"""

#accuracy evaluation
test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2) #use keras evaluate to test

print('\nTest accuracy:', test_acc)

#predictions
probability_model = tf.keras.Sequential([model, 
                                         tf.keras.layers.Softmax()])
predictions = probability_model.predict(test_images)

predictions[0]

np.argmax(predictions[0])

test_labels[0]

def plot_image(i, predictions_array, true_label, img):
  true_label, img = true_label[i], img[i]
  plt.grid(False)
  plt.xticks([])
  plt.yticks([])

  plt.imshow(img, cmap=plt.cm.binary)

  predicted_label = np.argmax(predictions_array)
  if predicted_label == true_label:
    color = 'blue'
  else:
    color = 'red'

  plt.xlabel("{} {:2.0f}% ({})".format(class_names[predicted_label],
                                100*np.max(predictions_array),
                                class_names[true_label]),
                                color=color)

def plot_value_array(i, predictions_array, true_label):
  true_label = true_label[i]
  plt.grid(False)
  plt.xticks(range(10))
  plt.yticks([])
  thisplot = plt.bar(range(10), predictions_array, color="#777777")
  plt.ylim([0, 1])
  predicted_label = np.argmax(predictions_array)

  thisplot[predicted_label].set_color('red')
  thisplot[true_label].set_color('blue')

#verify predictions
i = 0
plt.figure(figsize=(6,3))
plt.subplot(1,2,1)
plot_image(i, predictions[i], test_labels, test_images)
plt.subplot(1,2,2)
plot_value_array(i, predictions[i],  test_labels)
plt.show()

i = 12
plt.figure(figsize=(6,3))
plt.subplot(1,2,1)
plot_image(i, predictions[i], test_labels, test_images)
plt.subplot(1,2,2)
plot_value_array(i, predictions[i],  test_labels)
plt.show()

# Plot the first X test images, their predicted labels, and the true labels.
# Color correct predictions in blue and incorrect predictions in red.
num_rows = 5
num_cols = 3
num_images = num_rows*num_cols
plt.figure(figsize=(2*2*num_cols, 2*num_rows))
for i in range(num_images):
  plt.subplot(num_rows, 2*num_cols, 2*i+1)
  plot_image(i, predictions[i], test_labels, test_images)
  plt.subplot(num_rows, 2*num_cols, 2*i+2)
  plot_value_array(i, predictions[i], test_labels)
plt.tight_layout()
plt.show()

"""# Use the Trained Model"""

# Grab an image from the test dataset.
img = test_images[1]

print(img.shape)

# Add the image to a batch where it's the only member.
img = (np.expand_dims(img,0))

print(img.shape)

predictions_single = probability_model.predict(img)

print(predictions_single)

plot_value_array(1, predictions_single[0], test_labels)
_ = plt.xticks(range(10), class_names, rotation=45)
plt.show()

np.argmax(predictions_single[0])