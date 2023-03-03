import os
import config
import time
import random
import json
import logging
from datetime import datetime

path = config.IP['video_path']
img_path = config.IP['img_path']
CHUNK_SIZE = 60 * 1024 * 1024
isEnd = False


def read_in_chunks(file_object, CHUNK_SIZE):
    global isEnd
    while True:
        data = file_object.read(CHUNK_SIZE)
        if not data:
            isEnd = True
            break
        yield data


def get_dir_size(path):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total



def getFiles(limit_size):
    files = os.listdir(path)

    cnt = 0
    fileList = dict()
    file_sizes = 0

    while True:
        file_name = files[cnt]
        next_file = files[cnt + 1]
        filesize = os.path.getsize(path + file_name) / (1024.0 * 1024.0 * 1024.0)
        next_file_size = os.path.getsize(path + next_file) / (1024.0 * 1024.0 * 1024.0)
        file_sizes += filesize

        f = open(path + file_name, 'rb')
        fileList[file_name] = {file_name: f}
        f.close()

        if file_sizes + next_file_size > limit_size:
            print("total file size : ", file_sizes)
            break;
        cnt += 1
    print("SEND FILE LIST LENGTH : {}".format(len(fileList)))

    return fileList



def getFilesByCnt(img_cnt):
    files = os.listdir(img_path)

    fileList = dict()
    file_sizes = 0

    for i in range(0, img_cnt):
        file_name = files[i]
        filesize = os.path.getsize(img_path + file_name) / (1024.0 * 1024.0 * 1024.0)
        file_sizes += filesize

        f = open(img_path + file_name, 'rb')
        fileList[file_name] = {file_name: f}
        f.close()

    print("SEND FILE LIST LENGTH : {}".format(len(fileList)))

    return fileList


def getFileName(file):
    files = file.split(".")
    return files[0], files[1]

# def checkFileSize():
#     for root, dirs, files in os.walk(path):
#         # result = "%s : %.f MB in %d files." % (os.path.abspath(root), sum([getsize(join(root, name)) for name in files]) / (1024.0 * 1024.0), len(files))
#         file_size = sum([getsize(join(root, name)) for name in files]) / (1024.0 * 1024.0)
#         return file_size


def make_text(txt_id):
    cur_timestamp = time.time()
    cur_time = time.localtime(cur_timestamp)
    cur_time = time.strftime('%Y-%m-%d %I:%M:%s %p', cur_time)

    now_str = json.dumps({'isFile': 'F','isText': 'T','id': txt_id,'timestamp': cur_timestamp,'time': cur_time,'value': random.randint(0, 100000)})

    return now_str


def log(message):
    log_date, raw_data = get_log_date()
    log_message = "[{0}] {1}".format(log_date, message)
    print(log_message)
    logging.info(log_message)
    return raw_data


def get_log_date():
    raw_data = datetime.now()
    log_date = raw_data.strftime('%Y-%m-%d %H:%M:%S.%f')
    return log_date, raw_data