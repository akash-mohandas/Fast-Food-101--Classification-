# -*- coding: utf-8 -*-
"""FastAI_food.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1k1k7KwPOH52cbaeucnly_Z52APboBoIK

Import fastai libraries which has the food-101 dataset and built in models
"""

from fastai.vision import *
from fastai.metrics import error_rate

"""Any edits to the libraries will be reloaded automatically using following lines. Since fastai is developing rapidly, this is helpful."""

# %reload_ext autoreload
# %autoreload 2
# %matplotlib inline

"""Batch size to be used"""

bs=64

"""Download and extract food-101 data by passing the URL"""

path = untar_data(URLs.FOOD)

path.ls()

"""Import the json file containing the information about training data to be used in the images folder"""

path_train_img = path/'train.json'
import json
with open(path_train_img) as j_file:
  train_data=json.load(j_file)
  print(train_data)
j_file.close()
#fnames = get_image_files(path_img)

"""Checking if the training data is balanced"""

for labels in train_data:
  print(labels,len(train_data[labels]))

"""Get train data path"""

path_img = path/'images/'
train_images=[]
labels=[]
for food in train_data:
  for img in train_data[food]:
    train_images.append(path_img/(img+'.jpg'))
    labels.append(img[:img.rfind('/')])

"""Get test data path"""

path_test_img = path/'test.json'
with open(path_test_img) as j_file1:
  test_data=json.load(j_file1)
  print(test_data)
j_file1.close()
path_img = path/'images/'
test_images=[]
test_labels=[]
for food in test_data:
  for img in test_data[food]:
    test_images.append(path_img/(img+'.jpg'))
    test_labels.append(img[:img.rfind('/')])

"""Create a dataframe for train and test paths"""

import pandas as pd
train_df = pd.DataFrame()
train_df["column1"]=train_images
train_df["label"]=labels


test_df = pd.DataFrame()
test_df["column1"]=test_images
test_df["label"]=test_labels

"""Create an image data bunch for train and test"""

data = (ImageList.from_df(train_df,Path('/')).split_by_rand_pct(0.2)
       .label_from_df().transform(get_transforms(),size=224)
        .databunch(bs=bs//2).normalize(imagenet_stats))
test = ImageList.from_df(test_df, Path('/'))
data.add_test(test)

data.sanity_check

train_data = ImageDataBunch.from_lists(path_img,train_images,ds_tfms=get_transforms(),labels=labels,size=224,bs=bs//2).normalize(imagenet_stats)

"""Lets look how the training data looks like"""

train_data.show_batch(rows=3, figsize=(7,6))

print(train_data.classes)

"""Lets use the architecture of RESNET50 which is famous for Image classification"""

learner = cnn_learner(data,models.resnet50,metrics=accuracy)

learner.model

"""Find the loss vs learning rate for first epoch and choose the best learning rate"""

learner.lr_find()

learner.recorder.plot()

"""train the model for 17 epochs as it overfits there after"""

learner.fit_one_cycle(17,max_lr=slice(1e-2,1e-1))

learner.save('/content/gdrive/My Drive/Resnet50-epoch17-err0.2326')

"""Load the model saved on google drive as the kernel keeps dying. This model is trained with RESNET50 for 17 epochs and has training error rate of 0.2326"""

learner = cnn_learner(data,models.resnet50).load('/content/gdrive/My Drive/Resnet50-epoch17-err0.2326')

"""Geth the predictions for test data"""

preds = learner.get_preds(data.test_ds)

"""The model gives 68.99% accuracy on test data"""

acc=0
labels=sorted(list(set(test_labels)))
len(labels)
for i in range(len(test_labels)):
  if labels[preds[1][i]]==test_labels[i]:
    acc+=1
print(acc/len(test_labels))

learner = cnn_learner(train_data,models.resnet50).load('/content/gdrive/My Drive/Resnet50-epoch17-err0.2326')

"""Interpretation of learner"""

interp = ClassificationInterpretation.from_learner(learner)

"""What are the top misclassified foods among the training data"""

interp.plot_top_losses(15,figsize=(15,11))