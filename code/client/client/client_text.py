
from flask import request, Blueprint
import time
import threading
import socket
import requests

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import client_request as cr
import config
import utils

text_api = Blueprint('text_api', __name__)

my_ip = socket.gethostbyname(socket.getfqdn())
server_add = config.IP['server']

@text_api.route('/text/hello', methods=['GET', 'POST'])
def appImageHello():
    print("Text Hello")
    return "Hello"


@text_api.route('/upload_all_text', methods=['GET', 'POST'])
def textUploadToAll():
    try:
        limit = float(request.form.get('limit'))
        print("limit : ", limit)

        values = config.IP['clients']

        divide_limit_cnt = float(limit / len(values))

        start = time.time()
        threads = [threading.Thread(target=cr.requestToAllClients_text, args=(ip, divide_limit_cnt)) for ip in values]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        str = "Elapsed Time : " + (time.time() - start)
        print(str)
        return 'TEXT UPLOADED COMPLETE : ' + str
    except Exception as e:
        utils.log(str(e))
        return (str(e))



@text_api.route('/upload_text', methods=['GET', 'POST'])
def textUpload():
    try:
        limit = float(request.form.get('limit'))
        print(limit)
        limit = limit * 1024.0
        tot_size = 0

        txt_id = 0
        while tot_size < limit:
            now_str = utils.make_text(txt_id)
            print(now_str)

            cur_text_size = sys.getsizeof(now_str)
            tot_size += cur_text_size

            start_time = utils.log("{} send text {}byte, send START".format(my_ip, cur_text_size))

            params = {
                'time': start_time,
                'size': int(cur_text_size),
                'domId': my_ip
            }

            res = requests.post('http://' + server_add + '/upload', data=params)
            utils.log("{} text {}byte, send END".format(my_ip, cur_text_size))

            if res.ok:
                print(res.text)
            else:
                print("Something Wrong!")

            txt_id += 1
        utils.log("total send size : {} KB".format(tot_size / (1024.0)))
        print("Upload completed successfully!")
        return "Upload Text Complete"

    except Exception as e:
        utils.log(str(e))
        return str(e)