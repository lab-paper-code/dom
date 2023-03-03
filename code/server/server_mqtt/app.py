import paho.mqtt.client as mqtt
import argparse
import time
import json
import datetime
import os
import config

topic = ""
FILE_NAME = ""
MSG = ""
STATUS = "end"
UPLOAD_FOLDER = '/home/data/'
UPLOAD_LOG_FOLDER = UPLOAD_FOLDER + 'log/'
run_flag = True
current_payload = None
before_payload = None

def log_request(time, size, status):
    container = config.IP['client_ip']
    with open(UPLOAD_LOG_FOLDER + '_' + container + '_log.log', 'a+') as log:
        print('[' + str(time)+ '] ' + str(container) + ' received file ' + str(MSG['fileName']) + ' ' + str(size) + 'MB, receive ' + status)
        print('[' + str(time)+ '] ' + str(container) + ' received file ' + str(MSG['fileName']) + ' ' + str(size) + 'MB, receive ' + status ,file=log)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    global FILE_NAME
    global MSG
    global topic
    global run_flag
    global STATUS
    global before_payload
    global current_payload
    
    try:
        MSG_FIRST = json.loads(msg.payload)
        if MSG_FIRST['isText'] == "T":
            MSG = MSG_FIRST            
            timestamp = MSG['timestamp']
            value = MSG['value']
            print(MSG)
        elif MSG_FIRST['isFile'] == "F":
            MSG = MSG_FIRST
            domId = MSG['domId']
            size = MSG['size']
            stime = MSG['time']
            svalue = MSG['value']
            FILE_NAME = fileName
            print(FILE_NAME)
            log_request(datetime.datetime.now(), svalue, 'start')
            with open(UPLOAD_LOG_FOLDER + 'text.txt', 'ab') as log:
                print(stime, file = log)
            log_request(datetime.datetime.now(), svalue, 'end')


        elif MSG_FIRST['status'] == "start":        
            MSG = MSG_FIRST
            fileName = MSG['fileName']
            domId = MSG['domId']
            size = MSG['size']
            stime = MSG['time']
            STATUS = MSG['status']
            FILE_NAME = fileName
            print(FILE_NAME)
            log_request(stime, size / 1024 / 1024, 'start')
        elif MSG_FIRST['status'] == "end":
            
            print("end one file")
    except Exception as e:
        # get file 
        
        current_payload = msg.payload
        if before_payload == current_payload:
            print('before = current')
            return
        
        temp_name = 'tmp_' + MSG['domId'] + '_' + FILE_NAME
        with open(UPLOAD_FOLDER + temp_name, 'ab') as f:
            
            f.write(current_payload)
            before_payload = current_payload
            print('write finish')
            f.flush()
        nowdown_size = int(os.path.getsize(UPLOAD_FOLDER + temp_name))
        print('nowdown_size: ', nowdown_size)
        print('size: ', int(MSG['size']))
        if nowdown_size == int(MSG['size']):
            if os.path.exists(UPLOAD_FOLDER + FILE_NAME):
                FILE_NAME = MSG['domId'] + '_' + FILE_NAME
            os.replace(UPLOAD_FOLDER + temp_name, UPLOAD_FOLDER + FILE_NAME)
            down_filesize = os.path.getsize(UPLOAD_FOLDER + FILE_NAME)
            log_request(datetime.datetime.now(), down_filesize / 1024 / 1024,'end')
        f.close()
    print("success")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-i', '--ip', help='IP_address', required=True)
    parser.add_argument('-p', '--port', help='Port_number', required=True)
    args = vars(parser.parse_args())
    ip=args['ip']
    port=int(args['port'])
    
    # 새로운 클라이언트 생성
    client = mqtt.Client()
    # 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_subscribe(topic 구독),
    # on_message(발행된 메세지가 들어왔을 때)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    # address : localhost, port: 1883 에 연결
    client.connect(ip, port)
    # common topic 으로 메세지 발행
    
    topic = config.IP['client_ip']
    print(topic)
    client.subscribe(topic, 1)
    client.loop_forever()
    #client.loop_forever()
