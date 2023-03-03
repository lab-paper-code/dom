from keras.applications.inception_v3 import InceptionV3
from keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.utils import load_img
from keras.applications import imagenet_utils
from tensorflow.python.keras.models import load_model
from tensorflow.keras.utils import img_to_array

import numpy as np
import os
import sys
import time
from tqdm import tqdm
import config
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.applications import InceptionV3
# load model
#model = InceptionV3(weight="imagenet")
model = MobileNet(weights="imagenet")
IMAGE_PATH = config.IP['img_path']
FILE_LIMIT = sys.argv[1]


def getFilesByCnt(img_cnt):
    files = os.listdir(IMAGE_PATH)
    os.chdir(IMAGE_PATH)

    fileList = []

    for i in range(0, img_cnt):
        file_name = files[i]
        fileList.append(file_name)

    print("SEND FILE LIST LENGTH : {}".format(len(fileList)))

    return fileList


def getFiles(limit_size):
    files = os.listdir(IMAGE_PATH)
    os.chdir(IMAGE_PATH)
    cnt = 0
    fileList = []
    file_sizes = 0

    while True:
        file_name = files[cnt]
        next_file = files[cnt + 1]
        filesize = os.path.getsize(file_name) / (1024.0 * 1024.0 * 1024.0)
        next_file_size = os.path.getsize(next_file) / (1024.0 * 1024.0 * 1024.0)
        file_sizes += filesize

        fileList.append(file_name)

        if file_sizes + next_file_size > limit_size:
            print("total file size : ", file_sizes)
            break;
        cnt += 1
    print("SEND FILE LIST LENGTH : {}".format(len(fileList)))

    return fileList


def predict_fu(path, file):
    inputShape = (224, 224)
    img = load_img(path, target_size=inputShape)
    image = img_to_array(img)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)

    predicts = model.predict(image)
    P = imagenet_utils.decode_predictions(predicts)

    for (i, (imagenetID, label, prob)) in enumerate(P[0]):
        file.write("{}: {:.2f}% \n".format(label, prob * 100))
        # print("{}: {:.2f}%".format(label, prob * 100))
        return imagenetID, label


if os.path.isfile("result.txt"):
    os.unlink("result.txt")

f = open("result.txt", "w")

fileList = getFilesByCnt(int(FILE_LIMIT))

start = time.time()
for file in tqdm(fileList):
    if file.endswith('.JPEG') or file.endswith('.JPG') or file.endswith('.PNG'):
        predict_fu(file, f)
f.close()

print("Elapsed Time : %s" % (time.time() - start))
