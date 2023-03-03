
import requests
from flask import request
import time
import threading
import os
import socket
from flask import Blueprint

import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import client_request as cr
import config
import utils

combinedData_api = Blueprint('combinedData_api', __name__)


img_path = config.IP['img_path']
server_add = config.IP['server']
CHUNK_SIZE = 60 * 1024 * 1024
my_ip = socket.gethostbyname(socket.getfqdn())


@combinedData_api.route('/upload_hetero/hello', methods=['GET', 'POST'])
def appImageHello():
    print("Combine Hello")
    return "Hello"

@combinedData_api.route('/upload_hetero', methods=['GET', 'POST'])
def uploadHeterogenous():
    try:
        img_cnt = int(request.form.get('img_cnt'))
        limit = float(request.form.get('limit'))
        values = config.IP['clients']
        start_time = time.time()
        # 데이터 100% 비디오
        if img_cnt == 0:
            params = {
                'limit': float(limit),
                'is_zip': 'F'
            }
            res = requests.post('http://'+ my_ip + ':60000/upload_all_video', data=params)
            print("Elapsed Time : %s" % (time.time() - start_time))
        # 데이터 100% 이미지
        elif limit == 0:
            params = {
                'img_cnt' : int(img_cnt),
                'is_predict': 'F',
                'is_zip' : 'F'
            }
            res = requests.post('http://' + my_ip + ':60000/upload_all_img', data=params)
            print("Elapsed Time : %s" % (time.time() - start_time))
        # 데이터 50%:50%
        else:
            # TODO: hard coding -> parameter로 받게끔 변경 
            videos = values[0:10]
            images = values[10:]
            limit_size = limit / len(videos)
            url = "upload_video"
            threads_video = [threading.Thread(target=cr.requestToAllClients, args=(ip, limit_size, url)) for ip in videos]

            divide_img_cnt = int(img_cnt / len(images))
            is_predict='F'
            url="upload_image"
            threads_image = [threading.Thread(target= cr.requestToAllClientsImage, args=(ip, divide_img_cnt, is_predict, url)) for ip in
                       images]

            threads = threads_video + threads_image
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            print("Elapsed Time : %s" % (time.time() - start_time))
            return "upload"


    except Exception as e:
        utils.log(str(e))
        return str(e)