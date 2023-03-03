import time
import paho.mqtt.client as mqtt
import socket
from flask import Blueprint, request
import json
import threading

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import client_request as cr
import config
import utils

mqtt_api = Blueprint('mqtt_api', __name__)

MY_IP = my_ip = socket.gethostbyname(socket.getfqdn())
MQTT_BROKER = "59.27.74.76"
MQTT_PORT = 50210
path = config.IP['video_path']
CHUNK_SIZE = 60 * 1024 * 1024
img_path = config.IP['img_path']

@mqtt_api.route('/mqtt/hello', methods=['GET', 'POST'])
def appImageHello():
    print("Combine Hello")
    return "Hello"

@mqtt_api.route('/upload_all_video_mqtt', methods=['GET', 'POST'])
def uploadAllMqtt():
    print("upload all video")
    try:
        if request.method == 'POST':
            values = config.IP['clients']
            limit_size = float(request.form.get('limit'))
            print("limit size : ", limit_size)

            limit_size = limit_size / int(len(values))

            start = time.time()

            threads = [threading.Thread(target=cr.requestToAllClientsMqtt, args=(ip, limit_size)) for ip in values]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            print("Elapsed Time : %s" % (time.time() - start))
            return 'uploaded'
    except Exception as e:
        print(str(e))
        return str(e)


def wait_for(client, msgType, period=0.25, wait_time=5100, running_loop=False):
    client.running_loop = running_loop  # if using external loop
    wcount = 0
    # return True
    while True:
        # print("waiting"+ msgType)
        if msgType == "PUBACK":
            if client.on_publish:
                if client.puback_flag:
                    return True

        if not client.running_loop:
            client.loop(.01)  # check for messages manually
        time.sleep(period)
        # print("loop flag ",client.running_loop)
        wcount += 1
        if wcount > wait_time:
            print("return from wait loop taken too long")
            return False
    return True


def on_publish(client, userdata, mid):
    print("pub ack " + str(mid))
    client.mid_value = mid
    client.puback_flag = True


def c_publish(client, topic, out_message, qos):
    print("TOPIC :" + topic)
    res, mid = client.publish(topic, out_message, qos)  # publish

    if res == 0:  # published ok
        if wait_for(client, "PUBACK", running_loop=True):
            if mid == client.mid_value:
                print("match mid ", str(mid))
                client.puback_flag = False  # reset flag
            else:
                print("quitting")
                raise SystemExit("not got correct puback mid so quitting")

        else:
            raise SystemExit("not got puback so quitting")


def connect_mqtt():
    client_str = "dom_pub" + str(my_ip)
    print("client STR : " + client_str)
    mqttc = mqtt.Client(client_str)
    mqttc.on_publish = on_publish
    mqttc.puback_flag = False
    mqttc.connect(MQTT_BROKER, MQTT_PORT)
    return mqttc

def simple_on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Completely connected to mqtt")
    else:
        print("Bad Connection Return code = ", rc)


def simple_on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))



def simple_on_publish(client, userdata, mid):
    print("In on_pub callbacak mid =", mid)


@mqtt_api.route('/upload_video_mqtt', methods=['GET', 'POST'])
def uploadOneMqtt():
    print("upload video mqtt")

    try:
        print(request)
        files = os.listdir(path)

        limit_size = float(request.form.get('limit'))
        print("limit size : ", limit_size)
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
        print("SEND FILE LIST LENGHT : {}".format(len(fileList)))
        index = 0
        offset = 0

        mqttc = connect_mqtt()

        for file in fileList:
            filesize = os.path.getsize(path + file)
            filesize_mb = filesize / (1024.0 * 1024.0)

            log_time = utils.log("{} send file {} {}MB, send START".format(my_ip, file, filesize_mb))
            mqttc.loop_start()
            f = open(path + file, 'rb')
            # mqttc.publish("file" + str(cnt),json.dumps({'fileName': file, 'time': str(log_time), 'size': filesize, 'domId': my_ip, 'status': 'header'}), qos=1)
            start_json = json.dumps(
                {'isFile': 'F','fileName': file, 'time': str(log_time), 'size': filesize, 'domId': my_ip, 'status': 'start'})
            print(start_json)
            c_publish(mqttc, my_ip, start_json, 1)

            for chunk in utils.read_in_chunks(f, CHUNK_SIZE):
                offset = index + len(chunk)
                index = offset

                c_publish(mqttc, my_ip, bytes(chunk), 1)
            end_json = json.dumps(
                {'isFile': 'F','fileName': file, 'time': str(log_time), 'size': filesize, 'domId': my_ip, 'status': 'end'})
            print(end_json)
            c_publish(mqttc, my_ip, end_json, 1)

            f.close()
            # time.sleep(10)
            mqttc.loop_stop()
            print(file + " MQTT DONE")
            utils.log("{} send file {} {}MB, send END".format(my_ip, file, filesize_mb))
        # mqttc.loop_stop()

        utils.log("DONE")

        return "UPLOAD"
    except Exception as e:
        utils.log(str(e))
        print(str(e))
        return str(e)

@mqtt_api.route('/upload_all_image_mqtt', methods=['GET', 'POST'])
def uploadAllImageMqtt():
    print("upload all image mqtt")
    try:
        if request.method == 'POST':
            img_cnt = float(request.form.get('img_cnt'))
            print("img_cnt : ", img_cnt)

            values = config.IP['clients']
            start = time.time()

            divide_img_cnt = int(img_cnt / len(values))

            threads = [threading.Thread(target=cr.requestToAllClientsImageMqtt, args=(ip, divide_img_cnt)) for ip in values]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            print("Elapsed Time : %s" % (time.time() - start))
            return 'uploaded'
    except Exception as e:
        print(str(e))
        return str(e)


@mqtt_api.route('/upload_image_mqtt', methods=['GET', 'POST'])
def uploadImageMqtt():
    print("upload image mqtt")

    try:
        print(request)

        img_cnt = int(request.form.get('img_cnt'))
        print("img_cnt : ", img_cnt)

        fileList, files_size = utils.getFilesByCnt(img_cnt)

        index = 0
        offset = 0

        mqttc = connect_mqtt()

        for file in fileList:
            filesize = os.path.getsize(img_path + file)
            filesize_mb = filesize / (1024.0 * 1024.0)

            log_time = utils.log("{} send file {} {}MB, send START".format(my_ip, file, filesize_mb))
            mqttc.loop_start()
            f = open(img_path + file, 'rb')
            # mqttc.publish("file" + str(cnt),json.dumps({'fileName': file, 'time': str(log_time), 'size': filesize, 'domId': my_ip, 'status': 'header'}), qos=1)
            start_json = json.dumps(
                {'isFile': 'T', 'isText': 'F', 'fileName': file, 'time': str(log_time), 'size': filesize, 'domId': my_ip, 'status': 'start'})
            print(start_json)
            c_publish(mqttc, my_ip, start_json, 1)
            cnt = 0

            for chunk in utils.read_in_chunks(f, CHUNK_SIZE):
                cnt = cnt + 1
                offset = index + len(chunk)
                index = offset
                print("IMAGE REQUEST CNT : {}".format(cnt))

                c_publish(mqttc, my_ip, bytes(chunk), 1)
            end_json = json.dumps(
                {'isFile': 'T','isText': 'F', 'fileName': file, 'time': str(log_time), 'size': filesize, 'domId': my_ip, 'status': 'end'})
            print(end_json)
            c_publish(mqttc, my_ip, end_json, 1)

            f.close()
            # time.sleep(10)
            mqttc.loop_stop()
            print(file + " MQTT DONE")
            utils.log("{} send file {} {}MB, send END".format(my_ip, file, filesize_mb))
        # mqttc.loop_stop()

        utils.log("DONE")

        return "UPLOAD"
    except Exception as e:
        utils.log(str(e))
        print(str(e))
        return str(e)


@mqtt_api.route('/upload_txt_mqtt', methods=['GET', 'POST'])
def uploadTxtMqtt():
    print("upload text mqtt")

    try:
        print(request)

        limit_size = float(request.form.get('limit'))
        print("limit size : ", limit_size)

        limit = limit_size * 1024.0
        tot_size = 0

        txt_id = 0

        #mqttc = connect_mqtt()
        client = mqtt.Client()
        client.on_connect=simple_on_connect
        client.on_disconnect = simple_on_disconnect
        client.on_publish = simple_on_publish
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()

        while tot_size < limit:
            #mqttc.loop_start()

            now_str = utils.make_text(txt_id)
            cur_text_size = sys.getsizeof(now_str)
            tot_size += cur_text_size
            client.publish(my_ip, now_str, 1)

            print(now_str)
            #c_publish(mqttc, my_ip, now_str, 1)
            #mqttc.loop_stop()

            utils.log("{} text {}byte , now : {}KB, limit : {}KB, send END".format(my_ip, cur_text_size, tot_size, limit))

            txt_id += 1
        client.loop_stop()
        client.disconnect()
        utils.log("total send size : {} KB".format(tot_size / (1024.0)))
        print("Upload completed successfully!")
        utils.log("DONE")
        return "UPLOAD"
    except Exception as e:
        utils.log(str(e))
        print(str(e))
        return str(e)



@mqtt_api.route('/upload_all_txt_mqtt', methods=['GET', 'POST'])
def upload_all_txt_mqtt():
    print("upload all txt")
    try:
        if request.method == 'POST':
            limit_size = float(request.form.get('limit'))
            print("limit size : ", limit_size)

            values = config.IP['clients']
            start = time.time()
            divide_limit_cnt = float(limit_size / len(values))

            threads = [threading.Thread(target=cr.requestToAllTxtClientsMqtt, args=(ip, divide_limit_cnt)) for ip in values]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            print("Elapsed Time : %s" % (time.time() - start))
            return 'uploaded'
    except Exception as e:
        print(str(e))
        return str(e)






