


import os
import config

import subprocess
import shlex

import sys
import time

from collections import OrderedDict
# ffmpeg -i VIRAT_S_050201_03_000573_000647.mp4 -c:v libx264 -preset fast -crf 20 -c:a copy -profile:v high -level 4.2 output_video2.mp4


path = config.IP['video_path']
#output_path = config.IP['video_output_path']
FILE_LIMIT = float(sys.argv[1])
start = time.time()

def is_not_blank(s):
    return bool(s and not s.isspace())


def isIntegrityVideos(file_name):
    # command
    command = "ffmpeg -v error -sseof -1 -i " + path+file_name + " -f null -"
    print(command)

    command = shlex.split(command)
    out = subprocess.run(command, capture_output=True, encoding="utf-8")
    print(out.stderr)

    if is_not_blank(out.stderr):
        return False
    return True


def getFiles(limit_size):
    files = os.listdir(path)

    cnt = 0
    fileList = dict()
    file_sizes = 0
    limit_size = limit_size * 1024.0 * 1024.0 * 1024.0
    while True:
        file_name = files[cnt]
        next_file = files[cnt + 1]
        filesize = os.path.getsize(path + file_name)
        next_file_size = os.path.getsize(path + next_file)
        # filesize = os.path.getsize(path + file_name) / (1024.0 * 1024.0 * 1024.0)
        # next_file_size = os.path.getsize(path + next_file) / (1024.0 * 1024.0 * 1024.0)

        if isIntegrityVideos(file_name):

            file_sizes += filesize

            f = open(path + file_name, 'rb')
            fileList[file_name] = {file_name: f}
            f.close()

            # 용량 체크
            if file_sizes + next_file_size > limit_size:
                file_sizes = file_sizes + next_file_size

                f = open(path + next_file, 'rb')
                fileList[next_file] = {file_name: f}
                f.close()

                print("total file size : ", file_sizes, "byte, ", file_sizes / (1024.0 * 1024.0 * 1024.0), "GB")
                break;
        cnt += 1
    print("SEND FILE LIST LENGTH : {}".format(len(fileList)))

    return fileList, file_sizes


fileList, fileSize = getFiles(FILE_LIMIT)


for file in fileList:
    split = file.split(".")
    output_file_name = split[0] + "_compressed."+split[1]
    #command = "ffmpeg -i " +path+file+" -c:v libx264 -preset fast -crf 20 -c:a copy -profile:v high -level 4.2 "+output_path+output_file_name + " -y"
    command = "ffmpeg -i " + path + file + " " + path + output_file_name + " -y"
    command = shlex.split(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, err = process.communicate()


print("This devices Elapsed Time : %s" % (time.time() - start))

