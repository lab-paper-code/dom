import requests


# TODO: 함수 하나로 합칠 것
def requestToAllClients(ip, limit, url):
    print("Uploading {}".format(ip))
    params = {
        'limit': float(limit)
    }
    res = requests.post('http://' + ip + ':60000/' + url, data=params)


def requestToAllClientsMqtt(ip, limit):
    print("Uploading {}".format(ip))
    params = {
        'limit': limit
    }
    res = requests.post('http://' + ip + ':60000/upload_video_mqtt', data=params)

def requestToAllClientsImageMqtt(ip, img_cnt):
    print("Uploading {} img quantity : {}".format(ip, img_cnt))
    params = {
        'img_cnt': int(img_cnt)
    }
    res = requests.post('http://' + ip + ':60000/upload_image_mqtt', data=params)



def requestToAllClientsImage(ip, img_cnt, is_predict, url):
    print("Uploading {} img_cnt : {}".format(ip, img_cnt))
    params = {
        'img_cnt': img_cnt,
        'is_predict': is_predict
    }
    res = requests.post('http://' + ip + ':60000/' + url, data=params)


def requestToAllClientsImageAllZip(ip, img_cnt):
    print("Uploading {}, img_cnt : {}".format(ip, img_cnt))
    params = {
        'img_cnt': img_cnt
    }
    res = requests.post('http://' + ip + ':60000/upload_img_zip_all', data=params)

def requestToAllClientsImageZipBatch(ip, img_cnt, batch):
    print("Uploading {}, img_cnt : {}, batch cnt : {}".format(ip, img_cnt, batch))
    params = {
        'img_cnt' : img_cnt,
        'batch' : batch
    }

    res = requests.post('http://' + ip + ':60000/upload_img_zip_batch', data=params)

def requestToAllClientsVideoAllZip(ip, limit):
    print("Uploading {}, limit : {}".format(ip, limit))
    params = {
        'limit': int(limit)
    }
    res = requests.post('http://' + ip + ':60000/upload_video_zip_all', data=params)




def requestToAllClientsSocket(ip, limit, protocol, isZip):
    print("Uploading {}".format(ip))
    print("limit : {}, protocol : {}, isZip : {}".format(limit, protocol, isZip))
    params = {
        'limit': limit,
        'protocol': protocol,
        'isZip': isZip
    }
    res = requests.post('http://' + ip + ':60000/upload_socket', data=params)


def requestToAllClientsText(ip, limit):
    print("Uploading {}".format(ip))
    params = {
        'limit': limit
    }
    res = requests.post('http://' + ip + ':60000/upload_text', data=params)

def requestImageClassification1AllClients(ip, divide_cnt):
    try:
        print("Uploading {}".format(ip))
        parmas = {
            'img_cnt': divide_cnt
        }
        res = requests.post('http://' + ip + ':60000/image/app/device/each', data=parmas)
    except Exception as e:
        print(str(e))


def requestAllImageClassification2(ip, divide_cnt):
    try:
        print("Uploading {} img_cnt : {}".format(ip, divide_cnt))
        parmas = {
            'img_cnt': divide_cnt
        }
        res = requests.post('http://' + ip + ':60000/image/app/offloading/half/each', data=parmas)
    except Exception as e:
        print(str(e))


def requestAllImageClassification3(ip, divide_cnt):
    try:
        print("Uploading {} img_cnt : {}".format(ip, divide_cnt))
        parmas = {
            'img_cnt': divide_cnt
        }
        res = requests.post('http://' + ip + ':60000/image/app/offloading/full/each', data=parmas)
    except Exception as e:
        print(str(e))


def requestToAllTxtClientsMqtt(ip, limit):
    print("Uploading {}".format(ip))
    params = {
        'limit': float(limit)
    }
    res = requests.post('http://' + ip + ':60000/upload_txt_mqtt', data=params)


def requestAllVideoFFmpegToPI(ip, limit):
    try:
        print("request Video Compress1 {}".format(ip))
        parmas = {
            'limit': limit
        }
        res = requests.post('http://' + ip + ':60000/video_ffmpeg_each', data=parmas)
    except Exception as e:
        print(str(e))


def requestAllVideoFFmpegPiWithServer(ip, divide_limit):
    try:
        print("Uploading {} limit : {}GB".format(ip, divide_limit))
        parmas = {
            'limit': divide_limit
        }
        res = requests.post('http://' + ip + ':60000/video_ffmpeg_PiWithServer_each', data=parmas)
    except Exception as e:
        print(str(e))

def requestAllVideoFFmpegToServer(ip, divide_cnt):
    try:
        print("Uploading {} limit : {}GB".format(ip, divide_cnt))
        parmas = {
            'limit': divide_cnt
        }
        res = requests.post('http://' + ip + ':60000/video_ffmpeg_Server_each', data=parmas)
    except Exception as e:
        print(str(e))

