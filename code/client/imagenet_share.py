from keras.applications.inception_v3 import InceptionV3
from keras.applications.inception_v3 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from keras.applications import imagenet_utils
from tensorflow.python.keras.models import load_model

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
FILE_LIMIT = sys.argv[1]

INDEX = int(sys.argv[1])
AMOUNT = int(sys.argv[2])
webdav_path = config.IP['webdav']




def getFilesByIndex(start_index, amount):
    files = os.listdir(webdav_path + 'images/')
    files = files[start_index:start_index + amount]
    return files


def predict_fu(path, file):
    inputShape = (224, 224)

    full_path = webdav_path + "images/" + path
    img = load_img(full_path, target_size=inputShape)
    image = img_to_array(img)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)

    predicts = model.predict(image)
    P = imagenet_utils.decode_predictions(predicts)

    for (i, (imagenetID, label, prob)) in enumerate(P[0]):
        file.write("{}: {:.2f}% \n".format(label, prob * 100))
        # print("{}: {:.2f}%".format(label, prob * 100))
        return imagenetID, label

os.chdir(webdav_path)
if os.path.isfile("result.txt"):
    os.unlink("result.txt")

f = open("result.txt", "w")

fileList = getFilesByIndex(INDEX, AMOUNT)

start = time.time()
for file in tqdm(fileList):
    if file.endswith('.JPEG') or file.endswith('.JPG') or file.endswith('.PNG'):
        predict_fu(file, f)
f.close()

print("Elapsed Time : %s" % (time.time() - start))
