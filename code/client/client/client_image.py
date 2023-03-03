from flask import request, Blueprint
import time
import threading
import os
import socket
import requests
import zipfile
import sys


sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import client_request as cr
import config
import utils


image_api = Blueprint('image_api', __name__)

img_path = config.IP['img_path']
server_add = config.IP['server']
CHUNK_SIZE = 60 * 1024 * 1024
my_ip = socket.gethostbyname(socket.getfqdn())


@image_api.route('/image/hello', methods=['GET', 'POST'])
def appImageHello():
    print("Image Hello")
    return "Hello"


@image_api.route('/upload_all_img', methods=['GET', 'POST'])
def uploadAllImg():
    print("upload all image")
    try:
        if request.method == 'POST':
            img_cnt = int(request.form.get('img_cnt'))
            print("limit count : ", img_cnt)

            is_predict = request.form.get('is_predict')
            print("is predict: ", is_predict)

            is_compression = request.form.get('is_zip')
            print("is zipfile :", is_compression)

            values = config.IP['clients']
            start = time.time()

            divide_img_cnt = int(img_cnt / len(values))
            print("Image Quantity for Each Device : ", divide_img_cnt)

            url = "upload_image_zip" if is_compression == "T" else "upload_image"

            threads = [threading.Thread(target=cr.requestToAllClientsImage, args=(ip, divide_img_cnt, is_predict, url)) for ip in
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


@image_api.route('/upload_all_img_zip', methods=['GET', 'POST'])
def uploadAllImgAllZip():
    print("upload all image")
    try:
        if request.method == 'POST':
            img_cnt = int(request.form.get('img_cnt'))
            print("limit count : ", img_cnt)

            values = config.IP['clients']
            start = time.time()
            divide_cnt = int(img_cnt / len(values))

            threads = [threading.Thread(target=cr.requestToAllClients_image_all_zip, args=(ip, divide_cnt)) for ip in
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


@image_api.route('/upload_image', methods=['GET', 'POST'])
def uploadImage():
    print("upload Image")
    try:
        print(request)

        img_cnt = int(request.form.get('img_cnt'))
        print(img_cnt)
        is_predict = request.form.get('is_predict')
        print(is_predict)

        is_predict = "T" if is_predict == "T" else "F"

        fileList, files_size = utils.getFilesByCnt(img_cnt)

        start_time = time.time()
        for file in fileList:

            file_name, temp = utils.getFileName(file)
            file_name = file_name + '.' + temp
            print(file_name)
            file_size = os.path.getsize(img_path + file_name)

            # start_time = log("START {}  FILE_SIZE : {}MB SEND".format(file_name, file_size))
            start_time = utils.log("{} send file {} {}byte, send START".format(my_ip, file_name, file_size))
            index = 0
            offset = 0

            params = {
                'time': start_time,
                'size': int(file_size),
                'domId': my_ip,
                'is_predict': is_predict
            }

            f = open(img_path + file_name, 'rb')

            for chunk in utils.read_in_chunks(f, CHUNK_SIZE):
                offset = index + len(chunk)
                index = offset

                res = requests.post('http://' + server_add + '/upload', files={file_name: chunk},
                                    data=params)
                if res.ok:
                    print("Upload completed successfully! : {}".format(file_name))
                    print(res.text)
                else:
                    print("Something Wrong!")
            f.close()
            # log("END {} FILE_SIZE : {}MB SEND".format(file_name, file_size))
            utils.log("{} send file {} {}byte, send END".format(my_ip, file_name, file_size))

        return "UPLOAD IMAGE"
    except Exception as e:
        utils.log(str(e))
        # upload_run(current_i)
        print(str(e))
        return str(e)


@image_api.route('/upload_image_zip', methods=['GET', 'POST'])
def uploadImageCompressed():
    print("upload compressed")
    try:
        print(request)

        #crr.clearRequest()
        #crr.clearCompressedRate()

        img_cnt = int(request.form.get('img_cnt'))
        print(img_cnt)

        # 제한 크기 file list 생성
        fileList, files_size = utils.getFilesByCnt(img_cnt)

        for file in fileList:
            owd = os.getcwd()
            os.chdir(img_path)

            file_name = utils.getFileName(file)
            zip_file_path = img_path + file_name[0] + '.zip'
            zip_file_name = file_name[0] + '.zip'
            zip_start = time.time()


            zip_file = zipfile.ZipFile(zip_file_name, 'w')
            zip_file.write(file)
            zip_file.close()

            origin_file_size = os.path.getsize(img_path + file)
            comp_file_size = os.path.getsize(zip_file_name)
            #crr.addCompressedRate(origin_file_size, comp_file_size)

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

                res = requests.post('http://' + server_add + '/upload', files={zip_file_name: chunk},
                                    data=params)
                # log("END {} FILE_SIZE : {}MB SEND".format(zip_file_name, zip_file_size))
                utils.log("{} send file {} {}MB, send END".format(my_ip, zip_file_name, zip_file_size))
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
        #log("Compressed rate : {}, before  : {}, after : {}".format(compressed_rate, crr.origin_file_size, crr.getCompressedSize()))
        #log("Files size : {}".format(files_size))
        utils.log("DONE")
        return "UPLOAD COMPRESSED"
    except Exception as e:
        utils.log(str(e))
        # upload_run(current_i)
        print(str(e))
        return str(e)


@image_api.route('/upload_img_zip_all', methods=['GET', 'POST'])
def uploadImageCompressedAll():
    print("upload compressed all")
    try:
        print(request)

        #crr.clearRequest()
        #crr.clearCompressedRate()

        img_cnt = int(request.form.get('img_cnt'))
        print(img_cnt)

        # 제한 크기 file list 생성
        fileList, files_size = utils.getFilesByCnt(img_cnt)

        owd = os.getcwd()
        os.chdir(img_path)

        zip_start = time.time()

        zip_file_name = 'compressed.zip'
        zip_file = zipfile.ZipFile('compressed.zip', 'w')

        for file in fileList:
            zip_file.write(file)
        zip_file.close()
        comp_file_size = os.path.getsize(zip_file_name)
        utils.log("Compressed Time : %s" % (time.time() - zip_start))
        #crr.addCompressedRate(files_size, comp_file_size)

        os.chdir(owd)

        zip_file_path = img_path + 'compressed.zip'
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





