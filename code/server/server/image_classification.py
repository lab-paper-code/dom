from keras.applications.inception_v3 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from keras.applications import imagenet_utils
from tensorflow.python.keras.models import load_model
import tensorflow as tf
import numpy as np
import os
import sys
import time
import config
from tensorflow.keras.applications import NASNetMobile
import keras
import keras.backend as K

configg = tf.compat.v1.ConfigProto()
configg.gpu_options.allow_growth = True
configg.gpu_options.per_process_gpu_memory_fraction = 0.05
session = tf.compat.v1.Session(config=configg)


# load model
model = NASNetMobile(weights="imagenet")
IMAGE_PATH = config.IP['image_path']
FILE_LIMIT = sys.argv[1]


def getFiles(limit_size):
    files = os.listdir(IMAGE_PATH)
    os.chdir(IMAGE_PATH)
    cnt = 0
    fileList = []
    file_sizes = 0

    while cnt < limit_size:
        file_name = files[cnt]

        fileList.append(file_name)

        cnt += 1
    print("SEND FILE LIST LENGTH : {}".format(len(fileList)))

    return fileList


def predict_fu(path, model):
    inputShape = (224, 224)
    img = load_img(path, target_size=inputShape)
    image = img_to_array(img)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)

    predicts = model.predict(image)
    P = imagenet_utils.decode_predictions(predicts)

    for (i, (imagenetID, label, prob)) in enumerate(P[0]):
        print("{}: {:.2f}%".format(label, prob * 100))
        K.clear_session()
        return imagenetID, label


start = time.time()
fileList = getFiles(int(FILE_LIMIT))

for file in fileList:
    if file.endswith('.JPEG') or file.endswith('.JPG') or file.endswith('.PNG'):
        predict_fu(file, model)
print('elapsed time: ', time.time() - start)
