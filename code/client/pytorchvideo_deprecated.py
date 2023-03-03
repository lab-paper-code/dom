import torch
import json
from torchvision.transforms import Compose, Lambda
from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)
from pytorchvideo.data.encoded_video import EncodedVideo
from pytorchvideo.transforms import (
    ApplyTransformToKey,
    ShortSideScale,
    UniformTemporalSubsample,
    UniformCropVideo
)
from typing import Dict
import os
import config
from tqdm import tqdm
import time
import sys


VIDEO_PATH = config.IP['video_path']
FILE_LIMIT = sys.argv[1]

def getFiles(limit_size):
    try:
        files = os.listdir(VIDEO_PATH)
        os.chdir(VIDEO_PATH)
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
    except Exception as e:
        print(str(e))


# load model
# Device on which to run the model
# Set to cuda to load on GPU
device = "cpu"

# Pick a pretrained model and load the pretrained weights
model_name = "slowfast_r50"
model = torch.hub.load("facebookresearch/pytorchvideo", model=model_name, pretrained=True)

# Set to eval mode and move to desired device
model = model.to(device)
model = model.eval()


# setup Labels
with open("kinetics_classnames.json", "r") as f:
    kinetics_classnames = json.load(f)

# Create an id to label name mapping
kinetics_id_to_classname = {}
for k, v in kinetics_classnames.items():
    kinetics_id_to_classname[v] = str(k).replace('"', "")



# Input Transform
####################
# SlowFast transform
####################

side_size = 256
mean = [0.45, 0.45, 0.45]
std = [0.225, 0.225, 0.225]
crop_size = 256
num_frames = 32
sampling_rate = 2
frames_per_second = 30
alpha = 4

class PackPathway(torch.nn.Module):
    """
    Transform for converting video frames as a list of tensors.
    """
    def __init__(self):
        super().__init__()

    def forward(self, frames: torch.Tensor):
        fast_pathway = frames
        # Perform temporal sampling from the fast pathway.
        slow_pathway = torch.index_select(
            frames,
            1,
            torch.linspace(
                0, frames.shape[1] - 1, frames.shape[1] // alpha
            ).long(),
        )
        frame_list = [slow_pathway, fast_pathway]
        return frame_list

transform =  ApplyTransformToKey(
    key="video",
    transform=Compose(
        [
            UniformTemporalSubsample(num_frames),
            Lambda(lambda x: x/255.0),
            NormalizeVideo(mean, std),
            ShortSideScale(
                size=side_size
            ),
            CenterCropVideo(crop_size),
            PackPathway()
        ]
    ),
)

# The duration of the input clip is also specific to the model.
clip_duration = (num_frames * sampling_rate)/frames_per_second

def predict_video(file_path, file_name, result_file):
    try:
        # Select the duration of the clip to load by specifying the start and end duration
        # The start_sec should correspond to where the action occurs in the video
        start_sec = 0
        end_sec = start_sec + clip_duration

        # Initialize an EncodedVideo helper class
        video = EncodedVideo.from_path(file_path + file_name)

        # Load the desired clip
        video_data = video.get_clip(start_sec=start_sec, end_sec=end_sec)

        # Apply a transform to normalize the video input
        video_data = transform(video_data)

        # Move the inputs to the desired device
        inputs = video_data["video"]
        inputs = [i.to(device)[None, ...] for i in inputs]

        # Pass the input clip through the model
        preds = model(inputs)

        # Get the predicted classes
        post_act = torch.nn.Softmax(dim=1)
        preds = post_act(preds)
        pred_classes = preds.topk(k=5).indices

        # Map the predicted classes to the label names
        pred_class_names = [kinetics_id_to_classname[int(i)] for i in pred_classes[0]]
        result_file.write("{} : Predicted labels: {}".format(file_name, pred_class_names))

    except Exception as e:
        print(str(e))


if os.path.isfile("result_video.txt"):
    os.unlink("result_video.txt")

f = open("result_video.txt", "w")
# Load the example video
video_list = getFiles(int(FILE_LIMIT))


start_time = time.time()
for file in tqdm(video_list):
    video_name = file
    predict_video(VIDEO_PATH, video_name, f)
f.close()

print("Elapsed Time : %s" % (time.time() - start_time))

