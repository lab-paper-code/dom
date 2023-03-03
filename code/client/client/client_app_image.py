import time
from flask import request
import threading
import socket
import requests
from flask import Blueprint

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import client_request as cr
import config
import utils
import image_classification as imgApp

from silence_tensorflow import silence_tensorflow
silence_tensorflow()


appImage_api = Blueprint('appImage_api', __name__)

img_path = config.IP['img_path']
server_add = config.IP['server']
my_ip = socket.gethostbyname(socket.getfqdn())
CHUNK_SIZE = 60 * 1024 * 1024

@appImage_api.route('/image/app/hello', methods=['GET', 'POST'])
def appImageHello():
    print("App Image Hello")
    return "Hello"

@appImage_api.route('/image/app/device', methods=['GET', 'POST'])
def requestImageClassificationDeviceOnly():
    try:
        values = config.IP['clients']
        img_cnt = int(request.form.get('img_cnt'))

        divide_cnt = img_cnt / len(values)
        divide_cnt = int(divide_cnt)

        start = time.time()

        threads = [threading.Thread(target=cr.requestImageClassification1AllClients, args=(ip, divide_cnt)) for ip in
                   values]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print("Elapsed Time : %s" % (time.time() - start))
        return 'imagenet device only succeed'
    except Exception as e:
        return str(e)


# /imagenet1_each
@appImage_api.route('/image/app/device/each', methods=['GET', 'POST'])
def imageClassificationDeviceOnlyEach():
    try:
        print("=====imagenet1_each=======")
        # os.chdir(IMAGENET_LOC)
        img_cnt = int(request.form.get('img_cnt'))
        print("Image Cnt : {}".format(img_cnt))

        imgApp.image_classification(img_cnt)
        # print("command starts")
        # command = "python3.8 image_classification.py {}".format(img_cnt)
        # print(command)
        #
        # print('Started executing command')
        # command = shlex.split(command)
        # process = subprocess.Popen(command, stdout=subprocess.PIPE)
        # print("Run successfully")
        # output, err = process.communicate()
        return "success"
    except Exception as e:
        return str(e)


def imageClassificationHalfOffloading(divide_cnt):
    try:
        print("server thread")
        file_list, files_size = utils.getFilesByCnt(divide_cnt)
        for file in file_list:
            file_name, temp = utils.getFileName(file)
            file_name = file_name + '.' + temp
            print(file_name)
            file_size = os.path.getsize(img_path + file_name)

            print("server add : {}".format(server_add))
            start_time = utils.log("{} send file {} {}byte, send START".format(my_ip, file_name, file_size))
            index = 0
            offset = 0

            params = {
                'time': start_time,
                'size': int(file_size),
                'domId': my_ip,
                'is_predict': "T"
            }

            f = open(img_path + file_name, 'rb')

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
        return "=========ImageNet Classification2 server success"
    except Exception as e:
        return str(e)


def imageClassificationHalfDevice(pi_divide_cnt):
    try:
        print("pi thread")
        print("PI CNT : {}".format(pi_divide_cnt))

        imgApp.image_classification(pi_divide_cnt)
        #print("{} python3.8 image_classification.py {}".format(my_ip, pi_divide_cnt))
        #res = requests.post('http://' + my_ip + ':60000/image/app/device/each', data=params_pi)

        # if res.ok:
        #     print("Upload completed successfully!")
        #     print(res.text)
        # else:
        #     print("Something Wrong!")
        return "imageClassificationHalfDevice pi success"
    except Exception as e:
        return str(e)

# imagenet2_each
@appImage_api.route('/image/app/offloading/half/each', methods=['GET', 'POST'])
def imageClassificationOffloadingHalfEach():
    try:
        img_cnt = int(request.form.get('img_cnt'))

        # server and pi task thread로 생성s
        divide_cnt = img_cnt / 2
        divide_cnt = int(divide_cnt)
        print("divide_cnt: {}".format(divide_cnt))

        server_thread = threading.Thread(target=imageClassificationHalfOffloading, args=(divide_cnt,))
        pi_thread = threading.Thread(target=imageClassificationHalfDevice, args=(divide_cnt,))

        server_thread.start()
        pi_thread.start()

        server_thread.join()
        pi_thread.join()

        # log("imagenet2_each Elapsed Time : {}".format(end_time))
        return 'image/app/offloading/half/each succeed'

    except Exception as e:
        return str(e)


@appImage_api.route('/image/app/offloading/half', methods=['GET', 'POST'])
def requestImageClassificationHalfOffloading():
    try:
        values = config.IP['clients']
        img_cnt = int(request.form.get('img_cnt'))

        divide_cnt = img_cnt / len(values)
        # pi_divide_cnt = divide_cnt / PI_QUANTITY
        #
        divide_cnt = int(divide_cnt)
        # pi_divide_cnt = int(pi_divide_cnt)

        start = time.time()

        threads = [threading.Thread(target=cr.requestAllImageClassification2, args=(ip, divide_cnt)) for ip in
                   values]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print("Imagenet2 Elapsed Time : %s" % (time.time() - start))
        return '/image/app/offloading/half succeed'
    except Exception as e:
        return str(e)

# imagenet3_each
@appImage_api.route('/image/app/offloading/full/each', methods=['GET', 'POST'])
def imageClassificationOffloadingFull():
    try:
        img_cnt = int(request.form.get('img_cnt'))
        file_list, files_size = utils.getFilesByCnt(img_cnt)
        for file in file_list:
            file_name, temp = utils.getFileName(file)
            file_name = file_name + '.' + temp
            print(file_name)
            file_size = os.path.getsize(img_path + file_name)

            print("server add : {}".format(server_add))
            start_time = utils.log("{} send file {} {}byte, send START".format(my_ip, file_name, file_size))
            index = 0
            offset = 0

            params = {
                'time': start_time,
                'size': int(file_size),
                'domId': my_ip,
                'is_predict': "T"
            }

            f = open(img_path + file_name, 'rb')

            for chunk in utils.read_in_chunks(f, CHUNK_SIZE):
                offset = index + len(chunk)
                index = offset

                res = requests.post('http://' + server_add + '/upload', files={file_name: chunk}, data=params)
                if res.ok:
                    print("Upload completed successfully! : {}".format(file_name))
                    utils.log(res.text)
                else:
                    print("Something Wrong!")
            f.close()
            # log("END {} FILE_SIZE : {}MB SEND".format(file_name, file_size))
        utils.log("{} send file {} {}byte, send END".format(my_ip, file_name, file_size))
        return "=========ImageNet Classification2 server success"
    except Exception as e:
        return str(e)


@appImage_api.route('/image/app/offloading/full', methods=['GET', 'POST'])
def requestImageClassificationOffloadingFull():
    try:
        values = config.IP['clients']
        img_cnt = int(request.form.get('img_cnt'))
        print("1")

        divide_cnt = img_cnt / len(values)
        # pi_divide_cnt = divide_cnt / PI_QUANTITY
        #
        divide_cnt = int(divide_cnt)
        # pi_divide_cnt = int(pi_divide_cnt)

        start = time.time()

        threads = [threading.Thread(target=cr.requestAllImageClassification3, args=(ip, divide_cnt)) for ip in
                   values]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print("Imagenet3 Elapsed Time : %s" % (time.time() - start))
        return 'imagenet3 succeed'
    except Exception as e:
        return str(e)
