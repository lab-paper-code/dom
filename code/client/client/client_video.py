from flask import request, Blueprint
import time
import threading
import socket
import requests
import zipfile

import sys
import os
import subprocess
import shlex

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import client_request as cr
import config
import utils

video_api = Blueprint('video_api', __name__)

path = config.IP['video_path']
my_ip = socket.gethostbyname(socket.getfqdn())
CHUNK_SIZE = 60 * 1024 * 1024
server_add = config.IP['server']


@video_api.route('/video/hello', methods=['GET', 'POST'])
def appImageHello():
    print("Text Hello")
    return "Hello"


'''모든 클라이언트에게 서버 전송 명령'''
@video_api.route('/upload_all_video', methods=['GET', 'POST'])
def uploadAll():
    print("upload all video")
    try:
        if request.method == 'POST':
            values = config.IP['clients']
            limit_size = float(request.form.get('limit'))
            limit_size = float(limit_size / len(values))
            print("limit size : ", limit_size)
            is_compression = request.form.get('is_zip')
            print("is zip : ", is_compression)

            start = time.time()

            url = "upload_video_zip" if is_compression == "T" else "upload_video"
            threads = [threading.Thread(target=cr.requestToAllClients, args=(ip, limit_size, url)) for ip in values]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            print("Elapsed Time : %s" % (time.time() - start))

            return 'uploaded'
    except Exception as e:
        print(str(e))
        return str(e)

'''서버로 동영상 하나씩 전송'''
@video_api.route('/upload_video', methods=['GET', 'POST'])
def uploadEach():
    print("upload video")

    try:
        print(request)

        limit_size = float(request.form.get('limit'))
        print("limit size : ", limit_size)

        index = 0
        offset = 0
        fileList = utils.getFiles(limit_size)
        for file in fileList:
            filesize = os.path.getsize(path + file)

            log_time = utils.log("{} send file {} {}byte, send START".format(my_ip, file, filesize))
            print(file)

            params = {
                'time': log_time,
                'size': int(filesize),
                'domId': my_ip
            }
            f = open(path + file, 'rb')
            for chunk in utils.read_in_chunks(f, CHUNK_SIZE):
                offset = index + len(chunk)
                index = offset

                res = requests.post('http://' + server_add + '/upload', files={file: chunk}, data=params)

                if res.ok:
                    print("Upload completed successfully! : {}".format(file))
                    print(res.text)
                else:
                    print("Something Wrong!")
            f.close()
            utils.log("{} send file {} {}MB, send END".format(my_ip, file, filesize))

        utils.log("DONE")

        return "UPLOAD"
    except Exception as e:
        utils.log(str(e))
        # upload_run(current_i)
        print(str(e))
        return str(e)

@video_api.route('/upload_all_video_zip', methods=['GET', 'POST'])
def uploadAllVideoAllZip():
    print("upload all image")
    try:
        if request.method == 'POST':
            limit = float(request.form.get('limit'))
            print("limit : ", limit)

            values = config.IP['clients']
            start = time.time()
            divide_limit = float(limit / len(values))

            threads = [threading.Thread(target=cr.requestToAllClients_video_all_zip, args=(ip, divide_limit)) for ip in
                       values]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            print("Elapsed Time : %s" % (time.time() - start))

            return 'uploaded'
    except Exception as e:
        print(str(e))
        return str(e)


@video_api.route('/upload_video_zip_all', methods=['GET', 'POST'])
def uploadVideoCompressedAll():
    print("upload compressed all")
    try:
        print(request)

        #crr.clearCompressedRate()
        #crr.clearRequest()
        limit = float(request.form.get('limit'))
        print(limit)

        # 제한 크기 file list 생성
        fileList, files_size = utils.getFiles(limit)

        owd = os.getcwd()
        os.chdir(path)
        zip_start = time.time()

        zip_file_name = 'compressed.zip'
        zip_file = zipfile.ZipFile('compressed.zip', 'w')
        #
        for file in fileList:
            zip_file.write(file)
        zip_file.close()
        utils.log("Compressed Time : %s" % (time.time() - zip_start))
        compressed_size = os.path.getsize('compressed.zip')

        #crr.addCompressedRate(files_size, compressed_size)
        os.chdir(owd)

        zip_file_path = path + 'compressed.zip'
        zip_file_size = os.path.getsize(zip_file_path)

        # start_time = log("START {}  FILE_SIZE : {}MB SEND".format(zip_file_name, zip_file_size))
        start_time = utils.log("{} send file {} {}byte, send START".format(my_ip, zip_file_name, zip_file_size))
        index = 0
        offset = 0

        params = {
            'time': start_time,
            'size': int(zip_file_size),
            'domId': my_ip
        }

        f = open(zip_file_path, 'rb')

        for chunk in utils.read_in_chunks(f, CHUNK_SIZE):

            offset = index + len(chunk)
            index = offset

            print("{} send file {} {}byte, send START".format(my_ip, zip_file_name, zip_file_size))
            res = requests.post('http://' + server_add + '/upload', files={zip_file_name: chunk},
                                data=params)
            # log("END {} FILE_SIZE : {}MB SEND".format(zip_file_name, zip_file_size))
            utils.log("{} send file {} {}byte, send END".format(my_ip, zip_file_name, zip_file_size))
            if res.ok:
                print("Upload completed successfully! : {}".format(zip_file_name))
                print(res.text)
            else:
                print("Something Wrong!")
        f.close()

        #compressed_rate = crr.getCompressedRate()
        #log("Compressed rate : {}, before  : {}, after : {}", compressed_rate, files_size, compressed_size)

        # 압축 파일 삭제
        if os.path.exists(zip_file_path):
            os.unlink(zip_file_path)
        else:
            print("Compressed File not existed")
        utils.log("DONE")
        return "UPLOAD COMPRESSED"
    except Exception as e:
        utils.log(str(e))
        # upload_run(current_i)
        print(str(e))
        return str(e)

@video_api.route('/upload_video_zip', methods=['GET', 'POST'])
def uploadOneCompressed():
    print("upload compressed")
    try:
        print(request)
        #crr.clearCompressedRate()
        #crr.clearRequest()

        limit_size = float(request.form.get('limit'))
        print("limit size : ", limit_size)

        # 제한 크기 file list 생성
        fileList, files_size = utils.getFiles(limit_size)

        for file in fileList:
            owd = os.getcwd()
            os.chdir(path)

            file_name, temp = utils.getFileName(file)
            #origin_file_size = os.path.getsize(path + file)
            zip_file_name = file_name + '.zip'
            zip_file_path = path + file_name + '.zip'

            #comp_file_size = os.path.getsize(zip_file_path)
            zip_start = time.time()
            #crr.addCompressedRate(origin_file_size, comp_file_size)

            zip_file = zipfile.ZipFile(file_name + '.zip', 'w')
            zip_file.write(file)
            zip_file.close()

            os.chdir(owd)

            utils.log("Compressed Time : %s" % (time.time() - zip_start))
            zip_file_size = os.path.getsize(zip_file_path)

            # start_time = log("START {}  FILE_SIZE : {}MB SEND".format(zip_file_name, zip_file_size))
            start_time = utils.log("{} send file {} {}byte, send START".format(my_ip, zip_file_name, zip_file_size))
            index = 0
            offset = 0

            params = {
                'time': start_time,
                'size': int(zip_file_size),
                'domId': my_ip
            }
            f = open(zip_file_path, 'rb')
            #crr.addRequest()
            for chunk in utils.read_in_chunks(f, CHUNK_SIZE):
                offset = index + len(chunk)
                index = offset

                res = requests.post('http://' + server_add + '/upload', files={zip_file_name: chunk}, data=params)
                # log("END {} FILE_SIZE : {}MB SEND".format(zip_file_name, zip_file_size))
                utils.log("{} send file {} {}MB, send START".format(my_ip, zip_file_name, zip_file_size))
                if res.ok:
                    print("Upload completed successfully! : {}".format(zip_file_name))
                    print(res.text)
                else:
                    print("Something Wrong!")
            f.close()

            # 압축 파일 삭제
            if os.path.exists(zip_file_path):
                os.unlink(zip_file_path)
            else:
                print("Compressed File not existed")
        #request_cnt = crr.getRequest()
        #log("Request_cnt : {}, file length : {}".format(request_cnt, len(fileList)))
        #compressed_rate = crr.getCompressedRate()
        #log("Compressed rate : {}, before  : {}, after : {}", compressed_rate, files_size, crr.getCompressedSize())
        utils.log("DONE")
        return "UPLOAD COMPRESSED"
    except Exception as e:
        utils.log(str(e))
        # upload_run(current_i)
        print(str(e))
        return str(e)


###################ffmpeg을 이용한 영상 압축 ######################################
@video_api.route('/video_ffmpeg_pi', methods=['GET', 'POST'])
#@app.route('/video1', methods=['GET', 'POST'])
def requestVideoCompress1():
    try:
        values = config.IP['clients']
        limit = float(request.form.get('limit'))

        divide_cnt = float(limit / len(values))

        start_time = time.time()

        threads = [threading.Thread(target=cr.requestAllVideoFFmpegToPI, args=(ip, divide_cnt,)) for ip in
                   values]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print("Elapsed Time : %s" % (time.time() - start_time))

        return 'video compress succeed'

    except Exception as e:
        return str(e)


@video_api.route('/video_ffmpeg_each', methods=['GET', 'POST'])
def videoCompress1Each():
    try:
        print("=====video1_each=======")
        limit = float(request.form.get('limit'))
        print("Video size: {}".format(limit))

        print("command starts")
        command = "python3.8 videoCompress.py {}".format(limit)
        print(command)

        print('Started executing command')
        command = shlex.split(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        print("Run successfully")
        output, err = process.communicate()

        return "Video Compress 1 Success"
    except Exception as e:
        return str(e)


def is_not_blank(s):
    return bool(s and not s.isspace())

## 유효한 동영상 파일인지 확인.
## 동영상 데이터 중 전송시 or 어떤 이유로 재생이 되지 않는 영상 존재할 수 있다.
## 그럴 경우 ffmpeg가 제대로 동작하지 않는다.
## error를 방지하기 위해 미리 유효한 동영상 파일인지 확인
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



def videoFfmpegToServer(divide_limit):
    try:
        print("server thread")
        file_list, files_size = utils.getFiles(divide_limit)
        for file in file_list:
            file_name, temp = utils.getFileName(file)
            file_name = file_name + '.' + temp
            print(file_name)

            file_size = os.path.getsize(path + file_name)

            print("server add : {}".format(server_add))
            start_time = utils.log("{} send file {} {}byte, send START".format(my_ip, file_name, file_size))
            index = 0
            offset = 0

            params = {
                'time': start_time,
                'size': int(file_size),
                'domId': my_ip,
                'is_application' : 'T',
                'is_gpu' : 'F'
            }
            print(params)

            f = open(path + file_name, 'rb')

            for chunk in utils.read_in_chunks(f, CHUNK_SIZE):
                offset = index + len(chunk)
                index = offset

                res = requests.post('http://' + server_add + '/upload', files={file_name: chunk},
                                    data=params)
                if res.ok:
                    print("Upload completed successfully! : {}".format(file_name))
                    utils.log(res.text)
                else:
                    print("Something Wrong!")
            f.close()
            # log("END {} FILE_SIZE : {}MB SEND".format(file_name, file_size))
        utils.log("{} send file {} {}byte, send END".format(my_ip, file_name, file_size))
        return "=========Video Classification2 server success"
    except Exception as e:
        return str(e)


def videoFfmpegToPi(pi_divide_cnt):
    try:
        print("pi thread")
        print("PI CNT : {}".format(pi_divide_cnt))

        params_pi = {
            'limit': float(pi_divide_cnt)
        }

        print(params_pi)

        print("{} python3.8 videoCompress.py {}".format(my_ip, pi_divide_cnt))
        res = requests.post('http://' + my_ip + ':60000/video_ffmpeg_each', data=params_pi)

        if res.ok:
            print("Upload completed successfully!")
            print(res.text)
        else:
            print("Something Wrong!")
        return "=========Video Classification2 pi success"
    except Exception as e:
        return str(e)


@video_api.route('/video_ffmpeg_PiWithServer_each', methods=['GET', 'POST'])
def videoClassification2():
    try:
        limit = float(request.form.get('limit'))

        # server and pi task thread로 생성s
        divide_limit = limit / 2.0
        divide_limit = float(divide_limit)
        print("divide_limit: {}GB".format(divide_limit))

        server_thread = threading.Thread(target=videoFfmpegToServer, args=(divide_limit,))
        pi_thread = threading.Thread(target=videoFfmpegToPi, args=(divide_limit,))

        server_thread.start()
        pi_thread.start()

        server_thread.join()
        pi_thread.join()

        return 'video2_each succeed'

    except Exception as e:
        return str(e)


@video_api.route('/video_ffmpeg_PiWithServer', methods=['GET', 'POST'])
def requestVideoCompress2():
    try:
        values = config.IP['clients']
        limit = float(request.form.get('limit'))

        divide_limit = float(limit / len(values))
        # pi_divide_cnt = divide_cnt / PI_QUANTITY
        #
        divide_limit = float(divide_limit)
        # pi_divide_cnt = int(pi_divide_cnt)

        start = time.time()

        threads = [threading.Thread(target=cr.requestAllVideoFFmpegPiWithServer, args=(ip, divide_limit)) for ip in
                   values]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print("Imagenet2 Elapsed Time : %s" % (time.time() - start))
        return 'imagenet2 succeed'
    except Exception as e:
        return str(e)

@video_api.route('/video_ffmpeg_Server_each', methods=['GET', 'POST'])
def videoClassification3():
    try:
        limit = float(request.form.get('limit'))
        videoFfmpegToServer(limit)
        return "=========Video Classification3 server success"
    except Exception as e:
        return str(e)


@video_api.route('/video_ffmpegToServer', methods=['GET', 'POST'])
def requestVideoClassification3():
    try:
        values = config.IP['clients']
        limit = float(request.form.get('limit'))

        divide_cnt = limit / len(values)
        # pi_divide_cnt = divide_cnt / PI_QUANTITY
        #
        divide_cnt = float(divide_cnt)
        # pi_divide_cnt = int(pi_divide_cnt)

        start = time.time()

        threads = [threading.Thread(target=cr.requestAllVideoFFmpegToServer, args=(ip, divide_cnt)) for ip in
                   values]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print("Imagenet3 Elapsed Time : %s" % (time.time() - start))
        return 'imagenet3 succeed'
    except Exception as e:
        return str(e)
